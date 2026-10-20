import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import { Component, OnDestroy, OnInit, inject } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { ImageLightboxComponent, LightboxImage, PublicBreadcrumbComponent, PublicFilterDrawerComponent, SelectInputComponent, SelectInputOption } from '../../../components';
import { HerbariumImage } from '../../../core/interfaces/herbarium-image.interface';
import { PublicFilterOptions } from '../../../core/interfaces/filter-options.interface';
import { HerbariumImageService, ImageFilters } from '../../../core/services/herbarium-image.service';
import { FilterOptionsService } from '../../../core/services/filter-options.service';
import { CountUpDirective } from '../../../shared/directives/count-up.directive';

@Component({
  selector: 'app-gallery',
  standalone: true,
  imports: [UiTextPipe, CommonModule, FormsModule, RouterModule, SelectInputComponent, CountUpDirective, PublicBreadcrumbComponent, PublicFilterDrawerComponent, ImageLightboxComponent],
  templateUrl: './gallery.component.html',
  styleUrl: './gallery.component.scss'
})
export class GalleryComponent implements OnInit, OnDestroy {
  private imageService = inject(HerbariumImageService);
  private filterOptionsService = inject(FilterOptionsService);

  searchQuery = '';
  selectedSpecies = '';
  selectedFamily = '';
  selectedGenus = '';
  selectedLocation = '';
  selectedStatus = '';
  selectedSort = 'newest';
  viewMode: 'grid' | 'list' = 'grid';
  currentPage = 1;
  pageSize = 12;
  totalItems = 0;
  loading = false;
  filtersOpen = false;
  items: HerbariumImage[] = [];
  filterOptionsData: PublicFilterOptions | null = null;
  lightboxItem: HerbariumImage | null = null;
  lightboxIndex = 0;
  private searchTimer?: ReturnType<typeof setTimeout>;
  private filterSnapshot = this.captureFilters();

  ngOnInit(): void {
    this.loadFilterOptions();
    this.loadImages();
  }

  ngOnDestroy(): void {
    if (this.searchTimer) clearTimeout(this.searchTimer);
  }

