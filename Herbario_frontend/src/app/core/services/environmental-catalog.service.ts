import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { EnvironmentalCatalogItem, EnvironmentalCatalogWrite } from '../interfaces/environmental-catalog.interface';
import { unwrapData, unwrapList, unwrapVoid } from '../helpers/response.helper';

export type EnvironmentalCatalogType = 'climates' | 'habitats';

@Injectable({ providedIn: 'root' })
export class EnvironmentalCatalogService {
  private readonly http = inject(HttpClient);
  private readonly api = `${environment.apiURL}/locations`;

  getAll(type: EnvironmentalCatalogType, page = 1, pageSize = 10, search = ''): Observable<{ count: number; next: string | null; previous: string | null; results: EnvironmentalCatalogItem[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<unknown>(`${this.api}/${type}/`, { params }).pipe(
      unwrapList<EnvironmentalCatalogItem>()
    );
  }

  getById(type: EnvironmentalCatalogType, id: string): Observable<EnvironmentalCatalogItem> {
    return this.http.get<unknown>(`${this.api}/${type}/${id}/`).pipe(
      unwrapData<EnvironmentalCatalogItem>()
    );
  }

  create(type: EnvironmentalCatalogType, payload: EnvironmentalCatalogWrite): Observable<{ message?: string }> {
    return this.http.post<unknown>(`${this.api}/${type}/`, payload).pipe(unwrapVoid());
  }

  update(type: EnvironmentalCatalogType, id: string, payload: EnvironmentalCatalogWrite): Observable<{ message?: string }> {
    return this.http.put<unknown>(`${this.api}/${type}/${id}/`, payload).pipe(unwrapVoid());
  }

  delete(type: EnvironmentalCatalogType, id: string): Observable<{ message?: string }> {
    return this.http.delete<unknown>(`${this.api}/${type}/${id}/`).pipe(unwrapVoid());
  }
}
