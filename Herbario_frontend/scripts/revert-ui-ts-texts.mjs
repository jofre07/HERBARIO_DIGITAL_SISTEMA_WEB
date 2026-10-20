import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const appRoot = path.join(root, 'src', 'app');
const dictionaryPath = path.join(root, 'public', 'i18n', 'es.json');
const dictionary = JSON.parse(fs.readFileSync(dictionaryPath, 'utf8'));

function valueAt(key) {
  return key.split('.').reduce((current, part) => current?.[part], dictionary);
}

function walkFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const fullPath = path.join(directory, entry.name);
    return entry.isDirectory() ? walkFiles(fullPath) : [fullPath];
  });
}

for (const file of walkFiles(appRoot).filter(file => file.endsWith('.ts'))) {
  let source = fs.readFileSync(file, 'utf8');
  source = source.replace(/translateUiText\('([^']+)'\)/g, (match, key) => {
    const value = valueAt(key);
    return typeof value === 'string' ? JSON.stringify(value) : match;
  });
  source = source.replace(/^import \{ translateUiText \} from '[^']+';\r?\n/gm, '');
  fs.writeFileSync(file, source);
}

delete dictionary.code;
fs.writeFileSync(dictionaryPath, `${JSON.stringify(dictionary, null, 2)}\n`);
console.log('Migración TypeScript amplia revertida de forma segura.');
