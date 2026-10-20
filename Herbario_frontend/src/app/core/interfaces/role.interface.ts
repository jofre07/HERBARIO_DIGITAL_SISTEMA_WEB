import { Permission } from './permission.interface';

export interface Role {
  id: string;
  name: string;
  permission_ids: string[];
  permissions: string[];
}

export interface RoleWrite {
  name: string;
  permission_ids?: string[];
}
