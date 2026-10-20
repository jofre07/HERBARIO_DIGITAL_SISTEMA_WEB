import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, ElementRef, OnInit, OnDestroy, ViewChild, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import * as L from 'leaflet';
import { MARKER_ICON_OPTIONS, PlantMarkerSize, plantMarkerIcon } from '../../../shared/utils/map-marker';
import { LocationService, MapPointFilters } from '../../../core/services/location.service';
import { MapPoint } from '../../../core/interfaces/location.interface';
import { PublicFilterOptions } from '../../../core/interfaces/filter-options.interface';
import { FilterOptionsService } from '../../../core/services/filter-options.service';
import { PublicBreadcrumbComponent, PublicFilterDrawerComponent, SelectInputComponent, SelectInputOption } from '../../../components';
import { CountUpDirective } from '../../../shared/directives/count-up.directive';
import { translateUiText } from '../../../core/services/ui-text.service';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [UiTextPipe, CommonModule, FormsModule, RouterModule, SelectInputComponent, CountUpDirective, PublicBreadcrumbComponent, PublicFilterDrawerComponent],
  templateUrl: './map.component.html',
  styleUrl: './map.component.scss'
})
export class MapComponent implements OnInit, OnDestroy {
  private locationService = inject(LocationService);
  private filterOptionsService = inject(FilterOptionsService);
  private mapElement?: ElementRef<HTMLDivElement>;
  private map: L.Map | undefined;
  private manabiLayer: L.GeoJSON | undefined;
  private markersLayer: L.LayerGroup | undefined;
  private readonly markersByPoint = new Map<string, L.Marker>();
  private focusedMarker: L.Marker | undefined;

  @ViewChild("mapContainer")
  set mapHost(element: ElementRef<HTMLDivElement> | undefined) {
    this.mapElement = element;

    if (element) {
      setTimeout(() => this.initMap());
    }
  }

  filterSpecies = '';
  filterFamily = '';
  filterGenus = '';
  filterCommonName = '';
  filterCollector = '';
  loading = true;
  filtersOpen = false;
  markersData: MapPoint[] = [];
  filterOptionsData: PublicFilterOptions | null = null;
  readonly markerIconOptions = MARKER_ICON_OPTIONS;
  readonly resultPageSize = 5;
  currentResultPage = 1;
  private filterSnapshot = this.captureFilters();

  private readonly mapPointLimit = 1000;

  ngOnInit(): void {
    this.filterOptionsService.getOptions().subscribe({
      next: options => this.filterOptionsData = options
    });
    this.locationService.getMapPoints(1, this.mapPointLimit).subscribe({
      next: (res) => {
        this.markersData = res.results;
        this.currentResultPage = 1;
        this.renderFilteredMarkers();
        this.loading = false;
      },
      error: (error) => {
        this.loading = false;
        console.error("No fue posible cargar los puntos del mapa.", error);
      }
    });
  }

