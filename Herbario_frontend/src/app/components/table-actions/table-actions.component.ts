import { translateUiText } from '../../core/services/ui-text.service';
import { CommonModule } from "@angular/common";
import { Component, EventEmitter, Input, Output, inject } from "@angular/core";
import { TokenService } from '../../core/services/token.service';

@Component({
  selector: 'app-table-actions',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './table-actions.component.html',
  styleUrl: './table-actions.component.scss'
})
export class TableActionsComponent {
  private tokenService = inject(TokenService);
  @Input() editLabel = translateUiText('actions.edit');
  @Input() deleteLabel = translateUiText('actions.delete');
  @Input() viewLabel = 'Ver';
  @Input() editDisabled = false;
  @Input() deleteDisabled = false;
  @Input() showEdit = true;
  @Input() showDelete = true;
  @Input() showView = false;
  @Input() editPermission = '';
  @Input() deletePermission = '';
  @Output() edit = new EventEmitter<void>();
  @Output() delete = new EventEmitter<void>();
  @Output() view = new EventEmitter<void>();

  get canEdit(): boolean {
    return this.showEdit && (!this.editPermission || this.tokenService.hasPermission(this.editPermission));
  }

  get canDelete(): boolean {
    return this.showDelete && (!this.deletePermission || this.tokenService.hasPermission(this.deletePermission));
  }
}
