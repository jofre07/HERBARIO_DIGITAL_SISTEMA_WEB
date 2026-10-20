import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { map, Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Role, RoleWrite } from '../interfaces/role.interface';
import { Permission } from '../interfaces/permission.interface';
import { unwrapList, unwrapData, unwrapVoid } from '../helpers/response.helper';

@Injectable({ providedIn: 'root' })
export class RoleService {
  private http = inject(HttpClient);
  private api = `${environment.apiURL}/roles`;

  getAll(page: number = 1, pageSize: number = 10, search: string = ''): Observable<{ count: number; next: string | null; previous: string | null; results: Role[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    return this.http.get<any>(`${this.api}/`, { params }).pipe(unwrapList<Role>());
  }

  getById(id: string): Observable<Role> {
    return this.http.get<any>(`${this.api}/${id}/`).pipe(unwrapData<Role>());
  }

  create(payload: RoleWrite): Observable<any> {
    return this.http.post<any>(`${this.api}/`, payload).pipe(unwrapVoid());
  }

  update(id: string, payload: RoleWrite): Observable<any> {
    return this.http.put<any>(`${this.api}/${id}/`, payload).pipe(unwrapVoid());
  }

  delete(id: string): Observable<any> {
    return this.http.delete<any>(`${this.api}/${id}/`).pipe(unwrapVoid());
  }

  getPermissions(): Observable<{ count: number; next: string | null; previous: string | null; results: Permission[] }> {
    return this.http.get<any>(`${this.api}/permissions/`).pipe(
      map(response => {
        const data = response?.data;
        const results: Permission[] = Array.isArray(data)
          ? data
          : Array.isArray(data?.results)
            ? data.results
            : [];

        return {
          count: data?.count ?? results.length,
          next: data?.next ?? null,
          previous: data?.previous ?? null,
          results
        };
      })
    );
  }
}