  private initMap(): void {
    if (this.map || !this.mapElement) return;

    this.map = L.map(this.mapElement.nativeElement, {
      center: [-0.95, -80.35],
      zoom: 7,
      zoomControl: true
    });
    this.map.attributionControl.setPrefix(false);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a>",
      maxZoom: 18
    }).addTo(this.map);

    this.markersLayer = L.layerGroup().addTo(this.map);
    this.map.on('zoomend', () => this.resizeMarkersForZoom());
    this.addManabiHighlight();
    this.renderFilteredMarkers();

    setTimeout(() => this.map?.invalidateSize());
  }

  private async addManabiHighlight(): Promise<void> {
    if (!this.map) return;

    try {
      const response = await fetch('/data/manabi.geojson');
      if (!response.ok) throw new Error(`No se pudo cargar el límite de Manabí (${response.status})`);

      const geoJson = await response.json();
      if (!this.map) return;

      this.manabiLayer = L.geoJSON(geoJson, {
        style: {
          color: '#c2410c',
          weight: 3,
          opacity: 0.95,
          fillColor: '#f59e0b',
          fillOpacity: 0.28
        }
      }).addTo(this.map);

      this.manabiLayer.bringToBack();
    } catch (error) {
      console.warn("No fue posible resaltar la provincia de Manabí.", error);
    }
  }

  private addMarkers(points: MapPoint[]): void {
    if (!this.markersLayer) return;
    const markerSize = this.markerSizeForZoom();
    points.forEach(m => {
      const marker = L.marker([Number(m.latitude), Number(m.longitude)], {
        icon: plantMarkerIcon(m.marker_icon, Boolean(m.is_primary), markerSize)
      }).addTo(this.markersLayer!);
      marker.bindPopup(this.createMarkerPopup(m), {
        minWidth: 220,
        maxWidth: 280
      });
      marker.on('click', () => this.highlightMarker(marker));
      this.markersByPoint.set(this.pointKey(m), marker);
    });
  }

  private markerSizeForZoom(): PlantMarkerSize {
    const zoom = this.map?.getZoom() ?? 7;
    if (zoom <= 7) return 'compact';
    if (zoom <= 9) return 'small';
    if (zoom <= 11) return 'medium';
    return 'normal';
  }

  private resizeMarkersForZoom(): void {
    const markerSize = this.markerSizeForZoom();
    const sizeClasses = [
      'plant-map-marker-container--compact',
      'plant-map-marker-container--small',
      'plant-map-marker-container--medium',
      'plant-map-marker-container--normal'
    ];

    this.markersByPoint.forEach(marker => {
      const markerElement = marker.getElement();
      if (!markerElement) return;
      markerElement.classList.remove(...sizeClasses);
      markerElement.classList.add(`plant-map-marker-container--${markerSize}`);
    });
  }

  private createMarkerPopup(point: MapPoint): HTMLElement {
    const popup = document.createElement('article');
    popup.className = 'map-point-popup';

    const species = document.createElement('h3');
    species.textContent = point.species_name;

    const catalogCode = document.createElement('p');
    catalogCode.textContent = point.catalog_code;

    const media = document.createElement('div');
    media.className = 'map-point-popup__media';
    this.renderPopupImage(media, point);

    const detailLink = document.createElement('a');
    detailLink.className = 'map-point-popup__link';
    detailLink.href = `/catalogo/${encodeURIComponent(point.species_id)}`;
    detailLink.textContent = translateUiText('actions.viewDetail');

    popup.append(species, catalogCode, media, detailLink);
    return popup;
  }

  private renderPopupImage(container: HTMLElement, point: MapPoint): void {
    const imageUrl = point.image_url?.trim();
    if (!imageUrl) {
      container.replaceChildren(this.createImagePlaceholder());
      return;
    }

    const image = document.createElement('img');
    image.src = imageUrl;
    image.alt = `Imagen de ${point.species_name}`;
    image.loading = 'lazy';
    image.decoding = 'async';
    image.addEventListener('error', () => {
      container.replaceChildren(this.createImagePlaceholder());
    }, { once: true });
    container.replaceChildren(image);
  }

  private createImagePlaceholder(): HTMLElement {
    const placeholder = document.createElement('span');
    placeholder.className = 'map-point-popup__placeholder';

    const icon = document.createElement('i');
    icon.className = 'bi bi-flower1';
    icon.setAttribute('aria-hidden', 'true');

    const label = document.createElement('small');
    label.textContent = translateUiText('views.public.pages.map.map.sin_imagen_disponible');

    placeholder.append(icon, label);
    return placeholder;
  }

  applyFilters(): void {
    this.loading = true;
    this.locationService.getMapPoints(1, this.mapPointLimit, this.backendFilters).subscribe({
      next: response => {
        this.markersData = response.results;
        this.currentResultPage = 1;
        this.renderFilteredMarkers(true);
        this.loading = false;
        this.filterSnapshot = this.captureFilters();
        this.filtersOpen = false;
      },
      error: error => {
        this.loading = false;
        console.error("No fue posible filtrar los puntos del mapa.", error);
      }
    });
  }

  onFamilyChange(): void {
    if (this.filterGenus && !this.genusList.includes(this.filterGenus)) {
      this.filterGenus = '';
    }
    if (this.filterSpecies && !this.speciesList.includes(this.filterSpecies)) {
      this.filterSpecies = '';
    }
  }

  onGenusChange(): void {
    if (this.filterSpecies && !this.speciesList.includes(this.filterSpecies)) {
      this.filterSpecies = '';
    }
  }

  openFilters(): void {
    this.filterSnapshot = this.captureFilters();
    this.filtersOpen = true;
  }

  closeFilters(): void {
    this.restoreFilters(this.filterSnapshot);
    this.filtersOpen = false;
  }

  clearFilters(): void {
    this.filterFamily = '';
    this.filterGenus = '';
    this.filterSpecies = '';
    this.filterCommonName = '';
    this.filterCollector = '';
  }

  get hasActiveFilters(): boolean {
    return Boolean(
      this.filterFamily || this.filterGenus || this.filterSpecies ||
      this.filterCommonName || this.filterCollector
    );
  }

  get activeFilterCount(): number {
    return [this.filterFamily, this.filterGenus, this.filterSpecies,
      this.filterCommonName, this.filterCollector].filter(Boolean).length;
  }

  private captureFilters() {
    return {
      filterFamily: this.filterFamily,
      filterGenus: this.filterGenus,
      filterSpecies: this.filterSpecies,
      filterCommonName: this.filterCommonName,
      filterCollector: this.filterCollector
    };
  }

  private restoreFilters(filters: ReturnType<MapComponent['captureFilters']>): void {
    Object.assign(this, filters);
  }

  get filteredMapPoints(): MapPoint[] {
    return this.markersData.filter(point =>
      Number.isFinite(Number(point.latitude)) && Number.isFinite(Number(point.longitude))
    );
  }

  get totalResultPages(): number {
    return Math.max(1, Math.ceil(this.filteredMapPoints.length / this.resultPageSize));
  }

  get paginatedMapPoints(): MapPoint[] {
    const start = (this.currentResultPage - 1) * this.resultPageSize;
    return this.filteredMapPoints.slice(start, start + this.resultPageSize);
  }

  goToResultPage(page: number): void {
    if (page < 1 || page > this.totalResultPages || page === this.currentResultPage) return;
    this.currentResultPage = page;
  }

  get visibleStats(): { locations: number; specimens: number; species: number; collectors: number } {
    const points = this.filteredMapPoints;
    return {
      locations: new Set(points.map(point => `${point.location_name}|${point.latitude}|${point.longitude}`)).size,
      specimens: new Set(points.map(point => point.id)).size,
      species: new Set(points.map(point => point.species_id)).size,
      collectors: new Set(points.map(point => point.collector_name).filter(Boolean)).size
    };
  }

  get familyList(): string[] {
    return this.filterOptionsData?.families || [];
  }

  get genusList(): string[] {
    return this.uniqueSorted(
      (this.filterOptionsData?.genera || [])
        .filter(item => !this.filterFamily || item.family_name === this.filterFamily)
        .map(item => item.name)
    );
  }

  get speciesList(): string[] {
    return this.uniqueSorted(
      (this.filterOptionsData?.species || [])
        .filter(item => !this.filterFamily || item.family_name === this.filterFamily)
        .filter(item => !this.filterGenus || item.genus_name === this.filterGenus)
        .map(item => item.name)
    );
  }

  get commonNameList(): string[] {
    return this.filterOptionsData?.common_names || [];
  }

  get collectorList(): string[] {
    return this.filterOptionsData?.collectors || [];
  }

  get familyOptions(): SelectInputOption[] {
    return this.toSelectOptions(this.familyList);
  }

  get genusOptions(): SelectInputOption[] {
    return this.toSelectOptions(this.genusList);
  }

  get speciesOptions(): SelectInputOption[] {
    return this.toSelectOptions(this.speciesList);
  }

  get commonNameOptions(): SelectInputOption[] {
    return this.toSelectOptions(this.commonNameList);
  }

  get collectorOptions(): SelectInputOption[] {
    return this.toSelectOptions(this.collectorList);
  }

  private toSelectOptions(values: string[]): SelectInputOption[] {
    return values.map(value => ({ value, label: value }));
  }

  private get backendFilters(): MapPointFilters {
    return {
      family_name: this.filterFamily,
      genus_name: this.filterGenus,
      species_name: this.filterSpecies,
      common_name: this.filterCommonName,
      collector_name: this.filterCollector
    };
  }

  private uniqueSorted(values: Array<string | null | undefined>): string[] {
    return [...new Set(values.filter((value): value is string => Boolean(value)))].sort((a, b) =>
      a.localeCompare(b, 'es', { sensitivity: 'base' })
    );
  }

  private renderFilteredMarkers(focusResults = false): void {
    if (!this.markersLayer) return;

    this.markersLayer.clearLayers();
    this.markersByPoint.clear();
    this.focusedMarker = undefined;

    const validPoints = this.filteredMapPoints;

    this.addMarkers(validPoints);
    if (focusResults) {
      this.focusResults(validPoints);
    }
  }

  focusPoint(point: MapPoint): void {
    if (!this.map) return;
    const coordinates = L.latLng(Number(point.latitude), Number(point.longitude));
    this.map.stop();
    this.map.setView(coordinates, 13, { animate: false });

    const marker = this.markersByPoint.get(this.pointKey(point));
    if (!marker) return;

    this.highlightMarker(marker);
    marker.openPopup();
    this.map.panTo(coordinates, { animate: false });
  }

  private pointKey(point: MapPoint): string {
    return `${point.id}|${point.latitude}|${point.longitude}`;
  }

  private highlightMarker(marker: L.Marker): void {
    if (this.focusedMarker && this.focusedMarker !== marker) {
      this.focusedMarker.setZIndexOffset(0);
    }
    marker.setZIndexOffset(1000);
    this.focusedMarker = marker;
  }

  private focusResults(points: MapPoint[]): void {
    if (!this.map || points.length === 0) return;

    const coordinates = points.map(point =>
      L.latLng(Number(point.latitude), Number(point.longitude))
    );

    if (coordinates.length === 1) {
      this.map.setView(coordinates[0], 11);
      return;
    }

    this.map.fitBounds(L.latLngBounds(coordinates), {
      padding: [40, 40],
      maxZoom: 11
    });
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
      this.map = undefined;
    }
    this.markersLayer = undefined;
    this.manabiLayer = undefined;
    this.markersByPoint.clear();
    this.focusedMarker = undefined;
  }
}
