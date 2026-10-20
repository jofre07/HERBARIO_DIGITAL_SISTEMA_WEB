import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AdminImageDetail, AdminImageListItem, AdminSpecimenOption, HerbariumImage, HerbariumImageAsset, HerbariumImageWrite } from '../interfaces/herbarium-image.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

export interface ImageFilters {
  specimen_id?: string;
  family_name?: string;
  genus_name?: string;
  species_name?: string;
  location_name?: string;
  conservation_status?: string;
  collection_date_from?: string;
  collection_date_to?: string;
  image_type?: string;
  ordering?: string;
}

interface HerbariumImageGroup {
  specimen_id: string;
  catalog_code: string;
  images: HerbariumImageAsset[];
}

interface ImageWriteResponse {
  message?: string;
}

@Injectable({ providedIn: 'root' })
export class HerbariumImageService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/media`;

  getAdminList(page: number = 1, pageSize: number = 10, search: string = '', filters: ImageFilters = {}, includeUnpublished = false): Observable<{ count: number; next: string | null; previous: string | null; results: AdminImageListItem[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (includeUnpublished) params = params.set('include_unpublished', 'true');
    if (search.trim()) params = params.set('search', search.trim());
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<unknown>(`${this.api}/`, { params }).pipe(
      unwrapList<AdminImageListItem>()
    );
  }

  getAdminDetail(specimenId: string, includeUnpublished = false): Observable<AdminImageDetail> {
    let params = new HttpParams();
    if (includeUnpublished) params = params.set('include_unpublished', 'true');
    return this.http.get<unknown>(`${this.api}/specimens/${specimenId}/`, { params }).pipe(
      unwrapData<AdminImageDetail>()
    );
  }

  getAdminSpecimenOptions(): Observable<AdminSpecimenOption[]> {
    return this.http.get<unknown>(`${this.api}/specimen-options/`).pipe(
      unwrapData<AdminSpecimenOption[]>()
    );
  }

  getById(id: string): Observable<HerbariumImage> {
    return this.http.get<unknown>(`${this.api}/${id}/`).pipe(unwrapData<HerbariumImage>());
  }

  getPublicAll(page = 1, pageSize = 10, search = '', filters: ImageFilters = {}): Observable<{ count: number; next: string | null; previous: string | null; results: HerbariumImage[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<unknown>(`${environment.apiURL}/public/media/`, { params }).pipe(
      unwrapList<HerbariumImage | HerbariumImageGroup>(),
      map(response => ({
        ...response,
        results: response.results.map(item => this.normalizeImageGroup(item))
      }))
    );
  }

  getPublicBySpecies(speciesId: string, page = 1, pageSize = 5): Observable<{ count: number; next: string | null; previous: string | null; results: HerbariumImage[] }> {
    const params = new HttpParams().set('page', page).set('page_size', pageSize);
    return this.http.get<unknown>(`${environment.apiURL}/public/catalog/species/${speciesId}/images/`, { params }).pipe(
      unwrapList<HerbariumImage>()
    );
  }

  create(payload: HerbariumImageWrite): Observable<ImageWriteResponse> {
    return this.http.post<ImageWriteResponse>(`${this.api}/`, this.toFormData(payload)).pipe(unwrapVoid());
  }

  update(id: string, payload: HerbariumImageWrite): Observable<ImageWriteResponse> {
    return this.http.put<ImageWriteResponse>(`${this.api}/${id}/`, this.toFormData(payload)).pipe(unwrapVoid());
  }

  delete(id: string): Observable<ImageWriteResponse> {
    return this.http.delete<ImageWriteResponse>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }

  private toFormData(payload: HerbariumImageWrite): FormData {
    const formData = new FormData();
    formData.append('specimen_id', payload.specimen_id);
    if (payload.image) formData.append('image', payload.image, payload.image.name);
    formData.append('credit', payload.credit || '');
    return formData;
  }

  private normalizeImageGroup(item: HerbariumImage | HerbariumImageGroup): HerbariumImage {
    const groupedImages = (item as HerbariumImageGroup).images;
    if (!Array.isArray(groupedImages)) {
      const flatImage = item as HerbariumImage;
      return {
        ...flatImage,
        images: [{
          id: flatImage.id,
          url: flatImage.url,
          original_url: flatImage.original_url,
          variants: flatImage.variants,
          credit: flatImage.credit
        }]
      };
    }
    const group = item as HerbariumImageGroup;
    const cover = groupedImages[0];
    return {
      id: cover?.id || group.specimen_id,
      specimen_id: group.specimen_id,
      species_id: '',
      catalog_code: group.catalog_code,
      species_name: '',
      genus_name: '',
      family_name: '',
      collection_date: null,
      location_names: [],
      conservation_status: null,
      image_type: 'specimen',
      url: cover?.url || '',
      credit: cover?.credit || '',
      created_at: '',
      updated_at: '',
      images: groupedImages
    };
  }
}
