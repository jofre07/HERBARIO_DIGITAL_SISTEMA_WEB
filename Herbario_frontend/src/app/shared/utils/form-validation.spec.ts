import { FormControl, FormGroup } from '@angular/forms';
import {
  alphanumericHyphenValidator,
  applyBackendValidationErrors,
  getApiErrorMessage,
  lettersSpacesValidator,
  noHtmlValidator
} from './form-validation';

describe('form validation utilities', () => {
  it('uses the same character rules as the backend', () => {
    expect(lettersSpacesValidator(new FormControl('Español'))).toBeNull();
    expect(lettersSpacesValidator(new FormControl('Español 2'))).toEqual({ lettersSpaces: true });
    expect(alphanumericHyphenValidator(new FormControl('es-EC 2'))).toBeNull();
    expect(alphanumericHyphenValidator(new FormControl('es/EC'))).toEqual({ alphanumericHyphen: true });
    expect(noHtmlValidator(new FormControl('<b>texto</b>'))).toEqual({ noHtml: true });
  });

  it('assigns backend errors to their matching controls', () => {
    const form = new FormGroup({ code: new FormControl('***'), name: new FormControl('123') });
    const error = {
      error: {
        errors: {
          code: ['Solo se permiten letras, números, espacios y guiones.'],
          name: ['Solo se permiten letras y espacios.']
        }
      }
    };

    applyBackendValidationErrors(form, error);

    expect(form.controls.code.getError('backend')).toEqual([
      'Solo se permiten letras, números, espacios y guiones.'
    ]);
    expect(form.controls.name.touched).toBeTrue();
    expect(getApiErrorMessage(error)).toContain('Solo se permiten letras y espacios.');
  });

  it('supports field names that differ in a composed form', () => {
    const form = new FormGroup({ location_name: new FormControl('123') });
    applyBackendValidationErrors(
      form,
      { error: { errors: { name: ['Nombre inválido.'] } } },
      { name: 'location_name' }
    );
    expect(form.controls.location_name.getError('backend')).toEqual(['Nombre inválido.']);
  });

  it('clears a backend error as soon as the field value changes', () => {
    const form = new FormGroup({ code: new FormControl('***') });
    applyBackendValidationErrors(form, {
      error: { errors: { code: ['Código inválido.'] } }
    });

    form.controls.code.setValue('es-EC');

    expect(form.controls.code.hasError('backend')).toBeFalse();
  });
});
