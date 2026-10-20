import { translateUiText } from '../../core/services/ui-text.service';
import { AfterViewInit, DestroyRef, Directive, ElementRef, OnDestroy, Renderer2, inject } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { NgControl } from "@angular/forms";
import { merge, startWith } from 'rxjs';

@Directive({ selector: "[formControlName]", standalone: true })
export class ControlValidationMessageDirective implements AfterViewInit, OnDestroy {
  private readonly control = inject(NgControl);
  private readonly element = inject(ElementRef<HTMLElement>);
  private readonly renderer = inject(Renderer2);
  private readonly destroyRef = inject(DestroyRef);
  private messageElement?: HTMLElement;

  ngAfterViewInit(): void {
    const angularControl = this.control.control;
    if (!angularControl) return;
    const controlEvents = (angularControl as any).events ?? angularControl.valueChanges;
    merge(angularControl.statusChanges, angularControl.valueChanges, controlEvents)
      .pipe(startWith(null), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.render());
  }

  ngOnDestroy(): void {
    this.removeMessage();
    this.renderer.removeClass(this.element.nativeElement, 'is-invalid');
    this.renderer.removeClass(this.element.nativeElement, 'is-valid');
  }

  private render(): void {
    const control = this.control.control;
    const message = control?.touched && control.invalid ? this.message(control.errors) : '';
    const nativeElement = this.element.nativeElement;

    if (!message) {
      this.renderer.removeClass(nativeElement, 'is-invalid');
      this.removeMessage();

      if (control && control.valid && (control.dirty || control.touched) && this.hasValue(control.value)) {
        this.renderer.addClass(nativeElement, 'is-valid');
      } else {
        this.renderer.removeClass(nativeElement, 'is-valid');
      }
      return;
    }

    this.renderer.removeClass(nativeElement, 'is-valid');
    this.renderer.addClass(nativeElement, 'is-invalid');
    if (!this.messageElement) {
      this.messageElement = this.renderer.createElement('div');
      this.renderer.addClass(this.messageElement, 'invalid-feedback');
      this.renderer.addClass(this.messageElement, 'd-block');
      this.renderer.addClass(this.messageElement, 'auto-validation-message');
      this.renderer.setAttribute(this.messageElement, 'role', 'alert');

      const parent = nativeElement.parentElement;
      const wrapped = parent?.classList.contains('field-with-icon') || parent?.classList.contains('input-group');
      const anchor = wrapped && parent ? parent : nativeElement;
      const legacyMessage = anchor.nextElementSibling as HTMLElement | null;
      if (legacyMessage?.classList.contains('invalid-feedback') || legacyMessage?.classList.contains('text-danger')) {
        this.renderer.setStyle(legacyMessage, 'display', 'none');
      }
      this.renderer.insertBefore(anchor.parentNode, this.messageElement, anchor.nextSibling);
    }

    this.renderer.setProperty(this.messageElement, "textContent", message);
  }

  private hasValue(value: unknown): boolean {
    if (Array.isArray(value)) return value.length > 0;
    if (typeof value === 'string') return value.trim().length > 0;
    if (typeof value === 'boolean') return value;
    return value !== null && value !== undefined;
  }

  private removeMessage(): void {
    if (!this.messageElement) return;
    const parent = this.messageElement.parentNode;
    if (parent) this.renderer.removeChild(parent, this.messageElement);
    this.messageElement = undefined;
  }

  private message(errors: Record<string, any> | null): string {
    if (!errors) return '';
    if (errors['backend']) return Array.isArray(errors['backend']) ? errors['backend'].join(' ') : String(errors['backend']);
    if (errors['required']) return translateUiText('code.shared.directives.control_validation_message_directive.este_campo_es_obligatorio');
    if (errors['email']) return translateUiText('code.shared.directives.control_validation_message_directive.ingresa_un_correo_electronico_valido');
    if (errors['minlength']) return translateUiText('dynamic.validation.minLength', { length: errors['minlength'].requiredLength });
    if (errors['maxlength']) return translateUiText('dynamic.validation.maxLength', { length: errors['maxlength'].requiredLength });
    if (errors['min'] || errors['max']) {
      const min = errors['min']?.min;
      const max = errors['max']?.max;
      return min != null
        ? translateUiText('dynamic.validation.minValue', { value: min })
        : translateUiText('dynamic.validation.maxValue', { value: max });
    }
    if (errors["lettersSpaces"]) return translateUiText('code.shared.directives.control_validation_message_directive.solo_se_permiten_letras_y_espacios_sin_numeros_n');
    if (errors["alphanumericHyphen"]) return translateUiText('code.shared.directives.control_validation_message_directive.solo_se_permiten_letras_numeros_espacios_y_guion');
    if (errors["noHtml"]) return translateUiText('code.shared.directives.control_validation_message_directive.no_se_permiten_etiquetas_html');
    if (errors['pattern']) return translateUiText('code.shared.directives.control_validation_message_directive.el_formato_ingresado_no_es_valido');
    if (errors["atLeastOne"]) return translateUiText('code.shared.directives.control_validation_message_directive.selecciona_al_menos_una_opcion');
    return translateUiText('code.shared.directives.control_validation_message_directive.el_valor_ingresado_no_es_valido');
  }
}
