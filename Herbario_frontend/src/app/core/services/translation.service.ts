import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Translation, TranslationWrite } from '../interfaces/translation.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

@Injectable({ providedIn: 'root' })
export class TranslationService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/taxonomy/translations`;

  getAll(page: number = 1, pageSize: number = 10, search: string = ''): Observable<{ count: number; next: string | null; previous: string | null; results: Translation[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<any>(this.api, { params }).pipe(unwrapList<Translation>());
  }

  getById(id: string): Observable<Translation> {
    return this.http.get<any>(`${this.api}/${id}/`).pipe(unwrapData<Translation>());
  }

  create(payload: TranslationWrite): Observable<any> {
    return this.http.post<any>(`${this.api}/`, payload).pipe(unwrapVoid());
  }

  update(id: string, payload: TranslationWrite): Observable<any> {
    return this.http.put<any>(`${this.api}/${id}/`, payload).pipe(unwrapVoid());
  }

  delete(id: string): Observable<any> {
    return this.http.delete<any>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }
}
