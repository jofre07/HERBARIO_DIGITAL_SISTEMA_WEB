import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Species, SpeciesWrite, SpeciesCatalog, SpeciesCatalogDetail } from '../interfaces/species.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

export interface CatalogFilters {
  featured?: boolean;
  species?: string;
  q?: string;
  common_name?: string;
  family_name?: string;
  genus_name?: string;
  species_name?: string;
  conservation_status?: string;
  location_name?: string;
  climate?: string;
  habitat?: string;
  ordering?: string;
}

@Injectable({ providedIn: 'root' })
export class SpeciesService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/taxonomy/species`;

  getAll(page: number = 1, pageSize: number = 10, search: string = ''): Observable<{ count: number; next: string | null; previous: string | null; results: Species[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<any>(this.api, { params }).pipe(unwrapList<Species>());
  }

  getById(id: string): Observable<Species> {
    return this.http.get<any>(`${this.api}/${id}/`).pipe(unwrapData<Species>());
  }

  create(payload: SpeciesWrite): Observable<any> {
    return this.http.post<any>(`${this.api}/`, payload).pipe(unwrapVoid());
  }

  update(id: string, payload: SpeciesWrite): Observable<any> {
    return this.http.put<any>(`${this.api}/${id}/`, payload).pipe(unwrapVoid());
  }

  delete(id: string): Observable<any> {
    return this.http.delete<any>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }

  getCatalog(page: number = 1, pageSize: number = 10, filters: CatalogFilters = {}): Observable<{ count: number; next: string | null; previous: string | null; results: SpeciesCatalog[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<any>(`${environment.apiURL}/public/catalog/species/`, { params }).pipe(unwrapList<SpeciesCatalog>());
  }

  getPublicCatalogDetail(id: string): Observable<SpeciesCatalogDetail> {
    return this.http.get<unknown>(`${environment.apiURL}/public/catalog/species/${id}/`).pipe(
      unwrapData<SpeciesCatalogDetail>()
    );
  }
}
