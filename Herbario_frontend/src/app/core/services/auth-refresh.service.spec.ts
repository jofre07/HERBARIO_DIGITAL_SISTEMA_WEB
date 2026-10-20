import { HttpBackend, HttpEvent, HttpRequest, HttpResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { Observable, Subject } from 'rxjs';
import { AuthRefreshService } from './auth-refresh.service';
import { TokenService } from './token.service';

class RefreshHttpBackend implements HttpBackend {
  readonly requests: HttpRequest<unknown>[] = [];
  private readonly response$ = new Subject<HttpEvent<unknown>>();

  handle(request: HttpRequest<unknown>): Observable<HttpEvent<unknown>> {
    this.requests.push(request);
    return this.response$.asObservable();
  }

  respond(body: unknown): void {
    this.response$.next(new HttpResponse({ status: 200, body }));
    this.response$.complete();
  }
}

describe('AuthRefreshService', () => {
  let service: AuthRefreshService;
  let tokenService: TokenService;
  let backend: RefreshHttpBackend;

  beforeEach(() => {
    localStorage.clear();
    backend = new RefreshHttpBackend();

    TestBed.configureTestingModule({
      providers: [
        AuthRefreshService,
        TokenService,
        { provide: HttpBackend, useValue: backend }
      ]
    });

    service = TestBed.inject(AuthRefreshService);
    tokenService = TestBed.inject(TokenService);
    tokenService.updateTokens('access-anterior', 'refresh-anterior');
  });

  afterEach(() => localStorage.clear());

  it('comparte una sola renovación y guarda los tokens rotados', () => {
    const firstValues: string[] = [];
    const secondValues: string[] = [];

    service.refreshAccessToken().subscribe((token) => firstValues.push(token));
    service.refreshAccessToken().subscribe((token) => secondValues.push(token));

    expect(backend.requests.length).toBe(1);
    expect(backend.requests[0].body).toEqual({ refresh: 'refresh-anterior' });

    backend.respond({
      code: 200,
      message: 'Proceso realizado exitosamente',
      data: {
        access: 'access-nuevo',
        refresh: 'refresh-nuevo'
      }
    });

    expect(firstValues).toEqual(['access-nuevo']);
    expect(secondValues).toEqual(['access-nuevo']);
    expect(tokenService.getToken()).toBe('access-nuevo');
    expect(tokenService.getRefreshToken()).toBe('refresh-nuevo');
  });
});
