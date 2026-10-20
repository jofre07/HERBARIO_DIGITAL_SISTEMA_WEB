import { translateUiText } from '../../core/services/ui-text.service';
import { CommonModule } from "@angular/common";
import { Component, EventEmitter, Input, Output } from "@angular/core";
import { ModalComponent } from '../modal/modal.component';

@Component({
  selector: 'app-confirmation-modal',
  standalone: true,
  imports: [CommonModule, ModalComponent],
  templateUrl: './confirmation-modal.component.html',
  styleUrl: './confirmation-modal.component.scss'
})
export class ConfirmationModalComponent {
  @Input() open = false;
  @Input() title = translateUiText('code.components.confirmation_modal.confirmation_modal.confirmar_accion');
  @Input() subtitle = '';
  @Input() message = translateUiText('code.components.confirmation_modal.confirmation_modal.deseas_continuar_con_esta_accion');
  @Input() icon = 'warning';
  @Input() tone: 'danger' | 'warning' = 'danger';
  @Input() busy = false;
  @Input() cancelText = translateUiText('actions.cancel');
  @Input() confirmText = translateUiText('code.components.confirmation_modal.confirmation_modal.confirmar');
  @Input() busyText = translateUiText('code.components.confirmation_modal.confirmation_modal.procesando');
  @Output() closed = new EventEmitter<void>();
  @Output() confirmed = new EventEmitter<void>();

  close(): void {
    if (!this.busy) {
      this.closed.emit();
    }
  }
}
