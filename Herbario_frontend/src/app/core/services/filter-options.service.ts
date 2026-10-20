import { Injectable, inject } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { map, Observable, shareReplay, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { unwrapData } from '../helpers/response.helper';
import { PublicFilterOptions } from '../interfaces/filter-options.interface';

@Injectable({ providedIn: 'root' })
export class FilterOptionsService {
  private http = inject(HttpClient);
  private options$?: Observable<PublicFilterOptions>;

  getOptions(): Observable<PublicFilterOptions> {
    if (!this.options$) {
      this.options$ = this.http
        .get<any>(`${environment.apiURL}/public/filter-options/`)
        .pipe(unwrapData<PublicFilterOptions>(), shareReplay(1));
    }
    return this.options$;
  }

  recordSearch(term: string): Observable<void> {
    return this.http
      .post(`${environment.apiURL}/public/searches/`, { term })
      .pipe(
        tap(() => this.invalidate()),
        map(() => undefined)
      );
  }

  invalidate(): void {
    this.options$ = undefined;
  }
}