  private loadImages(): void {
    this.loading = true;
    this.imageService.getPublicAll(this.currentPage, this.pageSize, this.searchQuery, this.backendFilters).subscribe({
      next: response => {
        this.items = response.results;
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

  get filteredItems(): HerbariumImage[] {
    return this.items;
  }

  get paginatedItems(): HerbariumImage[] {
    return this.items;
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.totalItems / this.pageSize));
  }

  get pages(): number[] {
    const start = Math.max(1, this.currentPage - 2);
    const end = Math.min(this.totalPages, this.currentPage + 2);
    return Array.from({ length: end - start + 1 }, (_, index) => start + index);
  }

  get resultStart(): number {
    return this.totalItems ? (this.currentPage - 1) * this.pageSize + 1 : 0;
  }

  get resultEnd(): number {
    return Math.min(this.currentPage * this.pageSize, this.totalItems);
  }

  get hasActiveFilters(): boolean {
    return Boolean(
      this.searchQuery || this.selectedSpecies || this.selectedFamily ||
      this.selectedGenus || this.selectedLocation || this.selectedStatus
    );
  }

  get activeFilterCount(): number {
    return [this.searchQuery, this.selectedSpecies, this.selectedFamily, this.selectedGenus,
      this.selectedLocation, this.selectedStatus].filter(Boolean).length;
  }

  get familyList(): string[] {
    return this.filterOptionsData?.families || [];
  }

  get genusList(): string[] {
    return this.uniqueSorted(
      (this.filterOptionsData?.genera || [])
        .filter(item => !this.selectedFamily || item.family_name === this.selectedFamily)
        .map(item => item.name)
    );
  }

  get speciesList(): string[] {
    return this.uniqueSorted(
      (this.filterOptionsData?.species || [])
        .filter(item => !this.selectedFamily || item.family_name === this.selectedFamily)
        .filter(item => !this.selectedGenus || item.genus_name === this.selectedGenus)
        .map(item => item.name)
    );
  }

  get locationList(): string[] {
    return this.filterOptionsData?.locations || [];
  }

  get statusList(): string[] {
    return this.filterOptionsData?.conservation_statuses || [];
  }

  get familyOptions(): SelectInputOption[] { return this.toOptions(this.familyList); }
  get genusOptions(): SelectInputOption[] { return this.toOptions(this.genusList); }
  get speciesOptions(): SelectInputOption[] { return this.toOptions(this.speciesList); }
  get locationOptions(): SelectInputOption[] { return this.toOptions(this.locationList); }
  get statusOptions(): SelectInputOption[] { return this.toOptions(this.statusList); }
  get sortOptions(): SelectInputOption[] {
    return [
      { value: 'newest', label: translateUiText('views.public.pages.gallery.gallery.mas_recientes') },
      { value: 'oldest', label: translateUiText('views.public.pages.gallery.gallery.mas_antiguas') },
      { value: 'species', label: translateUiText('views.public.pages.gallery.gallery.especie_a_z') },
      { value: 'catalog', label: translateUiText('views.public.pages.gallery.gallery.codigo_de_catalogo') }
    ];
  }

  onFamilyChange(): void {
    if (this.selectedGenus && !this.genusList.includes(this.selectedGenus)) this.selectedGenus = '';
    if (this.selectedSpecies && !this.speciesList.includes(this.selectedSpecies)) this.selectedSpecies = '';
  }

  onGenusChange(): void {
    if (this.selectedSpecies && !this.speciesList.includes(this.selectedSpecies)) this.selectedSpecies = '';
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadImages();
  }

  onSearchInput(): void {}

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
    this.loadImages();
    this.filterSnapshot = this.captureFilters();
    this.filtersOpen = false;
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.selectedSpecies = '';
    this.selectedFamily = '';
    this.selectedGenus = '';
    this.selectedLocation = '';
    this.selectedStatus = '';
  }

  private captureFilters() {
    return {
      searchQuery: this.searchQuery,
      selectedSpecies: this.selectedSpecies,
      selectedFamily: this.selectedFamily,
      selectedGenus: this.selectedGenus,
      selectedLocation: this.selectedLocation,
      selectedStatus: this.selectedStatus
    };
  }

  private restoreFilters(filters: ReturnType<GalleryComponent['captureFilters']>): void {
    Object.assign(this, filters);
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.loadImages();
    }
  }

  openLightbox(item: HerbariumImage): void {
    this.lightboxItem = item;
    this.lightboxIndex = Math.max(0, this.items.findIndex(image => image.id === item.id));
  }

  closeLightbox(): void {
    this.lightboxItem = null;
    this.lightboxIndex = 0;
  }

  get lightboxImages(): LightboxImage[] {
    return this.items.filter(item => Boolean(item.url)).map(item => ({
      url: item.variants?.large?.url || item.url,
      alt: item.species_name || item.catalog_code,
      title: item.species_name || item.catalog_code,
      subtitle: [item.catalog_code, item.family_name].filter(Boolean).join(' · ')
    }));
  }

  imageTypeLabel(value: string): string {
    return value === 'specimen' ? translateUiText('views.public.pages.advanced_search.advanced_search.especimen') : value || translateUiText('code.public.pages.gallery.gallery.imagen');
  }

  private toOptions(values: string[]): SelectInputOption[] {
    return values.map(value => ({ value, label: value }));
  }

  private get backendFilters(): ImageFilters {
    return {
      species_name: this.selectedSpecies,
      family_name: this.selectedFamily,
      genus_name: this.selectedGenus,
      location_name: this.selectedLocation,
      conservation_status: this.selectedStatus,
      ordering: this.selectedSort
    };
  }

  private uniqueSorted(values: Array<string | null | undefined>): string[] {
    return [...new Set(values.filter((value): value is string => Boolean(value)))].sort((a, b) =>
      a.localeCompare(b, 'es', { sensitivity: 'base' })
    );
  }

}
