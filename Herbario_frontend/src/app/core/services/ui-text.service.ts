import { Injectable } from '@angular/core';
import spanishDictionary from '../../../../public/i18n/es.json';

type DictionaryValue = string | Dictionary;
type Dictionary = { [key: string]: DictionaryValue };
export type UiTextParameter = string | number | null | undefined;
export type UiTextParameters = Record<string, UiTextParameter>;

const dictionary = spanishDictionary as Dictionary;

export function translateUiText(key: string, parameters: UiTextParameters = {}): string {
  const value = key.split('.').reduce<DictionaryValue | undefined>((current, part) => {
    if (!current || typeof current === 'string') return undefined;
    return current[part];
  }, dictionary);

  if (typeof value !== 'string') return key;

  return value.replace(/{{\s*([\w.-]+)\s*}}/g, (match, parameter: string) =>
    Object.prototype.hasOwnProperty.call(parameters, parameter)
      ? String(parameters[parameter] ?? '')
      : match
  );
}

@Injectable({ providedIn: 'root' })
export class UiTextService {
  get(key: string, parameters: UiTextParameters = {}): string {
    return translateUiText(key, parameters);
  }
}
