import { parseTemplate } from '@angular/compiler';
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const appRoot = path.join(root, 'src', 'app');
const dictionaryPath = path.join(root, 'public', 'i18n', 'es.json');
const pipePath = path.join(appRoot, 'shared', 'pipes', 'ui-text.pipe');
const translatedAttributes = new Set([
  'placeholder',
  'searchPlaceholder',
  'emptyText',
  'title',
  'subtitle',
  'aria-label',
  'itemLabel',
  'itemLabelPlural',
  'current',
  'submitText',
  'cancelText',
  'confirmText',
  'busyText'
]);

const dictionary = JSON.parse(fs.readFileSync(dictionaryPath, 'utf8'));
const textToKey = new Map();

function indexDictionary(value, parts = []) {
  for (const [key, child] of Object.entries(value)) {
    if (typeof child === 'string') textToKey.set(child, [...parts, key].join('.'));
    else indexDictionary(child, [...parts, key]);
  }
}

indexDictionary(dictionary);

function walkFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const fullPath = path.join(directory, entry.name);
    return entry.isDirectory() ? walkFiles(fullPath) : [fullPath];
  });
}

function slug(text) {
  const normalized = text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 48);
  return normalized || 'texto';
}

function setDictionaryValue(parts, value) {
  let current = dictionary;
  for (const part of parts.slice(0, -1)) {
    if (!current[part] || typeof current[part] === 'string') current[part] = {};
    current = current[part];
  }
  current[parts.at(-1)] = value;
}

function keyFor(text, htmlPath) {
  const existing = textToKey.get(text);
  if (existing) return existing;

  const relative = path.relative(appRoot, htmlPath).replace(/\\/g, '/');
  const namespace = relative
    .replace(/\.component\.html$/, '')
    .replace(/\.html$/, '')
    .split('/')
    .map(slug);
  const base = slug(text);
  let candidateParts = ['views', ...namespace, base];
  let candidate = candidateParts.join('.');
  let suffix = 2;

  while (candidate.split('.').reduce((current, part) => current?.[part], dictionary) !== undefined) {
    candidateParts = ['views', ...namespace, `${base}_${suffix++}`];
    candidate = candidateParts.join('.');
  }

  setDictionaryValue(candidateParts, text);
  textToKey.set(text, candidate);
  return candidate;
}

function shouldTranslateText(text, ancestors) {
  const trimmed = text.trim();
  if (!trimmed || !/[A-Za-zÁÉÍÓÚÜÑáéíóúüñ¿¡]/.test(trimmed)) return false;
  if (trimmed.includes('&#') || trimmed.includes('| uiText')) return false;
  return !ancestors.some(element =>
    ['script', 'style'].includes(element.name) ||
    element.attributes?.some(attribute =>
      (attribute.name === 'translate' && attribute.value === 'no') ||
      (attribute.name === 'class' && attribute.value.split(/\s+/).includes('mat-icon'))
    )
  );
}

function attributeBinding(name, key) {
  if (name === 'aria-label') return `[attr.aria-label]="'${key}' | uiText"`;
  return `[${name}]="'${key}' | uiText"`;
}

