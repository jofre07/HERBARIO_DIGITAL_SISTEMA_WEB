import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Collection, CollectionWrite } from '../interfaces/collection.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

export interface CollectionFilters {
  collection_type?: string;
  conservation_status?: string;
  family_name?: string;
  location_name?: string;
}

@Injectable({ providedIn: 'root' })
export class CollectionService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/collections`;

  getAll(page: number = 1, pageSize: number = 10, search: string = '', filters: CollectionFilters = {}, includeUnpublished = false): Observable<{ count: number; next: string | null; previous: string | null; results: Collection[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (includeUnpublished) params = params.set('include_unpublished', 'true');
    if (search.trim()) params = params.set('search', search.trim());
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<any>(this.api, { params }).pipe(unwrapList<Collection>());
  }

  getById(id: string): Observable<Collection> {
    return this.http.get<any>(`${this.api}/${id}/`).pipe(unwrapData<Collection>());
  }

  getPublicAll(page = 1, pageSize = 10, search = '', filters: CollectionFilters = {}): Observable<{ count: number; next: string | null; previous: string | null; results: Collection[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<any>(`${environment.apiURL}/public/collections/`, { params }).pipe(unwrapList<Collection>());
  }

  create(payload: CollectionWrite): Observable<any> {
    return this.http.post<any>(`${this.api}/`, payload).pipe(unwrapVoid());
  }

  update(id: string, payload: CollectionWrite): Observable<any> {
    return this.http.put<any>(`${this.api}/${id}/`, payload).pipe(unwrapVoid());
  }

  delete(id: string): Observable<any> {
    return this.http.delete<any>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }
}
