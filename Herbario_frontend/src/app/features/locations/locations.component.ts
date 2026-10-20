import { translateUiText } from '../../core/services/ui-text.service';
import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { Component, OnDestroy, OnInit, inject } from "@angular/core";
import { FormModalComponent, HasPermissionDirective, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../components';
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { LocationService } from '../../core/services/location.service';
import { showConfirm, showError, showSuccess } from '../../shared/utils/alerts';
import { ControlValidationMessageDirective } from '../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator, noHtmlValidator } from '../../shared/utils/form-validation';
import * as L from 'leaflet';
import { plantMarkerIcon } from '../../shared/utils/map-marker';

const COORDINATE_PATTERN = /^-?\d{1,3}(?:\.\d{1,8})?$/;

@Component({
  selector: 'app-locations',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './locations.component.html',
  styleUrl: './locations.component.scss'
})
export class LocationsComponent implements OnInit, OnDestroy {
  private service = inject(LocationService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 76 },
    { kind: 'text', width: 82 },
    { kind: 'text', width: 82 },
    { kind: 'text', width: 90 },
    { kind: 'text', width: 28 },
    { kind: 'actions', actionCount: 2 }
  ];
  private map: L.Map | null = null;
  private marker: L.Marker | null = null;

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(255), lettersSpacesValidator]],
    latitude: ['', [Validators.required, Validators.pattern(COORDINATE_PATTERN), Validators.min(-90), Validators.max(90)]],
    longitude: ['', [Validators.required, Validators.pattern(COORDINATE_PATTERN), Validators.min(-180), Validators.max(180)]],
    comment: ['', noHtmlValidator]
  });

  ngOnInit(): void { this.loadData(); }

  ngOnDestroy(): void { this.destroyMap(); }

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
    setTimeout(() => this.initMap());
  }


  edit(item: any): void {
    this.selectedId = item.id;
    this.form.patchValue({
      name: item.name,
      latitude: item.latitude,
      longitude: item.longitude,
      comment: item.comment
    });
    this.formModalOpen = true;
    setTimeout(() => this.initMap());
  }

  resetForm(): void {
    this.selectedId = null;
    this.destroyMap();
    this.form.reset();
    this.formModalOpen = false;
  }

  save(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.form.value as any;
    if (this.selectedId) {
      this.service.update(this.selectedId, payload).subscribe({
        next: () => {
          showSuccess(translateUiText('code.features.collections.collections.actualizada'), translateUiText('code.features.locations.locations.ubicacion_actualizada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.locations.locations.error_al_actualizar_ubicacion')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: () => {
          showSuccess(translateUiText('code.features.collections.collections.creada'), translateUiText('code.features.locations.locations.ubicacion_creada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.locations.locations.error_al_crear_ubicacion')))
      });
    }
  }

  updateMapFromCoordinates(): void {
    const latitude = Number(this.form.controls.latitude.value);
    const longitude = Number(this.form.controls.longitude.value);
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;
    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) return;
    this.setMarker(latitude, longitude);
    this.map?.setView([latitude, longitude], Math.max(this.map.getZoom(), 13));
  }

  private initMap(): void {
    this.destroyMap();
    const element = document.getElementById('location-catalog-map');
    if (!element) return;
    const latitude = Number(this.form.controls.latitude.value);
    const longitude = Number(this.form.controls.longitude.value);
    const hasCoordinates = Number.isFinite(latitude) && Number.isFinite(longitude) && (latitude !== 0 || longitude !== 0);
    this.map = L.map(element, { center: hasCoordinates ? [latitude, longitude] : [-0.95, -80.35], zoom: hasCoordinates ? 14 : 8 });
    this.map.attributionControl.setPrefix(false);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: "&copy; OpenStreetMap", maxZoom: 19 }).addTo(this.map);
    if (hasCoordinates) this.setMarker(latitude, longitude);
    this.map.on('click', (event: L.LeafletMouseEvent) => {
      const selectedLatitude = event.latlng.lat.toFixed(8);
      const selectedLongitude = event.latlng.lng.toFixed(8);
      this.form.patchValue({ latitude: selectedLatitude, longitude: selectedLongitude });
      this.setMarker(Number(selectedLatitude), Number(selectedLongitude));
    });
    setTimeout(() => this.map?.invalidateSize());
  }

  private setMarker(latitude: number, longitude: number): void {
    if (!this.map) return;
    if (this.marker) {
      this.marker.setLatLng([latitude, longitude]);
      return;
    }
    this.marker = L.marker([latitude, longitude], { icon: plantMarkerIcon('plant', true) }).addTo(this.map);
  }

  private destroyMap(): void {
    this.map?.remove();
    this.map = null;
    this.marker = null;
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.locations.locations.estas_seguro_de_eliminar_esta_ubicacion'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.collections.collections.eliminada'), res.message || translateUiText('code.features.locations.locations.ubicacion_eliminada_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.locations.locations.error_al_eliminar_ubicacion'))
    });
  }
}
