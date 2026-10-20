import { User } from './user.interface';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface WrappedResponse<T> {
  code: number;
  message: string;
  data?: T;
  errors?: unknown;
}

export interface LoginData {
  access: string;
  refresh: string;
  user: User;
}

export type LoginResponse = WrappedResponse<LoginData>;

export interface RefreshRequest {
  refresh: string;
}

export interface RefreshData {
  access: string;
  refresh?: string;
}

export type RefreshResponse = WrappedResponse<RefreshData>;

export interface JwtPayload {
  token_type: string;
  exp: number;
  iat: number;
  jti: string;
  user_id: number;
  username: string;
  roles: string[];
}
