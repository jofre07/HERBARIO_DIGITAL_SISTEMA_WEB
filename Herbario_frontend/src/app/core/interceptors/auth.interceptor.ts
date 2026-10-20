import { HttpErrorResponse, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';
import { environment } from '../../../environments/environment';
import { AuthRefreshService } from '../services/auth-refresh.service';
import { TokenService } from '../services/token.service';

const withAccessToken = (request: HttpRequest<unknown>, accessToken: string) =>
  request.clone({
    setHeaders: {
      Authorization: `Bearer ${accessToken}`
    }
  });

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const tokenService = inject(TokenService);
  const authRefreshService = inject(AuthRefreshService);
  const router = inject(Router);
  const accessToken = tokenService.getToken();
  const isTokenEndpoint = req.url === `${environment.apiURL}/token/`
    || req.url === `${environment.apiURL}/token/refresh/`;
  const authenticatedRequest = accessToken && !isTokenEndpoint
    ? withAccessToken(req, accessToken)
    : req;

  return next(authenticatedRequest).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status !== 401 || isTokenEndpoint) {
        return throwError(() => error);
      }

      if (!tokenService.getRefreshToken()) {
        tokenService.clear();
        void router.navigate(['/login']);
        return throwError(() => error);
      }

      return authRefreshService.refreshAccessToken().pipe(
        switchMap((newAccessToken) => next(withAccessToken(req, newAccessToken))),
        catchError((refreshError: unknown) => {
          tokenService.clear();
          void router.navigate(['/login']);
          return throwError(() => refreshError);
        })
      );
    })
  );
};
