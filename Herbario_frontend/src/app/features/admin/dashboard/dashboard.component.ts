import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { StatsService } from '../../../core/services/stats.service';
import { DashboardChartPoint, HerbariumStats } from '../../../core/interfaces/dashboard.interface';
import { SpecimenService } from '../../../core/services/specimen.service';
import { Specimen, SpecimenLocation } from '../../../core/interfaces/specimen.interface';
import { catchError, forkJoin, of } from 'rxjs';
import * as L from 'leaflet';
import { MARKER_ICON_OPTIONS, plantMarkerIcon } from '../../../shared/utils/map-marker';
import { CountUpDirective } from '../../../shared/directives/count-up.directive';

interface DashboardMapPoint {
  specimen: Specimen;
  location: SpecimenLocation | null;
  latitude: number;
  longitude: number;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [UiTextPipe, CommonModule, CountUpDirective],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit, OnDestroy {
  private statsService = inject(StatsService);
  private specimenService = inject(SpecimenService);
  private specimensMap: L.Map | null = null;
  private specimensMapElement?: ElementRef<HTMLDivElement>;

  @ViewChild("specimensMap")
  set specimensMapHost(element: ElementRef<HTMLDivElement> | undefined) {
    this.specimensMapElement = element;
    if (element) setTimeout(() => this.initializeMap());
  }

  stats: HerbariumStats | null = null;
  specimens: Specimen[] = [];
  loading = false;
  loadError = false;

  readonly chartColors = ['#238636', '#4aa85a', '#79c181', '#a8d8ad', '#d1ead4', '#84a98c'];
  readonly markerIconOptions = MARKER_ICON_OPTIONS;
  readonly statusNames: Record<string, string> = {
    EX: "Extinto",
    EW: "Extinto en estado silvestre",
    CR: "Peligro crítico",
    EN: "En peligro",
    VU: "Vulnerable",
    NT: "Casi amenazado",
    LC: "Preocupación menor",
    DD: "Datos insuficientes",
    NE: "No evaluado"
  };

  ngOnInit(): void {
    this.loadDashboard();
  }

  ngOnDestroy(): void {
    this.destroyMap();
  }

  loadDashboard(): void {
    this.loading = true;
    this.loadError = false;

    forkJoin({
      stats: this.statsService.getStats(true).pipe(catchError(() => of(null))),
      specimens: this.specimenService.getAll(1, 100).pipe(catchError(() => of(null)))
    }).subscribe({
      next: ({ stats, specimens }) => {
        this.stats = stats;
        this.specimens = specimens?.results || [];
        this.loadError = !stats;
        this.loading = false;
      },
      error: () => {
        this.loadError = true;
        this.loading = false;
      }
    });
  }

  get mapPoints(): DashboardMapPoint[] {
    return this.specimens.flatMap<DashboardMapPoint>(specimen => {
      const locationPoints: DashboardMapPoint[] = (specimen.locations || [])
        .map(location => ({
          specimen,
          location,
          latitude: Number(location.latitude),
          longitude: Number(location.longitude)
        }))
        .filter(point => Number.isFinite(point.latitude) && Number.isFinite(point.longitude));

      if (locationPoints.length) return locationPoints;

      const latitude = Number(specimen.latitude);
      const longitude = Number(specimen.longitude);
      return Number.isFinite(latitude) && Number.isFinite(longitude)
        ? [{ specimen, location: null, latitude, longitude }]
        : [];
    });
  }

  get maxFamilyValue(): number {
    return this.maxChartValue(this.stats?.charts.specimens_by_family);
  }

  get maxYearValue(): number {
    return this.maxChartValue(this.stats?.charts.specimens_by_year);
  }

  get conservationTotal(): number {
    return (this.stats?.charts.species_by_conservation_status || [])
      .reduce((total, item) => total + item.value, 0);
  }

  get conservationGradient(): string {
    const points = this.stats?.charts.species_by_conservation_status || [];
    const total = this.conservationTotal;
    if (!points.length || !total) return 'conic-gradient(#e7ece8 0 100%)';

    let cursor = 0;
    const segments = points.map((point, index) => {
      const start = cursor;
      cursor += (point.value / total) * 100;
      return `${this.chartColor(index)} ${start}% ${cursor}%`;
    });
    return `conic-gradient(${segments.join(', ')})`;
  }

  familyBarWidth(point: DashboardChartPoint): number {
    return this.percentage(point.value, this.maxFamilyValue);
  }

  yearBarHeight(point: DashboardChartPoint): number {
    return Math.max(8, this.percentage(point.value, this.maxYearValue));
  }

  chartColor(index: number): string {
    return this.chartColors[index % this.chartColors.length];
  }

  statusName(code: string): string {
    return this.statusNames[code] || code;
  }

  private percentage(value: number, maximum: number): number {
    return maximum ? Math.round((value / maximum) * 100) : 0;
  }

  private maxChartValue(points?: DashboardChartPoint[]): number {
    return Math.max(0, ...(points || []).map(point => point.value));
  }

  private initializeMap(): void {
    this.destroyMap();
    const element = this.specimensMapElement?.nativeElement;
    if (!element) return;

    this.specimensMap = L.map(element, {
      center: [-1.45, -78.35],
      zoom: 6,
      scrollWheelZoom: true
    });
    this.specimensMap.attributionControl.setPrefix(false);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap"
    }).addTo(this.specimensMap);

