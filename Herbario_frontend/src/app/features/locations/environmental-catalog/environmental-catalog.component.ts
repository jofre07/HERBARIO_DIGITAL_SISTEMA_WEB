import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { FormModalComponent, HasPermissionDirective, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../../components';
import { EnvironmentalCatalogItem } from '../../../core/interfaces/environmental-catalog.interface';
import { EnvironmentalCatalogService, EnvironmentalCatalogType } from '../../../core/services/environmental-catalog.service';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator } from '../../../shared/utils/form-validation';
import { showConfirm, showError, showSuccess } from '../../../shared/utils/alerts';

interface CatalogRouteData {
  type: EnvironmentalCatalogType;
  title: string;
  singular: string;
  plural: string;
  icon: string;
  permissionModel: 'climate' | 'habitat';
}

@Component({
  selector: 'app-environmental-catalog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, FormModalComponent, HasPermissionDirective, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderComponent, TableSearchComponent],
  templateUrl: './environmental-catalog.component.html',
  styleUrl: './environmental-catalog.component.scss'
})
export class EnvironmentalCatalogComponent implements OnInit {
  private readonly service = inject(EnvironmentalCatalogService);
  private readonly fb = inject(FormBuilder);
  private readonly routeData = inject(ActivatedRoute).snapshot.data as CatalogRouteData;

  readonly type = this.routeData.type;
  readonly title = this.routeData.title;
  readonly singular = this.routeData.singular;
  readonly plural = this.routeData.plural;
  readonly icon = this.routeData.icon;
  readonly addPermission = `locations.add_${this.routeData.permissionModel}`;
  readonly editPermission = `locations.change_${this.routeData.permissionModel}`;
  readonly deletePermission = `locations.delete_${this.routeData.permissionModel}`;

  items: EnvironmentalCatalogItem[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  saving = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 52 },
    { kind: 'actions', actionCount: 2 }
  ];

  readonly form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(100), lettersSpacesValidator]]
  });

  ngOnInit(): void { this.loadData(); }

  loadData(): void {
    this.loading = true;
    this.service.getAll(this.type, this.currentPage, this.pageSize, this.searchQuery).subscribe({
      next: response => {
        this.items = response.results || [];
        this.totalItems = response.count || 0;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  onSearch(query: string): void {
    this.searchQuery = query;
    this.currentPage = 1;
    this.loadData();
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.loadData();
  }

  openCreateModal(): void {
    this.selectedId = null;
    this.form.reset();
    this.formModalOpen = true;
  }

  edit(item: EnvironmentalCatalogItem): void {
    this.selectedId = item.id;
    this.form.setValue({ name: item.name });
    this.formModalOpen = true;
  }

  resetForm(): void {
    this.selectedId = null;
    this.form.reset();
    this.formModalOpen = false;
  }

  save(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = { name: this.form.controls.name.value!.trim() };
    const request = this.selectedId
      ? this.service.update(this.type, this.selectedId, payload)
      : this.service.create(this.type, payload);
    this.saving = true;
    request.subscribe({
      next: response => {
        this.saving = false;
        showSuccess(this.selectedId ? `${this.singular} actualizado` : `${this.singular} creado`, response.message || 'El registro se guardó correctamente.');
        this.resetForm();
        this.currentPage = 1;
        this.loadData();
      },
      error: error => {
        this.saving = false;
        showError('Error', handleFormApiError(this.form, error, `No se pudo guardar el ${this.singular.toLowerCase()}.`));
      }
    });
  }

  async remove(item: EnvironmentalCatalogItem): Promise<void> {
    const confirmed = await showConfirm(`Eliminar ${this.singular.toLowerCase()}`, `¿Estás seguro de eliminar “${item.name}”?`);
    if (!confirmed.isConfirmed) return;
    this.service.delete(this.type, item.id).subscribe({
      next: response => {
        showSuccess(`${this.singular} eliminado`, response.message || 'El registro se eliminó correctamente.');
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: error => showError('No se puede eliminar', error.error?.message || `El ${this.singular.toLowerCase()} está siendo utilizado.`)
    });
  }
}
