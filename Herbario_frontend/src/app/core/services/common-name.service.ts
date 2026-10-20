import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { CommonName, CommonNameWrite } from '../interfaces/common-name.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

@Injectable({ providedIn: 'root' })
export class CommonNameService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/taxonomy/common-names`;

  getAll(page: number = 1, pageSize: number = 10, search: string = ''): Observable<{ count: number; next: string | null; previous: string | null; results: CommonName[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<any>(this.api, { params }).pipe(unwrapList<CommonName>());
  }

  getById(id: string): Observable<CommonName> {
    return this.http.get<any>(`${this.api}/${id}/`).pipe(unwrapData<CommonName>());
  }

  create(payload: CommonNameWrite): Observable<any> {
    return this.http.post<any>(`${this.api}/`, payload).pipe(unwrapVoid());
  }

  update(id: string, payload: CommonNameWrite): Observable<any> {
    return this.http.put<any>(`${this.api}/${id}/`, payload).pipe(unwrapVoid());
  }

  delete(id: string): Observable<any> {
    return this.http.delete<any>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }
}
