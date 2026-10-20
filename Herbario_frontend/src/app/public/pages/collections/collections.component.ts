import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import { Component, OnInit, inject } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { PublicBreadcrumbComponent, PublicFilterDrawerComponent, SelectInputComponent, SelectInputOption } from '../../../components';
import { Collection, CollectionType } from '../../../core/interfaces/collection.interface';
import { HerbariumStats } from '../../../core/interfaces/dashboard.interface';
import { PublicFilterOptions } from '../../../core/interfaces/filter-options.interface';
import { CollectionFilters, CollectionService } from '../../../core/services/collection.service';
import { FilterOptionsService } from '../../../core/services/filter-options.service';
import { StatsService } from '../../../core/services/stats.service';
import { CountUpDirective } from '../../../shared/directives/count-up.directive';

interface CollectionCategory {
  value: CollectionType | '';
  label: string;
  icon: string;
  count: number;
}

@Component({
  selector: 'app-collections',
  standalone: true,
  imports: [UiTextPipe, CommonModule, FormsModule, RouterModule, SelectInputComponent, CountUpDirective, PublicBreadcrumbComponent, PublicFilterDrawerComponent],
  templateUrl: './collections.component.html',
  styleUrl: './collections.component.scss'
})
export class CollectionsComponent implements OnInit {
  private collectionService = inject(CollectionService);
  private statsService = inject(StatsService);
  private filterOptionsService = inject(FilterOptionsService);

  loading = false;
  filtersOpen = false;
  collections: Collection[] = [];
  filterOptionsData: PublicFilterOptions | null = null;
  currentPage = 1;
  pageSize = 12;
  totalItems = 0;
  selectedCategory: CollectionType | '' = '';
  selectedStatus = '';
  selectedFamily = '';
  selectedLocation = '';
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
    charts: { specimens_by_family: [], specimens_by_year: [], species_by_conservation_status: [] }
  };

  readonly categoryDefinitions: Array<Omit<CollectionCategory, 'count'>> = [
    { value: '', label: translateUiText('code.public.pages.collections.collections.todas_las_colecciones'), icon: 'bi-collection' },
    { value: 'destacada', label: translateUiText('collections.types.destacada'), icon: 'bi-star' },
    { value: 'amenazada', label: translateUiText('collections.types.amenazada'), icon: 'bi-exclamation-triangle' },
    { value: 'reciente', label: translateUiText('collections.types.reciente'), icon: 'bi-file-earmark-plus' },
    { value: 'local', label: translateUiText('collections.types.local'), icon: 'bi-geo-alt' },
    { value: 'general', label: translateUiText('code.public.pages.collections.collections.colecciones_generales'), icon: 'bi-flower1' }
  ];

  ngOnInit(): void {
    this.loadFilterOptions();
    this.loadCollections();
    this.statsService.getStats().subscribe({ next: stats => this.stats = stats });
  }

  private loadCollections(): void {
    this.loading = true;
    this.collectionService.getPublicAll(this.currentPage, this.pageSize, '', this.backendFilters).subscribe({
      next: response => {
        this.collections = response.results;
        this.totalItems = response.count;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  private loadFilterOptions(): void {
    this.filterOptionsService.getOptions().subscribe({
      next: options => this.filterOptionsData = options
    });
  }

  get filteredCollections(): Collection[] {
    return this.collections;
  }

  get categories(): CollectionCategory[] {
    return this.categoryDefinitions.map(category => ({
      ...category,
      count: category.value
        ? this.filterOptionsData?.collection_categories.find(item => item.value === category.value)?.count || 0
        : this.filterOptionsData?.collection_categories.reduce((total, item) => total + item.count, 0) || 0
    }));
  }

  get statusOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptionsData?.conservation_statuses || []);
  }

  get familyOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptionsData?.families || []);
  }

  get locationOptions(): SelectInputOption[] {
    return this.toOptions(this.filterOptionsData?.locations || []);
  }

  get hasActiveFilters(): boolean {
    return Boolean(this.selectedCategory || this.selectedStatus || this.selectedFamily || this.selectedLocation);
  }

  get activeFilterCount(): number {
    return [this.selectedCategory, this.selectedStatus, this.selectedFamily, this.selectedLocation].filter(Boolean).length;
  }

  get collectionSpecimenCount(): number {
    return this.filterOptionsData?.collection_specimen_count || 0;
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.totalItems / this.pageSize));
  }

  get pages(): number[] {
    const start = Math.max(1, this.currentPage - 2);
    const end = Math.min(this.totalPages, this.currentPage + 2);
    return Array.from({ length: end - start + 1 }, (_, index) => start + index);
  }

  selectCategory(category: CollectionType | ''): void {
    this.selectedCategory = category;
  }

  openFilters(): void {
    this.filterSnapshot = this.captureFilters();
    this.filtersOpen = true;
  }

  closeFilters(): void {
    this.restoreFilters(this.filterSnapshot);
    this.filtersOpen = false;
  }

  applyFilters(): void {
    this.currentPage = 1;
    this.loadCollections();
    this.filterSnapshot = this.captureFilters();
    this.filtersOpen = false;
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.loadCollections();
    }
  }

  clearFilters(): void {
    this.selectedCategory = '';
    this.selectedStatus = '';
    this.selectedFamily = '';
    this.selectedLocation = '';
  }

  private captureFilters() {
    return {
      selectedCategory: this.selectedCategory,
      selectedStatus: this.selectedStatus,
      selectedFamily: this.selectedFamily,
      selectedLocation: this.selectedLocation
    };
  }

  private restoreFilters(filters: ReturnType<CollectionsComponent['captureFilters']>): void {
    Object.assign(this, filters);
  }

  private get backendFilters(): CollectionFilters {
    return {
      collection_type: this.selectedCategory,
      conservation_status: this.selectedStatus,
      family_name: this.selectedFamily,
      location_name: this.selectedLocation
    };
  }

  private toOptions(values: string[]): SelectInputOption[] {
    return values.map(value => ({ value, label: value }));
  }

}
