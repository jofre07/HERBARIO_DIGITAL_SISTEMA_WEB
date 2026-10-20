import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { GenusService } from '../../../core/services/genus.service';
import { FamilyService } from '../../../core/services/family.service';
import { showConfirm, showError, showSuccess } from '../../../shared/utils/alerts';
import { FormModalComponent, HasPermissionDirective, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../../components';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator, noHtmlValidator } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-genera',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './genera.component.html',
  styleUrl: './genera.component.scss'
})
export class GeneraComponent implements OnInit {
  private service = inject(GenusService);
  private familyService = inject(FamilyService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  families: any[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 62 },
    { kind: 'text', width: 68 },
    { kind: 'text', width: 90 },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(255), lettersSpacesValidator]],
    family_id: ['', Validators.required],
    comment: ['', noHtmlValidator]
  });

  ngOnInit(): void {
    this.loadData();
    this.familyService.getAll().subscribe(res => this.families = res.results || []);
  }

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
    this.form.patchValue({
      name: item.name,
      family_id: item.family_id,
      comment: item.comment
    });
    this.formModalOpen = true;
  }

  resetForm(): void {
    this.selectedId = null;
    this.form.reset();
    this.formModalOpen = false;
  }

  save(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.form.value as any;
    if (this.selectedId) {
      this.service.update(this.selectedId, payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.admin.roles.roles.actualizado'), res.message || translateUiText('code.features.taxonomy.genera.genera.genero_actualizado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.genera.genera.error_al_actualizar_genero')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.admin.roles.roles.creado'), res.message || translateUiText('code.features.taxonomy.genera.genera.genero_creado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.genera.genera.error_al_crear_genero')))
      });
    }
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.taxonomy.genera.genera.estas_seguro_de_eliminar_este_genero'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.admin.roles.roles.eliminado'), res.message || translateUiText('code.features.taxonomy.genera.genera.genero_eliminado_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.taxonomy.genera.genera.error_al_eliminar_genero'))
    });
  }
}
