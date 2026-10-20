import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Specimen, SpecimenFormOptions, SpecimenListItem, SpecimenWrite } from '../interfaces/specimen.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

export interface SpecimenFilters {
  species?: string;
  q?: string;
  family_name?: string;
  genus_name?: string;
  species_name?: string;
  common_name?: string;
  collector_name?: string;
  location_name?: string;
  conservation_status?: string;
  climate?: string;
  habitat?: string;
  collection_date_from?: string;
  collection_date_to?: string;
  collection?: string;
  ordering?: string;
}

@Injectable({ providedIn: 'root' })
export class SpecimenService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/specimens`;

  getAll(page: number = 1, pageSize: number = 10, search: string = '', filters: SpecimenFilters = {}, includeUnpublished = false): Observable<{ count: number; next: string | null; previous: string | null; results: Specimen[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (includeUnpublished) params = params.set('include_unpublished', 'true');
    if (search.trim()) params = params.set('search', search.trim());
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<any>(`${this.api}/`, { params }).pipe(unwrapList<Specimen>());
  }

  getAdminList(page: number = 1, pageSize: number = 10, search: string = '', includeUnpublished = false): Observable<{ count: number; next: string | null; previous: string | null; results: SpecimenListItem[] }> {
    let params = new HttpParams()
      .set('page', page)
      .set('page_size', pageSize)
      .set('view', 'summary');
    if (includeUnpublished) params = params.set('include_unpublished', 'true');
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<unknown>(`${this.api}/`, { params }).pipe(unwrapList<SpecimenListItem>());
  }

  getFormOptions(): Observable<SpecimenFormOptions> {
    return this.http.get<unknown>(`${this.api}/form-options/`).pipe(
      unwrapData<SpecimenFormOptions>()
    );
  }

  getById(id: string, includeUnpublished = false): Observable<Specimen> {
    const params = includeUnpublished
      ? new HttpParams().set('include_unpublished', 'true')
      : undefined;
    return this.http.get<any>(`${this.api}/${id}/`, { params }).pipe(unwrapData<Specimen>());
  }

  create(payload: SpecimenWrite): Observable<Specimen> {
    return this.http.post<any>(`${this.api}/`, payload).pipe(unwrapData<Specimen>());
  }

  update(id: string, payload: SpecimenWrite): Observable<Specimen> {
    return this.http.put<any>(`${this.api}/${id}/`, payload).pipe(unwrapData<Specimen>());
  }

  delete(id: string): Observable<any> {
    return this.http.delete<any>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }

  search(query: string): Observable<{ count: number; next: string | null; previous: string | null; results: Specimen[] }> {
    const params = new HttpParams().set('search', query.trim());
    return this.http.get<any>(`${this.api}/`, { params }).pipe(unwrapList<Specimen>());
  }

  searchAdvanced(filters: SpecimenFilters, page: number = 1, pageSize: number = 20): Observable<{ count: number; next: string | null; previous: string | null; results: Specimen[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<any>(`${this.api}/search/`, { params }).pipe(unwrapList<Specimen>());
  }
}
