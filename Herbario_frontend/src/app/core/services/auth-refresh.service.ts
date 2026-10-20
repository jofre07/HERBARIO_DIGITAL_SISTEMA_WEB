import { HttpBackend, HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, finalize, map, shareReplay, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { RefreshResponse } from '../interfaces/auth.interface';
import { TokenService } from './token.service';

@Injectable({ providedIn: 'root' })
export class AuthRefreshService {
  private readonly tokenService = inject(TokenService);
  private readonly http = new HttpClient(inject(HttpBackend));
  private readonly refreshUrl = `${environment.apiURL}/token/refresh/`;
  private refreshRequest$: Observable<string> | null = null;

  refreshAccessToken(): Observable<string> {
    if (this.refreshRequest$) {
      return this.refreshRequest$;
    }

    const refreshToken = this.tokenService.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No hay un refresh token disponible.'));
    }

    this.refreshRequest$ = this.http
      .post<RefreshResponse>(this.refreshUrl, { refresh: refreshToken })
      .pipe(
        map((response) => {
          const refreshedTokens = response.data;
          if (!refreshedTokens?.access) {
            throw new Error('La respuesta de renovación no contiene un access token.');
          }

          this.tokenService.updateTokens(
            refreshedTokens.access,
            refreshedTokens.refresh ?? refreshToken
          );

          return refreshedTokens.access;
        }),
        finalize(() => {
          this.refreshRequest$ = null;
        }),
        shareReplay({ bufferSize: 1, refCount: false })
      );

    return this.refreshRequest$;
  }
}
