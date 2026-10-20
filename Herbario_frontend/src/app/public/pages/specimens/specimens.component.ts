import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import { Component, ElementRef, inject, OnDestroy, OnInit, ViewChild } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ActivatedRoute, RouterModule } from "@angular/router";
import * as L from 'leaflet';
import { ImageLightboxComponent, LightboxImage, ModalComponent, PublicBreadcrumbComponent, PublicFilterDrawerComponent, SelectInputComponent, SelectInputOption } from '../../../components';
import { HerbariumStats } from '../../../core/interfaces/dashboard.interface';
import { PublicFilterOptions } from '../../../core/interfaces/filter-options.interface';
import { Specimen, SpecimenLocation } from '../../../core/interfaces/specimen.interface';
import { SpecimenFilters } from '../../../core/services/specimen.service';
import { PublicSpecimenService } from '../../../core/services/public-specimen.service';
import { StatsService } from '../../../core/services/stats.service';
import { FilterOptionsService } from '../../../core/services/filter-options.service';
import { plantMarkerIcon } from '../../../shared/utils/map-marker';
import { CountUpDirective } from '../../../shared/directives/count-up.directive';
import { SiteContentService } from '../../../core/services/site-content.service';

@Component({
  selector: 'app-public-specimens',
  standalone: true,
  imports: [UiTextPipe, CommonModule, RouterModule, FormsModule, ModalComponent, CountUpDirective, PublicBreadcrumbComponent, PublicFilterDrawerComponent, ImageLightboxComponent, SelectInputComponent],
  templateUrl: './specimens.component.html',
  styleUrl: './specimens.component.scss'
})
export class PublicSpecimensComponent implements OnInit, OnDestroy {
  private specimenService = inject(PublicSpecimenService);
  private statsService = inject(StatsService);
  private route = inject(ActivatedRoute);
  private filterOptionsService = inject(FilterOptionsService);
  private siteContentService = inject(SiteContentService);
  private detailMap: L.Map | null = null;

  @ViewChild("detailMap") private detailMapElement?: ElementRef<HTMLDivElement>;
  @ViewChild("resultsCard") private resultsCardElement?: ElementRef<HTMLDivElement>;

  searchQuery = '';
  selectedSpecies = '';
  selectedFamily = '';
  selectedGenus = '';
  selectedCollector = '';
  selectedLocation = '';
  selectedHabitat = '';
  selectedStatus = '';
  selectedSort = '-collection_date';
  viewMode: 'table' | 'grid' = 'table';
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  loading = false;
  filtersOpen = false;
  loadError = false;
  aboutImageUrl: string | null = null;

  speciesFilter: string[] = [];
  collectors: string[] = [];
  families: string[] = [];
  genera: string[] = [];
  locations: string[] = [];
  habitats: string[] = [];
  statuses: string[] = [];
  allItems: Specimen[] = [];
  filterOptionsData: PublicFilterOptions | null = null;
  collectionFilter = '';
  selectedItem: Specimen | null = null;
  galleryItem: Specimen | null = null;
  galleryIndex = 0;
  private searchTimer?: ReturnType<typeof setTimeout>;
  private scrollAfterPageChange = false;
  private filterSnapshot = this.captureFilters();
  stats: HerbariumStats = {
    species: 0,
    specimens: 0,
    families: 0,
    genera: 0,
    images: 0,
    collectors: 0,
    locations: 0,
    collections: 0,
    users: 0,
    charts: {
      specimens_by_family: [],
      specimens_by_year: [],
      species_by_conservation_status: []
    }
  };

  ngOnInit(): void {
    this.siteContentService.getPublicAboutContent().subscribe({
      next: content => { this.aboutImageUrl = content.introduction_image_url; },
      error: () => { this.aboutImageUrl = null; }
    });
    this.collectionFilter = this.route.snapshot.queryParamMap.get('collection') || '';
    this.loadFilterOptions();
    this.loadData();
    this.statsService.getStats().subscribe({
      next: stats => this.stats = stats
    });
  }

  private loadFilterOptions(): void {
    this.filterOptionsService.getOptions().subscribe({
      next: options => {
        this.filterOptionsData = options;
        this.speciesFilter = options.species.map(item => item.name);
        this.collectors = options.collectors;
        this.families = options.families;
        this.genera = options.genera.map(item => item.name);
        this.locations = options.locations;
        this.habitats = options.habitats;
        this.statuses = options.conservation_statuses;
      }
    });
  }

