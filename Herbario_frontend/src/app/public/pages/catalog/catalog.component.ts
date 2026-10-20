import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, HostListener, inject, OnDestroy, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { ActivatedRoute, RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { CatalogFilters, SpeciesService } from '../../../core/services/species.service';
import { SpeciesCatalog } from '../../../core/interfaces/species.interface';
import { PublicFilterOptions } from '../../../core/interfaces/filter-options.interface';
import { FilterOptionsService } from '../../../core/services/filter-options.service';
import { CountUpDirective } from '../../../shared/directives/count-up.directive';
import { PublicBreadcrumbComponent, PublicFilterDrawerComponent, SelectInputComponent, SelectInputOption } from '../../../components';
import { translateUiText } from '../../../core/services/ui-text.service';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [UiTextPipe, CommonModule, RouterModule, FormsModule, CountUpDirective, PublicBreadcrumbComponent, PublicFilterDrawerComponent, SelectInputComponent],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.scss'
})
export class CatalogComponent implements OnInit, OnDestroy {
  private speciesService = inject(SpeciesService);
  private route = inject(ActivatedRoute);
  private filterOptionsService = inject(FilterOptionsService);

  searchQuery = '';
  commonNameQuery = '';
  selectedFamily = '';
  selectedGenus = '';
  selectedStatus = '';
  selectedLocation = '';
  selectedClimate = '';
  selectedHabitat = '';
  selectedSort = 'name';
  viewMode: 'grid' | 'list' = 'grid';
  currentPage = 1;
  pageSize = 12;
  totalItems = 0;
  loading = false;
  mobileFiltersOpen = false;

  families: string[] = [];
  genera: string[] = [];
  statuses: string[] = [];
  locations: string[] = [];
  climates: string[] = [];
  habitats: string[] = [];
  allItems: SpeciesCatalog[] = [];
  filterOptionsData: PublicFilterOptions | null = null;
  private searchTimer?: ReturnType<typeof setTimeout>;
  private filterSnapshot = this.captureFilters();

  ngOnInit(): void {
    const params = this.route.snapshot.queryParamMap;
    this.searchQuery = params.get('q') || '';
    this.selectedFamily = params.get('family') || '';
    this.selectedGenus = params.get('genus') || '';
    this.selectedStatus = params.get('status') || '';
    this.loadFilterOptions();
    this.loadData();
  }

  ngOnDestroy(): void {
    if (this.searchTimer) clearTimeout(this.searchTimer);
    document.body.classList.remove('mobile-filters-open');
  }

  private loadFilterOptions(): void {
    this.filterOptionsService.getOptions().subscribe({
      next: options => {
        this.filterOptionsData = options;
        this.families = options.families;
        this.genera = options.genera.map(item => item.name);
        this.statuses = options.conservation_statuses;
        this.locations = options.locations;
        this.climates = options.climates;
        this.habitats = options.habitats;
      }
    });
  }

