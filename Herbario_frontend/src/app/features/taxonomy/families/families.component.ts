import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { FamilyService } from '../../../core/services/family.service';
import { showError, showSuccess } from '../../../shared/utils/alerts';
import {
  ConfirmationModalComponent,
  FormModalComponent,
  HasPermissionDirective,
  PageSizeSelectorComponent,
  PaginationComponent,
  TableActionsComponent,
  TablePlaceholderColumn,
  TablePlaceholderComponent,
  TableSearchComponent
} from '../../../components';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator, noHtmlValidator } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-families',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, ConfirmationModalComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './families.component.html',
  styleUrl: './families.component.scss'
})
export class FamiliesComponent implements OnInit {
  private service = inject(FamilyService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  selectedId: string | null = null;
  pendingDelete: any | null = null;
  formModalOpen = false;
  deleteModalOpen = false;
  saving = false;
  deleting = false;
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 64 },
    { kind: 'text', width: 90 },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(255), lettersSpacesValidator]],
    comment: ['', noHtmlValidator]
  });

  ngOnInit(): void { this.loadData(); }

  loadData(): void {
    this.loading = true;
    this.service.getAll(this.currentPage, this.pageSize, this.searchQuery).subscribe({
      next: (res) => {
        this.items = res.results || [];
        this.totalItems = res.count || 0;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.loadData();
  }

  onSearch(query: string): void {
    this.searchQuery = query;
    this.currentPage = 1;
    this.loadData();
  }

  openCreateModal(): void {
    this.selectedId = null;
    this.form.reset();
    this.formModalOpen = true;
  }

  edit(item: any): void {
    this.selectedId = item.id;
    this.form.patchValue({ name: item.name, comment: item.comment });
    this.formModalOpen = true;
  }

  resetForm(): void {
    this.selectedId = null;
    this.form.reset();
    this.formModalOpen = false;
  }

  save(): void {
    if (this.form.invalid || this.saving) {
      this.form.markAllAsTouched();
      return;
    }
    this.saving = true;
    const payload = this.form.value as any;
    if (this.selectedId) {
      this.service.update(this.selectedId, payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.admin.roles.roles.actualizado'), res.message || translateUiText('code.features.taxonomy.families.families.familia_actualizada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
          this.saving = false;
        },
        error: (err) => {
          this.saving = false;
          showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.families.families.error_al_actualizar_familia')));
        }
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.collections.collections.creada'), res.message || translateUiText('code.features.taxonomy.families.families.familia_creada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
          this.saving = false;
        },
        error: (err) => {
          this.saving = false;
          showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.families.families.error_al_crear_familia')));
        }
      });
    }
  }

  remove(item: any): void {
    this.pendingDelete = item;
    this.deleteModalOpen = true;
  }

  closeDeleteModal(): void {
    if (this.deleting) return;
    this.deleteModalOpen = false;
    this.pendingDelete = null;
  }

  confirmDelete(): void {
    if (!this.pendingDelete || this.deleting) return;
    this.deleting = true;
    this.service.delete(this.pendingDelete.id).subscribe({
      next: (res) => {
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        showSuccess(translateUiText('code.features.collections.collections.eliminada'), res.message || translateUiText('code.features.taxonomy.families.families.familia_eliminada_correctamente'));
        this.deleteModalOpen = false;
        this.pendingDelete = null;
        this.deleting = false;
        this.loadData();
      },
      error: (err) => {
        this.deleting = false;
        showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.taxonomy.families.families.error_al_eliminar_familia'));
      }
    });
  }
}
