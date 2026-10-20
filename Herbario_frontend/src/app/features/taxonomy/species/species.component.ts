import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { SpeciesService } from '../../../core/services/species.service';
import { GenusService } from '../../../core/services/genus.service';
import { showConfirm, showError, showSuccess } from '../../../shared/utils/alerts';
import { FormModalComponent, HasPermissionDirective, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../../components';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator, noHtmlValidator } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-species',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './species.component.html',
  styleUrl: './species.component.scss'
})
export class SpeciesComponent implements OnInit {
  private service = inject(SpeciesService);
  private genusService = inject(GenusService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  genera: any[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 76 },
    { kind: 'text', width: 70 },
    { kind: 'text', width: 70 },
    { kind: 'badge' },
    { kind: 'text', width: 88 },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(255), lettersSpacesValidator]],
    genus_id: ['', Validators.required],
    comment: ['', noHtmlValidator],
    is_featured: [false]
  });

  ngOnInit(): void {
    this.loadData();
    this.genusService.getAll().subscribe(res => this.genera = res.results || []);
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
    this.form.reset({ name: '', genus_id: '', comment: '', is_featured: false });
    this.formModalOpen = true;
  }


  edit(item: any): void {
    this.selectedId = item.id;
    this.form.patchValue({
      name: item.name,
      genus_id: item.genus_id,
      comment: item.comment,
      is_featured: item.is_featured
    });
    this.formModalOpen = true;
  }

  resetForm(): void {
    this.selectedId = null;
    this.form.reset({ name: '', genus_id: '', comment: '', is_featured: false });
    this.formModalOpen = false;
  }

  save(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.form.value as any;
    if (this.selectedId) {
      this.service.update(this.selectedId, payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.collections.collections.actualizada'), res.message || translateUiText('code.features.taxonomy.species.species.especie_actualizada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.species.species.error_al_actualizar_especie')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.collections.collections.creada'), res.message || translateUiText('code.features.taxonomy.species.species.especie_creada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.species.species.error_al_crear_especie')))
      });
    }
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.taxonomy.species.species.estas_seguro_de_eliminar_esta_especie'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.collections.collections.eliminada'), res.message || translateUiText('code.features.taxonomy.species.species.especie_eliminada_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.taxonomy.species.species.error_al_eliminar_especie'))
    });
  }
}
