import { translateUiText } from '../../core/services/ui-text.service';
import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from "@angular/core";
import {
  FormModalComponent,
  HasPermissionDirective,
  PageSizeSelectorComponent,
  PaginationComponent,
  SelectInputComponent,
  SelectInputOption,
  TableActionsComponent,
  TablePlaceholderColumn,
  TablePlaceholderComponent,
  TableSearchComponent
} from '../../components';
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { CollectionService } from '../../core/services/collection.service';
import { SpecimenService } from '../../core/services/specimen.service';
import { showConfirm, showError, showSuccess } from '../../shared/utils/alerts';
import { ControlValidationMessageDirective } from '../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator, noHtmlValidator } from '../../shared/utils/form-validation';

@Component({
  selector: 'app-collections',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, SelectInputComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './collections.component.html',
  styleUrl: './collections.component.scss'
})
export class CollectionsComponent implements OnInit {
  private service = inject(CollectionService);
  private specimenService = inject(SpecimenService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  specimenOptions: SelectInputOption[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  loadingSpecimens = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 72 },
    { kind: 'text', width: 92 },
    { kind: 'badge' },
    { kind: 'count' },
    { kind: 'actions', actionCount: 2 }
  ];

  readonly collectionTypes = [
    { value: 'destacada', label: translateUiText('views.features.taxonomy.species.species.destacada') },
    { value: 'amenazada', label: translateUiText('code.features.collections.collections.amenazada') },
    { value: 'reciente', label: translateUiText('code.features.collections.collections.registros_recientes') },
    { value: 'local', label: translateUiText('collections.types.local') },
    { value: 'general', label: translateUiText('collections.types.general') }
  ];

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(120), lettersSpacesValidator]],
    description: ['', noHtmlValidator],
    collection_type: ['general'],
    specimen_ids: [[] as string[]]
  });

  ngOnInit(): void {
    this.loadData();
    this.loadSpecimens();
  }

  loadSpecimens(): void {
    this.loadingSpecimens = true;
    this.specimenService.getAll(1, 9999, '', {}, true).subscribe({
      next: res => {
        this.specimenOptions = (res.results || []).map(specimen => ({
          value: specimen.id,
          label: specimen.species_name
            ? `${specimen.catalog_code} — ${specimen.species_name}`
            : specimen.catalog_code
        }));
        this.loadingSpecimens = false;
      },
      error: err => {
        this.specimenOptions = [];
        this.loadingSpecimens = false;
        showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.collections.collections.no_se_pudieron_cargar_los_especimenes'));
      }
    });
  }

  loadData(): void {
    this.loading = true;
    this.service.getAll(this.currentPage, this.pageSize, this.searchQuery, {}, true).subscribe({
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

  collectionTypeLabel(value: string): string {
    return this.collectionTypes.find(type => type.value === value)?.label || value;
  }

  openCreateModal(): void {
    this.selectedId = null;
    this.form.reset({
      name: '',
      description: '',
      collection_type: 'general',
      specimen_ids: []
    });
    this.formModalOpen = true;
  }


  edit(item: any): void {
    this.selectedId = item.id;
    this.form.patchValue({
      name: item.name,
      description: item.description,
      collection_type: item.collection_type,
      specimen_ids: item.specimen_ids || []
    });
    this.formModalOpen = true;
  }

  resetForm(): void {
    this.selectedId = null;
    this.form.reset({ collection_type: 'general', specimen_ids: [] });
    this.formModalOpen = false;
  }

  save(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.form.value as any;
    if (this.selectedId) {
      this.service.update(this.selectedId, payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.collections.collections.actualizada'), res.message || translateUiText('code.features.collections.collections.coleccion_actualizada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.collections.collections.error_al_actualizar_coleccion')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.collections.collections.creada'), res.message || translateUiText('code.features.collections.collections.coleccion_creada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.collections.collections.error_al_crear_coleccion')))
      });
    }
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.collections.collections.estas_seguro_de_eliminar_esta_coleccion'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.collections.collections.eliminada'), res.message || translateUiText('code.features.collections.collections.coleccion_eliminada_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.collections.collections.error_al_eliminar_coleccion'))
    });
  }
}