  ngOnDestroy(): void {
    this.destroyDetailMap();
    if (this.searchTimer) clearTimeout(this.searchTimer);
  }

  private loadData(): void {
    this.loading = true;
    this.loadError = false;
    this.specimenService.getAll(this.currentPage, this.pageSize, '', this.backendFilters).subscribe({
      next: (res) => {
        this.allItems = res.results.map(item => ({
          ...item,
          locations: item.locations || [],
          image_urls: item.image_urls || [],
          image_count: item.image_count || 0,
          conservation_status: item.conservation_status || null
        }));
        this.totalItems = res.count;
        this.loading = false;
        if (this.scrollAfterPageChange) this.scrollToResults();
      },
      error: () => {
        this.allItems = [];
        this.totalItems = 0;
        this.loadError = true;
        this.loading = false;
        if (this.scrollAfterPageChange) this.scrollToResults();
      }
    });
  }

  get filteredItems(): Specimen[] {
    return this.allItems;
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.pageSize) || 1;
  }

  get paginatedItems(): Specimen[] {
    return this.allItems;
  }

  get pages(): number[] {
    const start = Math.max(1, this.currentPage - 2);
    const end = Math.min(this.totalPages, this.currentPage + 2);
    const visible: number[] = [];
    for (let page = start; page <= end; page++) visible.push(page);
    return visible;
  }

  get filteredGenera(): string[] {
    const genera = this.filterOptionsData?.genera || [];
    return this.uniqueSorted(
      genera
        .filter(item => !this.selectedFamily || item.family_name === this.selectedFamily)
        .map(item => item.name)
    );
  }

  get familyOptions(): SelectInputOption[] { return this.toSelectOptions(this.families); }
  get genusOptions(): SelectInputOption[] { return this.toSelectOptions(this.filteredGenera); }
  get speciesOptions(): SelectInputOption[] { return this.toSelectOptions(this.speciesFilter); }
  get collectorOptions(): SelectInputOption[] { return this.toSelectOptions(this.collectors); }
  get locationOptions(): SelectInputOption[] { return this.toSelectOptions(this.locations); }
  get habitatOptions(): SelectInputOption[] { return this.toSelectOptions(this.habitats); }
  get statusOptions(): SelectInputOption[] { return this.toSelectOptions(this.statuses); }
  get sortOptions(): SelectInputOption[] {
    return [
      { value: '-collection_date', label: translateUiText('views.public.pages.specimens.specimens.fecha_de_coleccion_mas_reciente') },
      { value: 'collection_date', label: translateUiText('views.public.pages.specimens.specimens.fecha_de_coleccion_mas_antigua') },
      { value: 'catalog_code', label: translateUiText('views.public.pages.gallery.gallery.codigo_de_catalogo') },
      { value: 'species', label: translateUiText('views.features.specimens.specimens.especie') }
    ];
  }

  private toSelectOptions(values: string[]): SelectInputOption[] {
    return values.map(value => ({ value, label: value }));
  }

  get hasActiveFilters(): boolean {
    return Boolean(
      this.searchQuery || this.selectedSpecies || this.selectedFamily || this.selectedGenus ||
      this.selectedCollector || this.selectedLocation || this.selectedHabitat ||
      this.selectedStatus || this.collectionFilter
    );
  }

  get activeFilterCount(): number {
    return [this.searchQuery, this.selectedSpecies, this.selectedFamily, this.selectedGenus,
      this.selectedCollector, this.selectedLocation, this.selectedHabitat, this.selectedStatus,
      this.collectionFilter].filter(Boolean).length;
  }

  retry(): void {
    this.loadData();
  }

  get resultStart(): number {
    return this.totalItems ? (this.currentPage - 1) * this.pageSize + 1 : 0;
  }

  get resultEnd(): number {
    return Math.min(this.currentPage * this.pageSize, this.totalItems);
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.scrollAfterPageChange = true;
      this.loadData();
    }
  }

  private scrollToResults(): void {
    this.scrollAfterPageChange = false;
    requestAnimationFrame(() => {
      const element = this.resultsCardElement?.nativeElement;
      if (!element) return;
      const headerOffset = 80;
      const top = window.scrollY + element.getBoundingClientRect().top - headerOffset;
      window.scrollTo({
        top: Math.max(0, top),
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
      });
    });
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadData();
  }

  onSearchInput(): void {}

  onFamilyChange(): void {
    if (this.selectedGenus && !this.filteredGenera.includes(this.selectedGenus)) {
      this.selectedGenus = '';
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

  applyDrawerFilters(): void {
    this.currentPage = 1;
    this.loadData();
    this.filterSnapshot = this.captureFilters();
    this.filtersOpen = false;
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.selectedSpecies = '';
    this.selectedFamily = '';
    this.selectedGenus = '';
    this.selectedCollector = '';
    this.selectedLocation = '';
    this.selectedHabitat = '';
    this.selectedStatus = '';
    this.collectionFilter = '';
  }

  private captureFilters() {
    return {
      searchQuery: this.searchQuery,
      selectedSpecies: this.selectedSpecies,
      selectedFamily: this.selectedFamily,
      selectedGenus: this.selectedGenus,
      selectedCollector: this.selectedCollector,
      selectedLocation: this.selectedLocation,
      selectedHabitat: this.selectedHabitat,
      selectedStatus: this.selectedStatus,
      collectionFilter: this.collectionFilter
    };
  }

  private restoreFilters(filters: ReturnType<PublicSpecimensComponent['captureFilters']>): void {
    Object.assign(this, filters);
  }

  private get backendFilters(): SpecimenFilters {
    return {
      q: this.searchQuery,
      species_name: this.selectedSpecies,
      family_name: this.selectedFamily,
      genus_name: this.selectedGenus,
      collector_name: this.selectedCollector,
      location_name: this.selectedLocation,
      habitat: this.selectedHabitat,
      conservation_status: this.selectedStatus,
      collection: this.collectionFilter,
      ordering: this.selectedSort === 'species' ? 'species__name' : this.selectedSort
    };
  }

  primaryLocation(item: Specimen): SpecimenLocation | null {
    return item.locations.find(location => location.is_primary) || item.locations[0] || null;
  }

  openDetails(item: Specimen): void {
    this.selectedItem = item;
    setTimeout(() => this.initializeDetailMap());
  }

  closeDetails(): void {
    this.destroyDetailMap();
    this.selectedItem = null;
  }

  openImages(item: Specimen): void {
    if (!item.image_urls.length) return;
    this.galleryItem = item;
    this.galleryIndex = 0;
  }

  closeImages(): void {
    this.galleryItem = null;
    this.galleryIndex = 0;
  }

  get specimenLightboxImages(): LightboxImage[] {
    if (!this.galleryItem) return [];
    return this.galleryItem.image_urls.map((url, index) => ({
      url,
      alt: `Fotografía ${index + 1} del espécimen ${this.galleryItem?.catalog_code}`,
      title: this.galleryItem?.species_name || this.galleryItem?.catalog_code,
      subtitle: [this.galleryItem?.catalog_code, this.galleryItem?.family_name].filter(Boolean).join(' · ')
    }));
  }

  private initializeDetailMap(): void {
    this.destroyDetailMap();

    const item = this.selectedItem;
    const mapElement = this.detailMapElement?.nativeElement;
    if (!item || !mapElement) return;
    const locations = item.locations.filter(location =>
      Number.isFinite(Number(location.latitude)) && Number.isFinite(Number(location.longitude))
    );
    if (!locations.length) return;
    const primary = locations.find(location => location.is_primary) || locations[0];
    const latitude = Number(primary.latitude);
    const longitude = Number(primary.longitude);

    this.detailMap = L.map(mapElement, {
      center: [latitude, longitude],
      zoom: 14,
      scrollWheelZoom: false
    });
    this.detailMap.attributionControl.setPrefix(false);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap"
    }).addTo(this.detailMap);

    const bounds: L.LatLngExpression[] = [];
    locations.forEach(location => {
      const coordinates: L.LatLngExpression = [Number(location.latitude), Number(location.longitude)];
      bounds.push(coordinates);
      L.marker(coordinates, { icon: plantMarkerIcon(location.marker_icon, location.is_primary) })
        .bindPopup(`<strong>${location.location_name}</strong>${location.is_primary ? translateUiText('code.public.pages.specimens.specimens.br_principal') : ''}`)
        .addTo(this.detailMap!);
    });
    if (bounds.length > 1) {
      this.detailMap.fitBounds(L.latLngBounds(bounds), { padding: [24, 24], maxZoom: 15 });
    }

    setTimeout(() => this.detailMap?.invalidateSize());
  }

  private destroyDetailMap(): void {
    this.detailMap?.remove();
    this.detailMap = null;
  }

  private uniqueSorted(values: Array<string | null | undefined>): string[] {
    return [...new Set(values.filter((value): value is string => Boolean(value)))].sort((a, b) =>
      a.localeCompare(b, 'es')
    );
  }

}
