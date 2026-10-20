import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { TranslationService } from '../../../core/services/translation.service';
import { CommonNameService } from '../../../core/services/common-name.service';
import { LanguageService } from '../../../core/services/language.service';
import { showConfirm, showError, showSuccess } from '../../../shared/utils/alerts';
import { FormModalComponent, HasPermissionDirective, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../../components';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-translations',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './translations.component.html',
  styleUrl: './translations.component.scss'
})
export class TranslationsComponent implements OnInit {
  private service = inject(TranslationService);
  private commonNameService = inject(CommonNameService);
  private languageService = inject(LanguageService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  commonNames: any[] = [];
  languages: any[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 74 },
    { kind: 'text', width: 60 },
    { kind: 'text', width: 78 },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    common_name_id: ['', Validators.required],
    language_id: ['', Validators.required],
    translated_name: ['', [Validators.required, Validators.maxLength(255), lettersSpacesValidator]]
  });

  ngOnInit(): void {
    this.loadData();
    this.commonNameService.getAll().subscribe(res => this.commonNames = res.results || []);
    this.languageService.getAll(1, 9999).subscribe(res => this.languages = res.results || []);
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
      common_name_id: item.common_name_id,
      language_id: item.language_id,
      translated_name: item.translated_name
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
          showSuccess(translateUiText('code.features.collections.collections.actualizada'), res.message || translateUiText('code.features.taxonomy.translations.translations.traduccion_actualizada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.translations.translations.error_al_actualizar_traduccion')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.collections.collections.creada'), res.message || translateUiText('code.features.taxonomy.translations.translations.traduccion_creada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.translations.translations.error_al_crear_traduccion')))
      });
    }
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.taxonomy.translations.translations.estas_seguro_de_eliminar_esta_traduccion'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.collections.collections.eliminada'), res.message || translateUiText('code.features.taxonomy.translations.translations.traduccion_eliminada_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.taxonomy.translations.translations.error_al_eliminar_traduccion'))
    });
  }
}
