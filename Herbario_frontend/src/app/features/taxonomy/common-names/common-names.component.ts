import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { CommonNameService } from '../../../core/services/common-name.service';
import { SpeciesService } from '../../../core/services/species.service';
import { LanguageService } from '../../../core/services/language.service';
import { showConfirm, showError, showSuccess } from '../../../shared/utils/alerts';
import { FormModalComponent, HasPermissionDirective, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../../components';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-common-names',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './common-names.component.html',
  styleUrl: './common-names.component.scss'
})
export class CommonNamesComponent implements OnInit {
  private service = inject(CommonNameService);
  private speciesService = inject(SpeciesService);
  private languageService = inject(LanguageService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  speciesList: any[] = [];
  languages: any[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 80 },
    { kind: 'text', width: 62 },
    { kind: 'text', width: 78 },
    { kind: 'text', width: 58 },
    { kind: 'text', width: 68 },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    species_id: ['', Validators.required],
    language_id: ['', Validators.required],
    common_name: ['', [Validators.required, Validators.maxLength(255), lettersSpacesValidator]],
    dialect: ['', [Validators.maxLength(120), lettersSpacesValidator]]
  });

  ngOnInit(): void {
    this.loadData();
    this.speciesService.getAll(1, 9999).subscribe(res => this.speciesList = res.results || []);
    this.languageService.getAll(1, 9999).subscribe(res => this.languages = res.results || []);
  }

  speciesName(speciesId: string): string {
    return this.speciesList.find(species => species.id === speciesId)?.name || translateUiText('code.features.taxonomy.common_names.common_names.especie_no_disponible');
  }

  languageName(languageId: string): string {
    return this.languages.find(language => language.id === languageId)?.name || translateUiText('code.features.taxonomy.common_names.common_names.idioma_no_disponible');
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
      species_id: item.species_id,
      language_id: item.language_id,
      common_name: item.common_name,
      dialect: item.dialect
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
          showSuccess(translateUiText('code.features.admin.roles.roles.actualizado'), res.message || translateUiText('code.features.taxonomy.common_names.common_names.nombre_comun_actualizado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.common_names.common_names.error_al_actualizar_nombre_comun')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.admin.roles.roles.creado'), res.message || translateUiText('code.features.taxonomy.common_names.common_names.nombre_comun_creado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.common_names.common_names.error_al_crear_nombre_comun')))
      });
    }
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.taxonomy.common_names.common_names.estas_seguro_de_eliminar_este_nombre_comun'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.admin.roles.roles.eliminado'), res.message || translateUiText('code.features.taxonomy.common_names.common_names.nombre_comun_eliminado_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.taxonomy.common_names.common_names.error_al_eliminar_nombre_comun'))
    });
  }
}
