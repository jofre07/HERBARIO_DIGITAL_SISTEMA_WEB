import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule, ActivatedRoute } from "@angular/router";
import { SpeciesService } from '../../../core/services/species.service';
import { HerbariumImageService } from '../../../core/services/herbarium-image.service';
import { SpeciesCatalogDetail } from '../../../core/interfaces/species.interface';
import { HerbariumImage } from '../../../core/interfaces/herbarium-image.interface';
import { Specimen } from '../../../core/interfaces/specimen.interface';
import { ImageLightboxComponent, LightboxImage, PublicBreadcrumbComponent, PublicBreadcrumbItem, TableFilterPipe, TableSearchComponent } from '../../../components';
import { SpecimenLocation } from '../../../core/interfaces/specimen.interface';
import * as L from 'leaflet';
import { plantMarkerIcon } from '../../../shared/utils/map-marker';

interface CatalogLocationRecord {
  specimen: Specimen;
  location: SpecimenLocation;
}

@Component({
  selector: 'app-catalog-detail',
  standalone: true,
  imports: [UiTextPipe, CommonModule, RouterModule, PublicBreadcrumbComponent, TableSearchComponent, TableFilterPipe, ImageLightboxComponent],
  templateUrl: './catalog-detail.component.html',
  styleUrl: './catalog-detail.component.scss'
})
export class CatalogDetailComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private speciesService = inject(SpeciesService);
  private imageService = inject(HerbariumImageService);

  species: SpeciesCatalogDetail | null = null;
  specimens: Specimen[] = [];
  galleryImages: HerbariumImage[] = [];
  initialImageUrls: string[] = [];
  galleryImagesLoading = false;
  galleryImagesLoaded = false;
  galleryImagesPage = 1;
  galleryImagesTotal = 0;
  loading = true;
  loadError = false;
  activeTab = 'descripcion';
  specimenSearchQuery = '';
  selectedImageUrl: string | null = null;
  galleryOpen = false;
  galleryStartIndex = 0;
  private map: L.Map | null = null;
  private slideshowTimer?: ReturnType<typeof setInterval>;
  @ViewChild("speciesMap") private mapElement?: ElementRef<HTMLDivElement>;

  readonly tabs = [
    { key: 'descripcion', label: translateUiText('views.public.pages.catalog_detail.catalog_detail.descripcion'), icon: 'bi-file-text' },
    { key: 'taxonomia', label: translateUiText('views.public.pages.catalog_detail.catalog_detail.taxonomia'), icon: 'bi-diagram-3' },
    { key: 'nombres-comunes', label: translateUiText('views.public.pages.catalog_detail.catalog_detail.nombres_comunes'), icon: 'bi-translate' },
    { key: 'conservacion', label: translateUiText('views.public.pages.about.about.conservacion'), icon: 'bi-shield-check' },
    { key: 'clima-habitat', label: translateUiText('views.public.pages.catalog_detail.catalog_detail.clima_y_habitat'), icon: 'bi-geo-alt' },
    { key: 'mapa', label: translateUiText('navigation.map'), icon: 'bi-map' },
    { key: 'especimenes', label: translateUiText('navigation.specimens'), icon: 'bi-collection' },
    { key: 'galeria', label: translateUiText('navigation.gallery'), icon: 'bi-images' }
  ] as const;

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) this.loadSpecies(id);
    });
  }

  ngOnDestroy(): void {
    this.destroyMap();
    this.stopSlideshow();
  }

  get locations(): SpecimenLocation[] {
    return this.locationRecords.map(record => record.location);
  }

  get locationRecords(): CatalogLocationRecord[] {
    return this.specimens.flatMap(specimen =>
      (specimen.locations || []).map(location => ({ specimen, location }))
    );
  }

  get imageUrls(): string[] {
    return [...new Set([
      ...this.initialImageUrls,
      ...this.galleryImages.map(image => image.url)
    ])];
  }

  get previewImageUrls(): string[] {
    return [...new Set(this.initialImageUrls)].slice(0, 5);
  }

  get thumbnailUrls(): string[] {
    return this.previewImageUrls.filter(url => url !== this.selectedImageUrl);
  }

  get lightboxImages(): LightboxImage[] {
    const speciesName = this.species?.name || 'Especie';
    return this.imageUrls.map((url, index) => ({
      url: this.galleryImages.find(image => image.url === url)?.variants?.large?.url || url,
      alt: `Fotografía ${index + 1} de ${speciesName}`,
      title: speciesName,
      subtitle: this.species?.family_name || ''
    }));
  }

  get breadcrumbItems(): readonly PublicBreadcrumbItem[] {
    return [
      { label: translateUiText('navigation.home'), route: '/' },
      { label: translateUiText('views.public.pages.catalog.catalog.catalogo_de_especies'), route: '/catalogo' },
      { label: this.species?.name || translateUiText('code.public.pages.catalog_detail.catalog_detail.detalle_de_especie') }
    ];
  }

  private loadSpecies(id: string): void {
    this.stopSlideshow();
    this.loading = true;
    this.loadError = false;
    this.species = null;
    this.specimens = [];
    this.galleryImages = [];
    this.initialImageUrls = [];
    this.galleryImagesLoaded = false;
    this.galleryImagesPage = 1;
    this.galleryImagesTotal = 0;
    this.selectedImageUrl = null;

    this.speciesService.getPublicCatalogDetail(id).subscribe({
      next: detail => {
        this.species = detail;
        this.specimens = (detail.specimens || []).map(specimen => ({ ...specimen, image_urls: [] }));
        this.initialImageUrls = detail.image_urls || [];
        this.galleryImagesTotal = detail.image_count || this.initialImageUrls.length;
        this.galleryImagesLoaded = true;
        this.selectedImageUrl = this.previewImageUrls[0] || null;
        this.startSlideshow();
        this.loading = false;
      },
      error: () => {
        this.loadError = true;
        this.loading = false;
      }
    });
  }

  selectImage(url: string): void {
    this.selectedImageUrl = url;
    this.startSlideshow();
  }

  openGalleryImage(index: number): void {
    this.galleryStartIndex = index;
    this.galleryOpen = true;
    this.stopSlideshow();
  }

  closeGalleryImage(): void {
    this.galleryOpen = false;
    this.galleryStartIndex = 0;
    this.startSlideshow();
  }

  private startSlideshow(): void {
    this.stopSlideshow();
    if (this.previewImageUrls.length < 2 || this.galleryOpen) return;

    this.slideshowTimer = setInterval(() => {
      const currentIndex = Math.max(0, this.previewImageUrls.indexOf(this.selectedImageUrl || ''));
      this.selectedImageUrl = this.previewImageUrls[(currentIndex + 1) % this.previewImageUrls.length];
    }, 5000);
  }

  private stopSlideshow(): void {
    if (!this.slideshowTimer) return;
    clearInterval(this.slideshowTimer);
    this.slideshowTimer = undefined;
  }

  setTab(tab: string): void {
    this.activeTab = tab;
    if (tab === 'mapa') setTimeout(() => this.initializeMap());
    else this.destroyMap();
    if (tab === 'galeria' && this.imageUrls.length < this.galleryImagesTotal && this.galleryImagesPage === 1) {
      this.loadMoreGalleryImages();
    }
  }

  loadMoreGalleryImages(): void {
    if (this.galleryImagesLoading || this.imageUrls.length >= this.galleryImagesTotal) return;
    this.galleryImagesPage += 1;
    this.loadGalleryImages();
  }

  private loadGalleryImages(): void {
    const speciesId = this.species?.id;
    if (!speciesId || this.galleryImagesLoading) return;

    this.galleryImagesLoading = true;
    this.imageService.getPublicBySpecies(speciesId, this.galleryImagesPage, 5).subscribe({
      next: response => {
        const knownUrls = new Set(this.imageUrls);
        this.galleryImages = [
          ...this.galleryImages,
          ...response.results.filter(image => !knownUrls.has(image.url))
        ];
        this.galleryImagesTotal = response.count;
        this.galleryImagesLoading = false;
        if (!this.selectedImageUrl) this.selectedImageUrl = this.imageUrls[0] || null;
        this.startSlideshow();
      },
      error: () => {
        this.galleryImagesPage = Math.max(1, this.galleryImagesPage - 1);
        this.galleryImagesLoading = false;
      }
    });
  }

  private initializeMap(): void {
    this.destroyMap();
    const element = this.mapElement?.nativeElement;
    const records = this.locationRecords.filter(({ location }) =>
      Number.isFinite(Number(location.latitude)) && Number.isFinite(Number(location.longitude))
    );
    if (!element || !records.length) return;
    const first = records.find(({ location }) => location.is_primary) || records[0];
    this.map = L.map(element, {
      center: [Number(first.location.latitude), Number(first.location.longitude)],
      zoom: 10,
      scrollWheelZoom: true
    });
    this.map.attributionControl.setPrefix(false);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: "&copy; OpenStreetMap", maxZoom: 19 }).addTo(this.map);
    const bounds: L.LatLngExpression[] = [];
    records.forEach(({ specimen, location }) => {
      const coordinates: L.LatLngExpression = [Number(location.latitude), Number(location.longitude)];
      bounds.push(coordinates);
      const popup = document.createElement('div');
      const locationName = document.createElement('strong');
      const specimenCode = document.createElement('div');
      const environment = document.createElement('small');
      locationName.textContent = location.location_name || translateUiText('views.public.pages.catalog_detail.catalog_detail.ubicacion_sin_nombre');
      specimenCode.textContent = translateUiText('dynamic.map.specimen', { code: specimen.catalog_code });
      environment.textContent = [location.climate_name, location.habitat_name].filter(Boolean).join(' · ') || translateUiText('code.public.pages.catalog_detail.catalog_detail.sin_datos_ambientales');
      popup.append(locationName, specimenCode, environment);
      L.marker(coordinates, { icon: plantMarkerIcon(location.marker_icon, location.is_primary) })
        .bindPopup(popup)
        .addTo(this.map!);
    });
    if (bounds.length > 1) this.map.fitBounds(L.latLngBounds(bounds), { padding: [24, 24] });
    setTimeout(() => this.map?.invalidateSize());
  }

  private destroyMap(): void {
    this.map?.remove();
    this.map = null;
  }
}