  private loadData(): void {
    this.loading = true;
    this.speciesService.getCatalog(this.currentPage, this.pageSize, this.backendFilters).subscribe({
      next: (res) => {
        this.allItems = res.results.map(item => ({
          ...item,
          specimen_count: item.specimen_count || 0,
          location_names: item.location_names || [],
          climates: item.climates || [],
          habitats: item.habitats || []
        }));
        this.totalItems = res.count;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  get filteredItems(): SpeciesCatalog[] {
    return this.allItems;
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.pageSize) || 1;
  }

  get paginatedItems(): SpeciesCatalog[] {
    return this.allItems;
  }

  get pages(): number[] {
    const total = this.totalPages;
    const current = this.currentPage;
    const visible: number[] = [];
    const start = Math.max(1, current - 2);
    const end = Math.min(total, current + 2);
    for (let i = start; i <= end; i++) visible.push(i);
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
  get statusOptions(): SelectInputOption[] { return this.toSelectOptions(this.statuses); }
  get locationOptions(): SelectInputOption[] { return this.toSelectOptions(this.locations); }
  get climateOptions(): SelectInputOption[] { return this.toSelectOptions(this.climates); }
  get habitatOptions(): SelectInputOption[] { return this.toSelectOptions(this.habitats); }
  get sortOptions(): SelectInputOption[] {
    return [
      { value: 'name', label: translateUiText('views.public.pages.catalog.catalog.nombre_cientifico_a_z') },
      { value: '-name', label: translateUiText('views.public.pages.catalog.catalog.nombre_cientifico_z_a') },
      { value: 'family', label: translateUiText('views.public.pages.catalog.catalog.familia_a_z') },
      { value: 'date', label: translateUiText('views.public.pages.catalog.catalog.registro_reciente') }
    ];
  }

  private toSelectOptions(values: string[]): SelectInputOption[] {
    return values.map(value => ({ value, label: value }));
  }

  get hasActiveFilters(): boolean {
    return Boolean(
      this.searchQuery || this.commonNameQuery || this.selectedFamily || this.selectedGenus ||
      this.selectedStatus || this.selectedLocation || this.selectedClimate || this.selectedHabitat
    );
  }

  get activeFilterCount(): number {
    return [this.searchQuery, this.commonNameQuery, this.selectedFamily, this.selectedGenus,
      this.selectedStatus, this.selectedLocation, this.selectedClimate, this.selectedHabitat]
      .filter(Boolean).length;
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
      this.loadData();
    }
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadData();
  }

  openMobileFilters(): void {
    this.filterSnapshot = this.captureFilters();
    this.mobileFiltersOpen = true;
  }

  closeMobileFilters(): void {
    this.restoreFilters(this.filterSnapshot);
    this.mobileFiltersOpen = false;
  }

  applyMobileFilters(): void {
    this.currentPage = 1;
    this.loadData();
    this.filterSnapshot = this.captureFilters();
    this.mobileFiltersOpen = false;
  }

  @HostListener('document:keydown.escape')
  closeFiltersWithEscape(): void {
    if (this.mobileFiltersOpen) this.closeMobileFilters();
  }

  onSearchInput(): void {
    // La consulta se ejecuta una sola vez al confirmar el drawer.
  }

  onFamilyChange(): void {
    if (this.selectedGenus && !this.filteredGenera.includes(this.selectedGenus)) {
      this.selectedGenus = '';
    }
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.commonNameQuery = '';
    this.selectedFamily = '';
    this.selectedGenus = '';
    this.selectedStatus = '';
    this.selectedLocation = '';
    this.selectedClimate = '';
    this.selectedHabitat = '';
  }

  private captureFilters() {
    return {
      searchQuery: this.searchQuery,
      commonNameQuery: this.commonNameQuery,
      selectedFamily: this.selectedFamily,
      selectedGenus: this.selectedGenus,
      selectedStatus: this.selectedStatus,
      selectedLocation: this.selectedLocation,
      selectedClimate: this.selectedClimate,
      selectedHabitat: this.selectedHabitat
    };
  }

  private restoreFilters(filters: ReturnType<CatalogComponent['captureFilters']>): void {
    Object.assign(this, filters);
  }

  private get backendFilters(): CatalogFilters {
    const orderingMap: Record<string, string> = {
      name: 'name',
      '-name': '-name',
      family: 'genus__family__name',
      date: '-created_at'
    };
    return {
      q: this.searchQuery,
      common_name: this.commonNameQuery,
      family_name: this.selectedFamily,
      genus_name: this.selectedGenus,
      conservation_status: this.selectedStatus,
      location_name: this.selectedLocation,
      climate: this.selectedClimate,
      habitat: this.selectedHabitat,
      ordering: orderingMap[this.selectedSort] || 'name'
    };
  }

  private uniqueSorted(values: string[]): string[] {
    return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es'));
  }

}
