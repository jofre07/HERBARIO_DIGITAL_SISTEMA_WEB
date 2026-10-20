import { Injectable, inject } from "@angular/core";
import { HttpClient, HttpParams } from "@angular/common/http";
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { HerbariumStats } from '../interfaces/dashboard.interface';
import { unwrapData } from '../helpers/response.helper';

@Injectable({ providedIn: 'root' })
export class StatsService {
  private http = inject(HttpClient);
  getStats(includeUnpublished = false): Observable<HerbariumStats> {
    const params = includeUnpublished
      ? new HttpParams().set('include_unpublished', 'true')
      : undefined;
    const endpoint = includeUnpublished
      ? `${environment.apiURL}/stats/`
      : `${environment.apiURL}/public/stats/`;
    return this.http.get<any>(endpoint, { params }).pipe(unwrapData<HerbariumStats>());
  }
}