    void this.addManabiHighlight(this.specimensMap);

    const bounds: L.LatLngExpression[] = [];
    for (const point of this.mapPoints) {
      const specimen = point.specimen;
      const coordinates: L.LatLngExpression = [point.latitude, point.longitude];
      bounds.push(coordinates);

      const popup = document.createElement('div');
      const code = document.createElement('strong');
      const species = document.createElement('div');
      const location = document.createElement('div');
      const collector = document.createElement('small');
      code.textContent = specimen.catalog_code;
      species.textContent = specimen.species_name || translateUiText('views.public.pages.advanced_search.advanced_search.especie_no_registrada');
      location.textContent = point.location?.location_name
        ? translateUiText('dynamic.map.location', {
            name: point.location.location_name,
            primary: point.location.is_primary ? translateUiText('code.features.admin.dashboard.dashboard.principal') : ''
          })
        : translateUiText('views.public.pages.catalog_detail.catalog_detail.ubicacion_sin_nombre');
      collector.textContent = specimen.collector_name
        ? translateUiText('dynamic.map.collector', { name: specimen.collector_name })
        : translateUiText('views.public.pages.map.map.colector_no_registrado');
      popup.append(code, species, location, collector);

      L.marker(coordinates, {
        icon: plantMarkerIcon(point.location?.marker_icon, point.location?.is_primary ?? true)
      })
        .bindPopup(popup)
        .addTo(this.specimensMap);
    }

    if (bounds.length) {
      this.specimensMap.fitBounds(L.latLngBounds(bounds), {
        padding: [35, 35],
        maxZoom: 13
      });
    }

    setTimeout(() => this.specimensMap?.invalidateSize());
  }

  private async addManabiHighlight(map: L.Map): Promise<void> {
    try {
      const response = await fetch('/data/manabi.geojson');
      if (!response.ok) {
        throw new Error(`No se pudo cargar el límite de Manabí (${response.status})`);
      }

      const geoJson = await response.json();
      if (this.specimensMap !== map) return;

      L.geoJSON(geoJson, {
        style: {
          color: '#c2410c',
          weight: 3,
          opacity: 0.95,
          fillColor: '#f59e0b',
          fillOpacity: 0.28
        }
      }).addTo(map).bringToBack();
    } catch (error) {
      console.warn("No fue posible resaltar la provincia de Manabí.", error);
    }
  }

  private destroyMap(): void {
    this.specimensMap?.remove();
    this.specimensMap = null;
  }
}