function isVisibleExpressionText(value) {
  if (typeof value !== 'string' || !/[A-Za-zÁÉÍÓÚÜÑáéíóúüñ¿¡]/.test(value)) return false;
  if (/^[A-Za-z0-9_.-]+$/.test(value) || /^(\/|#|https?:|mailto:|tel:)/.test(value)) return false;
  if (/^[dmyhms:/ -]+$/i.test(value)) return false;
  return true;
}

function dictionaryValue(key) {
  return key.split('.').reduce((current, part) => current?.[part], dictionary);
}

function normalizePreviousPass(source) {
  let normalized = source
    .replace(/\('([^']+)' \| uiText\)[A-Za-z0-9_.]+' \| uiText\)/g, "('$1' | uiText)")
    .replace(/(\('[^']+' \| uiText\))'/g, '$1');

  normalized = normalized.replace(
    /\(('([^']+)' \| uiText)\) \| uiText/g,
    (match, _expression, key) => {
      const targetKey = dictionaryValue(key);
      return typeof targetKey === 'string' && /^[A-Za-z0-9_.-]+$/.test(targetKey)
        ? `'${targetKey}' | uiText`
        : match;
    }
  );

  return normalized;
}

function collectAstLiterals(ast, htmlPath, replacements, seen = new WeakSet()) {
  if (!ast || typeof ast !== 'object' || seen.has(ast)) return;
  seen.add(ast);

  if (
    ast.constructor?.name === 'LiteralPrimitive' &&
    isVisibleExpressionText(ast.value) &&
    ast.sourceSpan?.start !== undefined
  ) {
    const key = keyFor(ast.value, htmlPath);
    replacements.push({
      start: ast.sourceSpan.start,
      end: ast.sourceSpan.end,
      value: `('${key}' | uiText)`
    });
    return;
  }

  for (const [property, child] of Object.entries(ast)) {
    if (['span', 'sourceSpan', 'nameSpan', 'location', 'errors', 'source'].includes(property)) continue;
    if (Array.isArray(child)) {
      child.forEach(item => collectAstLiterals(item, htmlPath, replacements, seen));
    } else {
      collectAstLiterals(child, htmlPath, replacements, seen);
    }
  }
}

function collectReplacements(nodes, source, htmlPath, ancestors = [], replacements = []) {
  for (const node of nodes) {
    if (node.constructor.name === 'BoundText') {
      collectAstLiterals(node.value?.ast, htmlPath, replacements);
    }

    for (const input of node.inputs || []) {
      collectAstLiterals(input.value?.ast, htmlPath, replacements);
    }

    if (node.constructor.name === 'Text' && shouldTranslateText(node.value, ancestors)) {
      const leading = node.value.match(/^\s*/)?.[0] || '';
      const trailing = node.value.match(/\s*$/)?.[0] || '';
      const text = node.value.trim();
      const key = keyFor(text, htmlPath);
      replacements.push({
        start: node.sourceSpan.start.offset,
        end: node.sourceSpan.end.offset,
        value: `${leading}{{ '${key}' | uiText }}${trailing}`
      });
    }

    if (node.constructor.name === 'Element') {
      const skipAttributes = node.attributes?.some(attribute =>
        attribute.name === 'translate' && attribute.value === 'no'
      );
      if (!skipAttributes) {
        for (const attribute of node.attributes || []) {
          if (!translatedAttributes.has(attribute.name) || !attribute.value.trim()) continue;
          const key = keyFor(attribute.value.trim(), htmlPath);
          replacements.push({
            start: attribute.sourceSpan.start.offset,
            end: attribute.sourceSpan.end.offset,
            value: attributeBinding(attribute.name, key)
          });
        }
      }
    }

    if (node.children?.length) {
      collectReplacements(
        node.children,
        source,
        htmlPath,
        node.constructor.name === 'Element' ? [...ancestors, node] : ancestors,
        replacements
      );
    }
  }
  return replacements;
}

function addPipeImport(tsPath) {
  if (!fs.existsSync(tsPath)) return;
  let source = fs.readFileSync(tsPath, 'utf8');
  if (source.includes('UiTextPipe')) return;

  let relativePipePath = path.relative(path.dirname(tsPath), pipePath).replace(/\\/g, '/');
  if (!relativePipePath.startsWith('.')) relativePipePath = `./${relativePipePath}`;
  source = `import { UiTextPipe } from '${relativePipePath}';\n${source}`;

  if (/imports\s*:\s*\[/.test(source)) {
    source = source.replace(/imports\s*:\s*\[/, match => `${match}UiTextPipe, `);
  } else if (/standalone\s*:\s*true\s*,/.test(source)) {
    source = source.replace(/standalone\s*:\s*true\s*,/, match => `${match}\n  imports: [UiTextPipe],`);
  } else {
    throw new Error(`No se pudo registrar UiTextPipe en ${tsPath}`);
  }

  fs.writeFileSync(tsPath, source);
}

const htmlFiles = walkFiles(appRoot).filter(file => file.endsWith('.html'));

for (const htmlPath of htmlFiles) {
  const originalSource = fs.readFileSync(htmlPath, 'utf8');
  let source = normalizePreviousPass(originalSource);
  const parsed = parseTemplate(source, htmlPath, { preserveWhitespaces: true });
  if (parsed.errors?.length) {
    throw new Error(`${htmlPath}: ${parsed.errors.map(error => error.toString()).join('\n')}`);
  }

  const collectedReplacements = collectReplacements(parsed.nodes, source, htmlPath);
  const replacements = [...new Map(
    collectedReplacements.map(replacement => [`${replacement.start}:${replacement.end}`, replacement])
  ).values()].sort((left, right) => right.start - left.start);
  if (!replacements.length && source === originalSource) continue;

  for (const replacement of replacements) {
    source = source.slice(0, replacement.start) + replacement.value + source.slice(replacement.end);
  }

  fs.writeFileSync(htmlPath, source);
  addPipeImport(htmlPath.replace(/\.html$/, '.ts'));
}

fs.writeFileSync(dictionaryPath, `${JSON.stringify(dictionary, null, 2)}\n`);
console.log(`Migradas ${htmlFiles.length} plantillas al diccionario de interfaz.`);
