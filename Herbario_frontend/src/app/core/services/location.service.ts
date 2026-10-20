import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { map, Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Location, LocationWrite, MapPoint } from '../interfaces/location.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

export interface MapPointFilters {
  family_name?: string;
  genus_name?: string;
  species_name?: string;
  common_name?: string;
  collector_name?: string;
}

@Injectable({ providedIn: 'root' })
export class LocationService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/locations`;

  getAll(page: number = 1, pageSize: number = 10, search: string = ''): Observable<{ count: number; next: string | null; previous: string | null; results: Location[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<any>(`${this.api}/`, { params }).pipe(unwrapList<Location>());
  }

  getById(id: string): Observable<Location> {
    return this.http.get<any>(`${this.api}/${id}/`).pipe(unwrapData<Location>());
  }

  create(payload: LocationWrite): Observable<Location> {
    return this.http.post<any>(`${this.api}/`, payload).pipe(unwrapData<Location>());
  }

  update(id: string, payload: LocationWrite): Observable<Location> {
    return this.http.put<any>(`${this.api}/${id}/`, payload).pipe(unwrapData<Location>());
  }

  delete(id: string): Observable<any> {
    return this.http.delete<any>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }

  getMapPoints(page: number = 1, pageSize: number = 10, filters: MapPointFilters = {}): Observable<{ count: number; next: string | null; previous: string | null; results: MapPoint[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<any>(`${environment.apiURL}/public/map/points/`, { params }).pipe(
      map((response) => {
        const data = response?.data ?? response;

        if (Array.isArray(data)) {
          return {
            count: data.length,
            next: null,
            previous: null,
            results: data as MapPoint[]
          };
        }

        return {
          count: data?.count ?? 0,
          next: data?.next ?? null,
          previous: data?.previous ?? null,
          results: Array.isArray(data?.results) ? data.results as MapPoint[] : []
        };
      })
    );
  }
}
