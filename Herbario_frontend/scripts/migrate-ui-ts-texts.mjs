import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';

const root = process.cwd();
const appRoot = path.join(root, 'src', 'app');
const dictionaryPath = path.join(root, 'public', 'i18n', 'es.json');
const uiTextModule = path.join(appRoot, 'core', 'services', 'ui-text.service');
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
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 48) || 'texto';
}

function setDictionaryValue(parts, value) {
  let current = dictionary;
  for (const part of parts.slice(0, -1)) {
    if (!current[part] || typeof current[part] === 'string') current[part] = {};
    current = current[part];
  }
  current[parts.at(-1)] = value;
}

function keyFor(text, tsPath) {
  const existing = textToKey.get(text);
  if (existing) return existing;

  const namespace = path.relative(appRoot, tsPath)
    .replace(/\\/g, '/')
    .replace(/\.component\.ts$/, '')
    .replace(/\.ts$/, '')
    .split('/')
    .map(slug);
  const base = slug(text);
  let parts = ['code', ...namespace, base];
  let key = parts.join('.');
  let suffix = 2;

  const valueAt = candidate => candidate.split('.').reduce((current, part) => current?.[part], dictionary);
  while (valueAt(key) !== undefined) {
    parts = ['code', ...namespace, `${base}_${suffix++}`];
    key = parts.join('.');
  }

  setDictionaryValue(parts, text);
  textToKey.set(text, key);
  return key;
}

function isVisibleText(value) {
  if (!/[A-Za-zÁÉÍÓÚÜÑáéíóúüñ¿¡]/.test(value)) return false;
  if (/^[a-z0-9_.-]+$/.test(value)) return false;
  if (/^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)+$/.test(value)) return false;
  if (/^(\/|\.\/|\.\.\/|#|https?:|mailto:|tel:)/.test(value)) return false;
  if (/^\s+[a-z][a-z0-9_-]*$/i.test(value) || /^[a-z-]+\([^)]*\)$/i.test(value)) return false;
  if (/^[dmyhms:/ -]+$/i.test(value)) return false;
  return true;
}

function addImport(source, tsPath) {
  if (/import\s*\{\s*translateUiText\s*\}/.test(source)) return source;
  let modulePath = path.relative(path.dirname(tsPath), uiTextModule).replace(/\\/g, '/');
  if (!modulePath.startsWith('.')) modulePath = `./${modulePath}`;
  return `import { translateUiText } from '${modulePath}';\n${source}`;
}

const uiPropertyNames = new Set([
  'label', 'optionLabel', 'title', 'message', 'description', 'placeholder',
  'searchPlaceholder', 'emptyText', 'cancelText', 'confirmText', 'busyText',
  'confirmButtonText', 'cancelButtonText', 'text'
]);

function propertyName(node) {
  if (!node) return '';
  if (ts.isIdentifier(node) || ts.isStringLiteral(node)) return node.text;
  return '';
}

function hasForbiddenAncestor(node) {
  let current = node.parent;
  while (current) {
    if (ts.isImportDeclaration(current) || ts.isExportDeclaration(current) || ts.isDecorator(current)) return true;
    current = current.parent;
  }
  return false;
}

function isUiContext(node) {
  if (hasForbiddenAncestor(node)) return false;
  const parent = node.parent;
  if (!parent) return false;

  if (ts.isPropertyAssignment(parent) && uiPropertyNames.has(propertyName(parent.name))) return true;
  if (ts.isPropertyDeclaration(parent)) {
    const name = propertyName(parent.name);
    return uiPropertyNames.has(name) || /(Label|Text|Message|Title|Placeholder)$/i.test(name);
  }
  if (ts.isConditionalExpression(parent) && (parent.whenTrue === node || parent.whenFalse === node)) return true;
  if (ts.isBinaryExpression(parent)) {
    return [ts.SyntaxKind.BarBarToken, ts.SyntaxKind.PlusToken].includes(parent.operatorToken.kind);
  }
  if (ts.isReturnStatement(parent)) return true;
  if (ts.isVariableDeclaration(parent) && /^(msg|message|title|label|description)$/i.test(parent.name.getText())) return true;

  let current = parent;
  while (current && !ts.isFunctionLike(current)) {
    if (ts.isCallExpression(current)) {
      const callName = current.expression.getText();
      if (/^(showSuccess|showError|showConfirm|handleFormApiError)$/.test(callName)) return true;
    }
    if (ts.isVariableDeclaration(current) && /_(LABELS|TEXTS|MESSAGES)$/.test(current.name.getText())) return true;
    current = current.parent;
  }
  return false;
}

const tsFiles = walkFiles(appRoot).filter(file =>
  file.endsWith('.ts') &&
  !file.endsWith('.spec.ts') &&
  !file.endsWith('ui-text.service.ts')
);

for (const tsPath of tsFiles) {
  let source = fs.readFileSync(tsPath, 'utf8');
  const sourceFile = ts.createSourceFile(tsPath, source, ts.ScriptTarget.Latest, true);
  const replacements = [];

  function visit(node) {
    if (
      (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) &&
      isVisibleText(node.text) &&
      isUiContext(node)
    ) {
      const key = keyFor(node.text, tsPath);
      replacements.push({
        start: node.getStart(sourceFile),
        end: node.getEnd(),
        value: `translateUiText('${key}')`
      });
      return;
    }
    ts.forEachChild(node, visit);
  }

  visit(sourceFile);
  if (!replacements.length) continue;

  for (const replacement of replacements.sort((left, right) => right.start - left.start)) {
    source = source.slice(0, replacement.start) + replacement.value + source.slice(replacement.end);
  }
  source = addImport(source, tsPath);
  fs.writeFileSync(tsPath, source);
}

fs.writeFileSync(dictionaryPath, `${JSON.stringify(dictionary, null, 2)}\n`);
console.log(`Revisados ${tsFiles.length} archivos TypeScript.`);
