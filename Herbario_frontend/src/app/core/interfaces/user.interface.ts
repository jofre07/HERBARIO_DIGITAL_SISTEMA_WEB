export interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  role_ids: string[];
  roles: string[];
  permission_ids: string[];
  permissions: string[];
  effective_permissions?: string[];
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  is_active?: boolean;
  role_ids: string[];
  permission_ids?: string[];
}

export interface UserUpdate {
  username?: string;
  email?: string;
  password?: string;
  is_active?: boolean;
  role_ids?: string[];
  permission_ids?: string[];
}
