import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { ConservationStatusService } from '../../../core/services/conservation-status.service';
import { SpeciesService } from '../../../core/services/species.service';
import { StatusService } from '../../../core/services/status.service';
import { showConfirm, showError, showSuccess } from '../../../shared/utils/alerts';
import { FormModalComponent, HasPermissionDirective, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../../components';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-conservation-statuses',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './conservation-statuses.component.html',
  styleUrl: './conservation-statuses.component.scss'
})
export class ConservationStatusesComponent implements OnInit {
  private service = inject(ConservationStatusService);
  private speciesService = inject(SpeciesService);
  private statusService = inject(StatusService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  speciesList: any[] = [];
  statuses: any[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 76 },
    { kind: 'text', width: 64 },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    species_id: ['', Validators.required],
    status_id: ['', Validators.required]
  });

  ngOnInit(): void {
    this.loadData();
    this.speciesService.getAll(1, 9999).subscribe(res => this.speciesList = res.results || []);
    this.statusService.getAll(1, 9999).subscribe(res => this.statuses = res.results || []);
  }

  speciesName(speciesId: string): string {
    return this.speciesList.find(species => species.id === speciesId)?.name || translateUiText('code.features.taxonomy.common_names.common_names.especie_no_disponible');
  }

  statusName(statusId: string): string {
    return this.statuses.find(status => status.id === statusId)?.name || translateUiText('code.features.taxonomy.conservation_statuses.conservation_statuses.estado_no_disponible');
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
      status_id: item.status_id
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
          showSuccess(translateUiText('code.features.admin.roles.roles.actualizado'), res.message || translateUiText('code.features.taxonomy.conservation_statuses.conservation_statuses.estado_de_conservacion_actualizado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.conservation_statuses.conservation_statuses.error_al_actualizar_estado_de_conservacion')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.admin.roles.roles.creado'), res.message || translateUiText('code.features.taxonomy.conservation_statuses.conservation_statuses.estado_de_conservacion_creado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.taxonomy.conservation_statuses.conservation_statuses.error_al_crear_estado_de_conservacion')))
      });
    }
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.taxonomy.conservation_statuses.conservation_statuses.estas_seguro_de_eliminar_este_estado_de_conserva'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.admin.roles.roles.eliminado'), res.message || translateUiText('code.features.taxonomy.conservation_statuses.conservation_statuses.estado_de_conservacion_eliminado_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.taxonomy.conservation_statuses.conservation_statuses.error_al_eliminar_estado_de_conservacion'))
    });
  }
}
