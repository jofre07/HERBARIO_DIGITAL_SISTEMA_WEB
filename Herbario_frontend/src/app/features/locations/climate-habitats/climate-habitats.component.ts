import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from "@angular/core";
import { FormModalComponent, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../../components';
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { ClimateHabitatService } from '../../../core/services/climate-habitat.service';
import { LocationService } from '../../../core/services/location.service';
import { showConfirm, showError, showSuccess } from '../../../shared/utils/alerts';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-climate-habitats',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, TableSearchComponent],
  templateUrl: './climate-habitats.component.html',
  styleUrl: './climate-habitats.component.scss'
})
export class ClimateHabitatsComponent implements OnInit {
  private service = inject(ClimateHabitatService);
  private locationService = inject(LocationService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  locations: any[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 84 },
    { kind: 'text', width: 68 },
    { kind: 'text', width: 76 },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    location_id: ['', Validators.required],
    climate: ['', [Validators.maxLength(100), lettersSpacesValidator]],
    habitat: ['', [Validators.maxLength(100), lettersSpacesValidator]]
  });

  ngOnInit(): void {
    this.loadData();
    this.locationService.getAll().subscribe(res => this.locations = res.results || []);
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
      location_id: item.location_id,
      climate: item.climate,
      habitat: item.habitat
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
          showSuccess(translateUiText('code.features.admin.roles.roles.actualizado'), res.message || translateUiText('code.features.locations.climate_habitats.climate_habitats.clima_habitat_actualizado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.locations.climate_habitats.climate_habitats.error_al_actualizar_clima_habitat')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.admin.roles.roles.creado'), res.message || translateUiText('code.features.locations.climate_habitats.climate_habitats.clima_habitat_creado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.locations.climate_habitats.climate_habitats.error_al_crear_clima_habitat')))
      });
    }
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.locations.climate_habitats.climate_habitats.estas_seguro_de_eliminar_este_clima_habitat'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.admin.roles.roles.eliminado'), res.message || translateUiText('code.features.locations.climate_habitats.climate_habitats.clima_habitat_eliminado_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.locations.climate_habitats.climate_habitats.error_al_eliminar_clima_habitat'))
    });
  }
}
