import { AbstractControl, FormGroup, ValidationErrors, ValidatorFn } from "@angular/forms";

const LETTERS_SPACES = /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+$/;
const ALPHANUMERIC_HYPHEN = /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\s-]+$/;
const HTML_TAG = /<[^>]*>/;

export const lettersSpacesValidator: ValidatorFn = (control: AbstractControl): ValidationErrors | null => {
  const value = String(control.value ?? '');
  return !value || LETTERS_SPACES.test(value) ? null : { lettersSpaces: true };
};

export const alphanumericHyphenValidator: ValidatorFn = (control: AbstractControl): ValidationErrors | null => {
  const value = String(control.value ?? '');
  return !value || ALPHANUMERIC_HYPHEN.test(value) ? null : { alphanumericHyphen: true };
};

export const noHtmlValidator: ValidatorFn = (control: AbstractControl): ValidationErrors | null => {
  const value = String(control.value ?? '');
  return !value || !HTML_TAG.test(value) ? null : { noHtml: true };
};

function toMessages(value: unknown): string[] {
  if (Array.isArray(value)) return value.flatMap(toMessages);
  if (typeof value === 'string') return [value];
  if (value && typeof value === 'object') return Object.values(value).flatMap(toMessages);
  return value == null ? [] : [String(value)];
}

function responseErrors(error: any): Record<string, unknown> | null {
  const body = error?.error ?? error;
  const errors = body?.errors ?? body?.error?.errors;
  return errors && typeof errors === 'object' && !Array.isArray(errors) ? errors : null;
}

/** Assigns DRF field errors to matching Angular controls and returns all useful messages. */
export function applyBackendValidationErrors(
  form: FormGroup,
  error: any,
  fieldMap: Record<string, string> = {}
): string[] {
  const errors = responseErrors(error);
  if (!errors) return [];

  const messages: string[] = [];
  for (const [field, detail] of Object.entries(errors)) {
    const fieldMessages = toMessages(detail);
    messages.push(...fieldMessages);

    const control = form.get(fieldMap[field] ?? field);
    if (!control || !fieldMessages.length) continue;

    control.setErrors({ ...control.errors, backend: fieldMessages });
    control.markAsTouched();

    const subscription = control.valueChanges.subscribe(() => {
      const current = control.errors;
      if (current?.['backend']) {
        const { backend: _backend, ...remaining } = current;
        control.setErrors(Object.keys(remaining).length ? remaining : null);
      }
      subscription.unsubscribe();
    });
  }

  form.updateValueAndValidity({ emitEvent: false });
  return messages;
}

export function getApiErrorMessage(error: any, fallback = "Ocurrió un error inesperado."): string {
  const errors = responseErrors(error);
  const details = errors ? Object.values(errors).flatMap(toMessages) : [];
  if (details.length) return [...new Set(details)].join('\n');

  const body = error?.error ?? error;
  return body?.message || body?.detail || fallback;
}

export function handleFormApiError(
  form: FormGroup,
  error: any,
  fallback?: string,
  fieldMap: Record<string, string> = {}
): string {
  applyBackendValidationErrors(form, error, fieldMap);
  return getApiErrorMessage(error, fallback);
}
