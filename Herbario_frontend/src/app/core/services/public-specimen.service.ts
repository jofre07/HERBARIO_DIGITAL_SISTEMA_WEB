import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { unwrapData, unwrapList } from '../helpers/response.helper';
import { Specimen } from '../interfaces/specimen.interface';
import { SpecimenFilters } from './specimen.service';

@Injectable({ providedIn: 'root' })
export class PublicSpecimenService {
  private readonly http = inject(HttpClient);
  private readonly api = `${environment.apiURL}/public/specimens`;

  getAll(page = 1, pageSize = 10, search = '', filters: SpecimenFilters = {}): Observable<{ count: number; next: string | null; previous: string | null; results: Specimen[] }> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (search.trim()) params = params.set('search', search.trim());
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params = params.set(key, value);
    });
    return this.http.get<unknown>(`${this.api}/`, { params }).pipe(unwrapList<Specimen>());
  }

  getById(id: string): Observable<Specimen> {
    return this.http.get<unknown>(`${this.api}/${id}/`).pipe(unwrapData<Specimen>());
  }

  searchAdvanced(filters: SpecimenFilters, page = 1, pageSize = 20): Observable<{ count: number; next: string | null; previous: string | null; results: Specimen[] }> {
    return this.getAll(page, pageSize, '', filters);
  }
}
