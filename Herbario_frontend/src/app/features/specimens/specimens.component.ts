import { translateUiText } from '../../core/services/ui-text.service';
import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import { Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from "@angular/core";
import { FormArray, FormBuilder, FormsModule, ReactiveFormsModule, Validators } from "@angular/forms";
import * as L from 'leaflet';
import { finalize } from 'rxjs';

import {
  FormModalComponent,
  HasPermissionDirective,
  PageSizeSelectorComponent,
  PaginationComponent,
  TableActionsComponent,
  TablePlaceholderColumn,
  TablePlaceholderComponent,
  TableSearchComponent
} from '../../components';
import {
  Specimen,
  SpecimenListItem,
  SpecimenLocationWrite,
  SpecimenNamedOption,
  SpecimenWrite
} from '../../core/interfaces/specimen.interface';
import { FilterOptionsService } from '../../core/services/filter-options.service';
import { SpecimenService } from '../../core/services/specimen.service';
import { ControlValidationMessageDirective } from '../../shared/directives/control-validation-message.directive';
import { showConfirm, showError, showSuccess } from '../../shared/utils/alerts';
import {
  alphanumericHyphenValidator,
  handleFormApiError,
  lettersSpacesValidator,
  noHtmlValidator
} from '../../shared/utils/form-validation';
import { MARKER_ICON_OPTIONS, MarkerIconType, plantMarkerIcon } from '../../shared/utils/map-marker';

const COORDINATE_PATTERN = /^-?\d{1,3}(?:\.\d{1,8})?$/;

@Component({
  selector: 'app-specimens',
  standalone: true,
  imports: [UiTextPipe, 
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    ControlValidationMessageDirective,
    PaginationComponent,
    PageSizeSelectorComponent,
    TableActionsComponent,
    TablePlaceholderComponent,
    FormModalComponent,
    HasPermissionDirective,
    TableSearchComponent
  ],
  templateUrl: './specimens.component.html',
  styleUrl: './specimens.component.scss'
})
export class SpecimensComponent implements OnInit, OnDestroy {
  private service = inject(SpecimenService);
  private filterOptionsService = inject(FilterOptionsService);
  private fb = inject(FormBuilder);
  private locationMap: L.Map | null = null;
  private locationMarker: L.Marker | null = null;

  @ViewChild("locationsList") private locationsListElement?: ElementRef<HTMLDivElement>;

  items: SpecimenListItem[] = [];
  speciesList: SpecimenNamedOption[] = [];
  collectors: SpecimenNamedOption[] = [];
  climates: SpecimenNamedOption[] = [];
  habitats: SpecimenNamedOption[] = [];
  selectedId: string | null = null;
  formModalOpen = false;
  loading = false;
  loadingFormOptions = false;
  loadingSpecimenDetail = false;
  saving = false;
  currentStep: 1 | 2 = 1;
  activeLocationIndex: number | null = 0;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly markerOptions = MARKER_ICON_OPTIONS;
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 82 },
    { kind: 'text', width: 70 },
    { kind: 'text', width: 68 },
    { kind: 'text', width: 78 },
    { kind: 'text', width: 76 },
    { kind: 'count' },
    { kind: 'badge' },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    catalog_code: ['', [Validators.required, Validators.maxLength(40), alphanumericHyphenValidator]],
    is_published: [false],
    collection_date: [''],
    collection_number: ['', [Validators.maxLength(80), alphanumericHyphenValidator]],
    morphological_description: ['', noHtmlValidator],
    species_id: ['', Validators.required],
    collector_id: [''],
    locations: this.fb.array([])
  });

  get locations(): FormArray {
    return this.form.controls.locations;
  }

  get tablePlaceholderRows(): number {
    if (!this.totalItems) return this.pageSize;

    const remainingItems = this.totalItems - ((this.currentPage - 1) * this.pageSize);
    return Math.max(1, Math.min(this.pageSize, remainingItems));
  }

  ngOnInit(): void {
    this.loadData();
  }

  ngOnDestroy(): void {
    this.destroyLocationMap();
  }

  loadData(): void {
    this.loading = true;
    this.service.getAdminList(this.currentPage, this.pageSize, this.searchQuery, true).subscribe({
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
    this.resetEditor();
    this.addLocation();
    this.formModalOpen = true;
    this.ensureFormOptions();
  }

  edit(item: SpecimenListItem): void {
    this.resetEditor();
    this.selectedId = item.id;
    this.loadingSpecimenDetail = true;
    this.formModalOpen = true;
    this.ensureFormOptions();
    this.service.getById(item.id, true).subscribe({
      next: specimen => {
        if (this.selectedId !== item.id) return;
        this.populateEditor(specimen);
        this.loadingSpecimenDetail = false;
      },
      error: () => {
        if (this.selectedId !== item.id) return;
        this.loadingSpecimenDetail = false;
        this.resetForm();
        showError('Error', 'No se pudo cargar el detalle del espécimen.');
      }
    });
  }

  private populateEditor(item: Specimen): void {
    this.form.patchValue({
      catalog_code: item.catalog_code,
      is_published: item.is_published,
      collection_date: item.collection_date,
      collection_number: item.collection_number,
      morphological_description: item.morphological_description,
      species_id: item.species_id,
      collector_id: item.collector_id
    });
    (item.locations || []).forEach(location => {
      this.locations.push(this.createLocationGroup({
        location_id: location.location_id,
        name: location.location_name,
        latitude: location.latitude,
        longitude: location.longitude,
        location_comment: location.location_comment,
        climate_id: location.climate_id,
        habitat_id: location.habitat_id,
        comment: location.comment,
        marker_icon: location.marker_icon
      }));
    });
    if (!this.locations.length) this.addLocation();
  }

  resetForm(): void {
    this.resetEditor();
    this.formModalOpen = false;
  }

  private resetEditor(): void {
    this.destroyLocationMap();
    this.selectedId = null;
    this.currentStep = 1;
    this.activeLocationIndex = 0;
    this.saving = false;
    this.loadingSpecimenDetail = false;
    this.form.reset({ is_published: false });
    this.locations.clear();
  }

  private createLocationGroup(value: any = {}) {
    const originalLocationSignature = value.location_id
      ? this.locationSignature(value)
      : '';

    return this.fb.group({
      location_id: [value.location_id || ''],
      original_location_signature: [originalLocationSignature],
      name: [value.name || '', [Validators.required, Validators.maxLength(255), lettersSpacesValidator]],
      latitude: [String(value.latitude ?? ''), [Validators.required, Validators.pattern(COORDINATE_PATTERN), Validators.min(-90), Validators.max(90)]],
      longitude: [String(value.longitude ?? ''), [Validators.required, Validators.pattern(COORDINATE_PATTERN), Validators.min(-180), Validators.max(180)]],
      location_comment: [value.location_comment || '', noHtmlValidator],
      climate_id: [value.climate_id || ''],
      habitat_id: [value.habitat_id || ''],
      comment: [value.comment || '', noHtmlValidator],
      marker_icon: [value.marker_icon || 'plant']
    });
  }

  addLocation(): void {
    this.locations.push(this.createLocationGroup());
    this.activateLocation(this.locations.length - 1);
    setTimeout(() => {
      const list = this.locationsListElement?.nativeElement;
      list?.scrollTo({ top: list.scrollHeight, behavior: 'smooth' });
    });
  }

  removeLocation(index: number): void {
    if (this.locations.length === 1) return;
    this.locations.removeAt(index);
    this.activateLocation(Math.min(index, this.locations.length - 1));
  }

  selectMarkerIcon(index: number, markerIcon: MarkerIconType): void {
    this.locations.at(index).get('marker_icon')?.setValue(markerIcon);
    if (this.activeLocationIndex === index && this.locationMarker) {
      this.locationMarker.setIcon(plantMarkerIcon(markerIcon, false));
    }
  }

  activateLocation(index: number): void {
    this.destroyLocationMap();
    this.activeLocationIndex = index;
    if (this.currentStep === 2) setTimeout(() => this.initLocationMap());
  }

  toggleLocation(index: number): void {
    if (this.activeLocationIndex === index) {
      this.destroyLocationMap();
      this.activeLocationIndex = null;
      return;
    }
    this.activateLocation(index);
  }

  submitStep(): void {
    if (this.currentStep === 1) {
      if (this.isStepOneInvalid) {
        this.markStepOneAsTouched();
        return;
      }
      this.currentStep = 2;
      this.activateLocation(0);
      return;
    }
    this.save();
  }

  previousStep(): void {
    this.destroyLocationMap();
    this.currentStep = 1;
  }

  updateMapFromCoordinates(index: number): void {
    if (index !== this.activeLocationIndex) return;
    const group = this.locations.at(index);
    const latitude = Number(group.get('latitude')?.value);
    const longitude = Number(group.get('longitude')?.value);
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;
    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) return;
    this.setLocationMarker(latitude, longitude);
    this.locationMap?.setView([latitude, longitude], Math.max(this.locationMap.getZoom(), 13));
  }

  private initLocationMap(): void {
    if (this.locationMap || this.currentStep !== 2 || !this.locations.length || this.activeLocationIndex === null) return;
    const element = document.getElementById('specimen-location-map');
    if (!element) return;
    const group = this.locations.at(this.activeLocationIndex);
    const latitude = Number(group.get('latitude')?.value);
    const longitude = Number(group.get('longitude')?.value);
    const hasCoordinates = Number.isFinite(latitude) && Number.isFinite(longitude)
      && (latitude !== 0 || longitude !== 0);
    const initialCenter: L.LatLngExpression = hasCoordinates ? [latitude, longitude] : [-0.95, -80.35];

    this.locationMap = L.map(element, { center: initialCenter, zoom: hasCoordinates ? 14 : 8 });
    this.locationMap.attributionControl.setPrefix(false);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: "&copy; OpenStreetMap",
      maxZoom: 19
    }).addTo(this.locationMap);
    if (hasCoordinates) this.setLocationMarker(latitude, longitude);
    this.locationMap.on('click', (event: L.LeafletMouseEvent) => {
      const selectedLatitude = event.latlng.lat.toFixed(8);
      const selectedLongitude = event.latlng.lng.toFixed(8);
      group.patchValue({ latitude: selectedLatitude, longitude: selectedLongitude });
      group.get('latitude')?.markAsTouched();
      group.get('longitude')?.markAsTouched();
      this.setLocationMarker(Number(selectedLatitude), Number(selectedLongitude));
    });
    setTimeout(() => this.locationMap?.invalidateSize());
  }

  private setLocationMarker(latitude: number, longitude: number): void {
    if (!this.locationMap) return;
    const coordinates: L.LatLngExpression = [latitude, longitude];
    if (this.locationMarker) {
      this.locationMarker.setLatLng(coordinates);
      return;
    }
    const group = this.activeLocationIndex === null ? null : this.locations.at(this.activeLocationIndex);
    const markerIcon = group?.get('marker_icon')?.value || 'plant';
    this.locationMarker = L.marker(coordinates, { icon: plantMarkerIcon(markerIcon, false) }).addTo(this.locationMap);
  }

  private destroyLocationMap(): void {
    this.locationMap?.remove();
    this.locationMap = null;
    this.locationMarker = null;
  }

  get isStepOneInvalid(): boolean {
    return ['catalog_code', 'species_id'].some(name => this.form.get(name)?.invalid);
  }

  get isStepTwoInvalid(): boolean {
    return this.locations.invalid || !this.locations.length || this.hasDuplicateLocations;
  }

  get hasDuplicateLocations(): boolean {
    const coordinates = this.locations.getRawValue()
      .filter(item => item.latitude !== '' && item.longitude !== '')
      .map(item => this.coordinateKey(item.latitude, item.longitude));
    return coordinates.length !== new Set(coordinates).size;
  }

  private coordinateKey(latitude: unknown, longitude: unknown): string {
    return `${this.normalizeCoordinate(latitude)}:${this.normalizeCoordinate(longitude)}`;
  }

  private normalizeCoordinate(value: unknown): string {
    const parsedValue = Number(value);
    return Number.isFinite(parsedValue) ? parsedValue.toFixed(8) : String(value ?? '').trim();
  }

  private locationSignature(value: {
    name?: unknown;
    latitude?: unknown;
    longitude?: unknown;
    location_comment?: unknown;
  }): string {
    return JSON.stringify([
      String(value.name ?? '').trim(),
      this.normalizeCoordinate(value.latitude),
      this.normalizeCoordinate(value.longitude),
      String(value.location_comment ?? '').trim()
    ]);
  }

  private markStepOneAsTouched(): void {
    ['catalog_code', 'collection_date', 'collection_number', 'morphological_description', 'species_id', 'collector_id']
      .forEach(name => this.form.get(name)?.markAsTouched());
  }

  private save(): void {
    if (this.isStepTwoInvalid) {
      this.locations.markAllAsTouched();
      if (this.hasDuplicateLocations) showError(translateUiText('code.features.specimens.specimens.ubicaciones_duplicadas'), translateUiText('code.features.specimens.specimens.no_puedes_asociar_dos_veces_la_misma_ubicacion'));
      return;
    }
    this.saving = true;
    const payload = this.buildSpecimenPayload();
    const request = this.selectedId
      ? this.service.update(this.selectedId, payload)
      : this.service.create(payload);
    request.pipe(finalize(() => this.saving = false)).subscribe({
      next: () => this.finishSave(
        this.selectedId ? translateUiText('code.features.admin.roles.roles.actualizado') : translateUiText('code.features.admin.roles.roles.creado'),
        this.selectedId ? translateUiText('code.features.specimens.specimens.especimen_actualizado_correctamente') : translateUiText('code.features.specimens.specimens.especimen_creado_correctamente')
      ),
      error: err => showError(
        translateUiText('code.features.admin.roles.roles.error'),
        handleFormApiError(this.form, err, this.selectedId ? translateUiText('code.features.specimens.specimens.error_al_actualizar_el_especimen') : translateUiText('code.features.specimens.specimens.error_al_crear_el_especimen'))
      )
    });
  }

  private buildSpecimenPayload(): SpecimenWrite {
    const locationPayloads: SpecimenLocationWrite[] = this.locations.getRawValue().map((item, index) => ({
      ...(item.location_id && item.original_location_signature === this.locationSignature(item)
        ? { location_id: item.location_id }
        : {
            new_location: {
              name: item.name!,
              latitude: item.latitude!,
              longitude: item.longitude!,
              comment: item.location_comment || ''
            }
          }),
      climate_id: item.climate_id || null,
      habitat_id: item.habitat_id || null,
      comment: item.comment || '',
      marker_icon: item.marker_icon || 'plant',
      is_primary: index === 0,
      order: index + 1
    }));
    return {
      catalog_code: this.form.controls.catalog_code.value!,
      is_published: Boolean(this.form.controls.is_published.value),
      collection_date: this.form.controls.collection_date.value || '',
      collection_number: this.form.controls.collection_number.value || '',
      morphological_description: this.form.controls.morphological_description.value || '',
      species_id: this.form.controls.species_id.value!,
      collector_id: this.form.controls.collector_id.value || null,
      locations: locationPayloads
    };
  }

  private finishSave(title: string, message: string): void {
    showSuccess(title, message);
    this.filterOptionsService.invalidate();
    this.invalidateFormOptions();
    this.resetForm();
    this.currentPage = 1;
    this.loadData();
  }

  private ensureFormOptions(): void {
    if (this.speciesList.length || this.loadingFormOptions) return;

    this.loadingFormOptions = true;
    this.service.getFormOptions().subscribe({
      next: options => {
        this.speciesList = options.species;
        this.collectors = options.collectors;
        this.climates = options.climates;
        this.habitats = options.habitats;
        this.loadingFormOptions = false;
      },
      error: () => {
        this.loadingFormOptions = false;
        showError('Error', 'No se pudieron cargar las opciones del formulario.');
      }
    });
  }

  private invalidateFormOptions(): void {
    this.speciesList = [];
    this.collectors = [];
    this.climates = [];
    this.habitats = [];
  }

  async remove(item: SpecimenListItem): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.specimens.specimens.estas_seguro_de_eliminar_este_especimen'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: () => {
        showSuccess(translateUiText('code.features.admin.roles.roles.eliminado'), translateUiText('code.features.specimens.specimens.especimen_eliminado_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: err => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.specimens.specimens.error_al_eliminar_el_especimen'))
    });
  }
}
