import { translateUiText } from '../../core/services/ui-text.service';
import { CommonModule } from "@angular/common";
import { Component, EventEmitter, Input, Output } from "@angular/core";
import { ModalComponent } from '../modal/modal.component';

@Component({
  selector: 'app-form-modal',
  standalone: true,
  imports: [CommonModule, ModalComponent],
  templateUrl: './form-modal.component.html',
  styleUrl: './form-modal.component.scss'
})
export class FormModalComponent {
  @Input() open = false;
  @Input() title = '';
  @Input() subtitle = '';
  @Input() formId = '';
  @Input() mode: 'create' | 'edit' = 'create';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() busy = false;
  @Input() submitDisabled = false;
  @Input() cancelText = translateUiText('actions.cancel');
  @Input() submitText = '';
  @Input() submitIcon = '';
  @Output() closed = new EventEmitter<void>();

  get actionText(): string {
    if (this.busy) return translateUiText('code.components.form_modal.form_modal.guardando');
    if (this.submitText) return this.submitText;
    return this.mode === 'edit' ? translateUiText('actions.saveChanges') : translateUiText('code.components.form_modal.form_modal.crear');
  }

  get actionIcon(): string {
    return this.submitIcon || (this.mode === 'edit' ? 'save' : 'add');
  }
}
