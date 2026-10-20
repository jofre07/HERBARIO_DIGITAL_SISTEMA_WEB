import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import { Component, ElementRef, HostListener, OnInit, ViewChild, inject } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import {
  PaginationComponent,
  PublicBreadcrumbComponent,
  PublicFilterDrawerComponent,
  SelectInputComponent,
  SelectInputOption
} from '../../../components';
import { PublicFilterOptions } from '../../../core/interfaces/filter-options.interface';
import { Specimen } from '../../../core/interfaces/specimen.interface';
import { FilterOptionsService } from '../../../core/services/filter-options.service';
import { PublicSpecimenService } from '../../../core/services/public-specimen.service';

@Component({
  selector: 'app-advanced-search',
  standalone: true,
  imports: [UiTextPipe, 
    CommonModule,
    FormsModule,
    RouterModule,
    PublicBreadcrumbComponent,
    PublicFilterDrawerComponent,
    SelectInputComponent,
    PaginationComponent
  ],
  templateUrl: './advanced-search.component.html',
  styleUrl: './advanced-search.component.scss'
})
export class AdvancedSearchComponent implements OnInit {
  private specimenService = inject(PublicSpecimenService);
  private filterOptionsService = inject(FilterOptionsService);
  @ViewChild('resultsSection') private resultsSection?: ElementRef<HTMLElement>;

  filters = this.emptyFilters();
  filterOptions: PublicFilterOptions | null = null;
  searched = false;
  loading = false;
  filtersOpen = false;
  loadError = false;
  viewMode: 'table' | 'cards' = 'table';
  results: Specimen[] = [];
  currentPage = 1;
  pageSize = 20;
  totalResults = 0;
  private filterSnapshot = this.emptyFilters();

  ngOnInit(): void {
    this.filterOptionsService.getOptions().subscribe({
      next: options => this.filterOptions = options,
      error: () => this.filterOptions = null
    });
  }

  get familyOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptions?.families || []);
  }

  get genusOptions(): SelectInputOption[] {
    const genera = (this.filterOptions?.genera || [])
      .filter(genus => !this.filters.family || genus.family_name === this.filters.family)
      .map(genus => genus.name);
    return this.toOptions(genera);
  }

  get speciesOptions(): SelectInputOption[] {
    const species = (this.filterOptions?.species || [])
      .filter(item => !this.filters.family || item.family_name === this.filters.family)
      .filter(item => !this.filters.genus || item.genus_name === this.filters.genus)
      .map(item => item.name);
    return this.toOptions(species);
  }

  get commonNameOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptions?.common_names || []);
  }

  get collectorOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptions?.collectors || []);
  }

  get locationOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptions?.locations || []);
  }

  get conservationOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptions?.conservation_statuses || []);
  }

  get habitatOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptions?.habitats || []);
  }

  get climateOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptions?.climates || []);
  }

  get hasActiveFilters(): boolean {
    return Object.values(this.filters).some(Boolean);
  }

  get activeFilterCount(): number {
    return Object.values(this.filters).filter(Boolean).length;
  }

  openFilters(): void {
    this.filterSnapshot = { ...this.filters };
    this.filtersOpen = true;
  }

  closeFilters(): void {
    this.filters = { ...this.filterSnapshot };
    this.filtersOpen = false;
  }

  search(): void {
    const showAllRecords = !this.hasActiveFilters;
    this.searched = true;
    this.currentPage = 1;
    this.executeSearch(showAllRecords);
    this.filterSnapshot = { ...this.filters };
    this.filtersOpen = false;
  }

  @HostListener('document:keydown.enter', ['$event'])
  searchWithEnter(event: KeyboardEvent): void {
    const target = event.target as HTMLElement | null;
    if (!this.filtersOpen || target?.closest('app-select-input, button, textarea') || this.loading) return;
    event.preventDefault();
    this.search();
  }

  clearFilters(): void {
    this.filters = this.emptyFilters();
  }

  onFamilyChange(): void {
    if (!this.genusOptions.some(option => option.value === this.filters.genus)) {
      this.filters.genus = '';
    }
    this.ensureSelectedSpeciesIsAvailable();
  }

  onGenusChange(): void {
    this.ensureSelectedSpeciesIsAvailable();
  }

  goToPage(page: number): void {
    if (page === this.currentPage || page < 1) return;
    this.currentPage = page;
    this.executeSearch();
  }

  retry(): void {
    this.executeSearch();
  }

  primaryLocationName(specimen: Specimen): string {
    const location = specimen.locations.find(item => item.is_primary) || specimen.locations[0];
    return location?.location_name || translateUiText('views.public.pages.advanced_search.advanced_search.sin_registrar');
  }

  private executeSearch(forceResultsScroll = false): void {
    this.loading = true;
    this.loadError = false;
    this.specimenService.searchAdvanced({
      family_name: this.filters.family,
      genus_name: this.filters.genus,
      species_name: this.filters.species,
      common_name: this.filters.commonName,
      collector_name: this.filters.collector,
      location_name: this.filters.location,
      conservation_status: this.filters.conservationStatus,
      habitat: this.filters.habitat,
      climate: this.filters.climate,
      ordering: '-collection_date'
    }, this.currentPage, this.pageSize).subscribe({
      next: response => {
        this.results = response.results;
        this.totalResults = response.count;
        this.loading = false;
        this.revealResultsIfNeeded(forceResultsScroll);
      },
      error: () => {
        this.results = [];
        this.totalResults = 0;
        this.loadError = true;
        this.loading = false;
        this.revealResultsIfNeeded(forceResultsScroll);
      }
    });
  }

  private revealResultsIfNeeded(forceScroll = false): void {
    requestAnimationFrame(() => requestAnimationFrame(() => {
      const element = this.resultsSection?.nativeElement;
      if (!element) return;

      const rect = element.getBoundingClientRect();
      const headingRect = element.querySelector<HTMLElement>('.results-heading')?.getBoundingClientRect() || rect;
      const fixedHeaderOffset = 80;
      const viewportBottomMargin = 16;
      const headingIsFullyVisible = headingRect.top >= fixedHeaderOffset && headingRect.bottom <= window.innerHeight - viewportBottomMargin;
      const userIsAlreadyInsideResults = rect.top < fixedHeaderOffset && rect.bottom > fixedHeaderOffset;
      if (!forceScroll && (headingIsFullyVisible || userIsAlreadyInsideResults)) return;

      window.scrollTo({
        top: Math.max(0, window.scrollY + rect.top - fixedHeaderOffset),
        behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
      });
    }));
  }

  private ensureSelectedSpeciesIsAvailable(): void {
    if (!this.speciesOptions.some(option => option.value === this.filters.species)) {
      this.filters.species = '';
    }
  }

  private toOptions(values: string[]): SelectInputOption[] {
    return [...new Set(values.filter(Boolean))].map(value => ({ value, label: value }));
  }

  private emptyFilters() {
    return {
      family: '',
      genus: '',
      species: '',
      commonName: '',
      collector: '',
      location: '',
      conservationStatus: '',
      habitat: '',
      climate: ''
    };
  }
}
