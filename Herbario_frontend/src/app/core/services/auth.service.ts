import { Injectable, inject } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable, map } from 'rxjs';
import { environment } from '../../../environments/environment';
import { LoginRequest, LoginResponse, LoginData } from '../interfaces/auth.interface';
import { TokenService } from './token.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private tokenService = inject(TokenService);
  private api = environment.apiURL;

  login(payload: LoginRequest): Observable<LoginData> {
    return this.http.post<LoginResponse>(`${this.api}/token/`, payload).pipe(
      map((response) => {
        const data = response.data!;
        this.tokenService.saveSession(data.access, data.refresh, data.user);
        return data;
      })
    );
  }

  logout(): void {
    this.tokenService.clear();
  }
}
