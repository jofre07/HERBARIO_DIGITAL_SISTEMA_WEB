import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Language } from '../interfaces/language.interface';
import { unwrapList, unwrapData } from '../helpers/response.helper';

@Injectable({ providedIn: 'root' })
export class LanguageService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/taxonomy/languages`;

  getAll(page: number = 1, pageSize: number = 10, search: string = ''): Observable<{ count: number; next: string | null; previous: string | null; results: Language[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<any>(`${this.api}/`, { params }).pipe(unwrapList<Language>());
  }

  getById(id: string): Observable<Language> {
    return this.http.get<any>(`${this.api}/${id}/`).pipe(unwrapData<Language>());
  }
}
