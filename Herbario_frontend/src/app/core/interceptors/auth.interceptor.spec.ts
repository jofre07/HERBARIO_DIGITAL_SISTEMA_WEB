import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';
import { AuthRefreshService } from '../services/auth-refresh.service';
import { TokenService } from '../services/token.service';
import { authInterceptor } from './auth.interceptor';

describe('authInterceptor', () => {
  let httpTesting: HttpTestingController;
  let tokenService: TokenService;
  let refreshService: jasmine.SpyObj<AuthRefreshService>;

  beforeEach(() => {
    localStorage.clear();
    refreshService = jasmine.createSpyObj<AuthRefreshService>('AuthRefreshService', [
      'refreshAccessToken'
    ]);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        TokenService,
        { provide: AuthRefreshService, useValue: refreshService },
        { provide: Router, useValue: jasmine.createSpyObj<Router>('Router', ['navigate']) }
      ]
    });

    httpTesting = TestBed.inject(HttpTestingController);
    tokenService = TestBed.inject(TokenService);
    tokenService.updateTokens('access-anterior', 'refresh-vigente');
  });

  afterEach(() => {
    httpTesting.verify();
    localStorage.clear();
  });

  it('renueva el access token y repite la petición que recibió 401', () => {
    refreshService.refreshAccessToken.and.returnValue(of('access-nuevo'));

    const http = TestBed.inject(HttpClient);
    let response: unknown;
    http.get('/api/users/').subscribe((value) => response = value);

    const originalRequest = httpTesting.expectOne('/api/users/');
    expect(originalRequest.request.headers.get('Authorization')).toBe('Bearer access-anterior');
    originalRequest.flush({}, { status: 401, statusText: 'Unauthorized' });

    const retriedRequest = httpTesting.expectOne('/api/users/');
    expect(retriedRequest.request.headers.get('Authorization')).toBe('Bearer access-nuevo');
    retriedRequest.flush({ ok: true });

    expect(refreshService.refreshAccessToken).toHaveBeenCalledTimes(1);
    expect(response).toEqual({ ok: true });
  });
});
