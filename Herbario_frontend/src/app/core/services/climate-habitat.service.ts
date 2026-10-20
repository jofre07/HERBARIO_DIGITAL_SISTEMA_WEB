import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ClimateHabitat, ClimateHabitatWrite } from '../interfaces/climate-habitat.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

@Injectable({ providedIn: 'root' })
export class ClimateHabitatService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/locations/climate-habitats`;

  getAll(page: number = 1, pageSize: number = 10, search: string = ''): Observable<{ count: number; next: string | null; previous: string | null; results: ClimateHabitat[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<any>(this.api, { params }).pipe(unwrapList<ClimateHabitat>());
  }

  getById(id: string): Observable<ClimateHabitat> {
    return this.http.get<any>(`${this.api}/${id}/`).pipe(unwrapData<ClimateHabitat>());
  }

  create(payload: ClimateHabitatWrite): Observable<any> {
    return this.http.post<any>(`${this.api}/`, payload).pipe(unwrapVoid());
  }

  update(id: string, payload: ClimateHabitatWrite): Observable<any> {
    return this.http.put<any>(`${this.api}/${id}/`, payload).pipe(unwrapVoid());
  }

  delete(id: string): Observable<any> {
    return this.http.delete<any>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }
}
