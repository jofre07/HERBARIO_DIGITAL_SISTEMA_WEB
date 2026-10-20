import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import { Component, OnInit, ViewChild, inject } from "@angular/core";
import { finalize } from 'rxjs';
import { Role } from '../../../core/interfaces/role.interface';
import {
  User,
  UserCreate,
  UserUpdate
} from '../../../core/interfaces/user.interface';
import { RoleService } from '../../../core/services/role.service';
import { UserService } from '../../../core/services/user.service';
import {
  ConfirmationModalComponent,
  FormModalComponent,
  HasPermissionDirective,
  PageSizeSelectorComponent,
  PaginationComponent,
  TableSearchComponent,
  TableActionsComponent,
  TablePlaceholderColumn,
  TablePlaceholderComponent,
  UserFormComponent
} from '../../../components';
import { showError, showSuccess } from '../../../shared/utils/alerts';
import { getApiErrorMessage, handleFormApiError } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [UiTextPipe, 
    CommonModule,
    PaginationComponent,
    PageSizeSelectorComponent,
    TableActionsComponent,
    TablePlaceholderComponent,
    ConfirmationModalComponent,
    FormModalComponent,
    UserFormComponent,
    HasPermissionDirective,
    TableSearchComponent,
  ],
  templateUrl: './users.component.html',
  styleUrl: './users.component.scss'
})
export class UsersComponent implements OnInit {
  @ViewChild(UserFormComponent) userForm?: UserFormComponent;
  private userService = inject(UserService);
  private roleService = inject(RoleService);

  users: User[] = [];
  roles: Role[] = [];
  selectedUser: User | null = null;
  userPendingDelete: User | null = null;

  loading = false;
  loadingRoles = false;
  saving = false;
  deleting = false;
  formModalOpen = false;
  deleteModalOpen = false;

  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly pageSizeOptions = [5, 10, 20, 50];
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'avatarText', width: 58 },
    { kind: 'text', width: 88 },
    { kind: 'badge' },
    { kind: 'badge' },
    { kind: 'actions', actionCount: 2 }
  ];

  ngOnInit(): void {
    this.loadUsers();
    this.loadRoles();
  }

  loadUsers(): void {
    this.loading = true;
    this.userService
      .getAll(this.currentPage, this.pageSize, this.searchQuery)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe({
        next: response => {
          this.users = response.results ?? [];
          this.totalItems = response.count ?? 0;
        },
        error: error => {
          this.users = [];
          this.totalItems = 0;
          showError(translateUiText('code.features.admin.users.users.no_se_pudieron_cargar_los_usuarios'), this.getErrorMessage(error));
        }
      });
  }

  loadRoles(): void {
    this.loadingRoles = true;
    this.roleService
      .getAll(1, 100)
      .pipe(finalize(() => (this.loadingRoles = false)))
      .subscribe({
        next: response => (this.roles = response.results ?? []),
        error: error => showError(translateUiText('code.features.admin.users.users.no_se_pudieron_cargar_los_roles'), this.getErrorMessage(error))
      });
  }

  openCreateModal(): void {
    this.selectedUser = null;
    this.formModalOpen = true;
  }

  openEditModal(user: User): void {
    this.selectedUser = user;
    this.formModalOpen = true;
  }

  closeFormModal(): void {
    if (this.saving) return;
    this.formModalOpen = false;
    this.selectedUser = null;
  }

  saveUser(payload: UserCreate | UserUpdate): void {
    if (this.saving) return;

    const editingUser = this.selectedUser;
    const request = editingUser
      ? this.userService.update(editingUser.id, payload as UserUpdate)
      : this.userService.create(payload as UserCreate);

    this.saving = true;
    request
      .pipe(finalize(() => (this.saving = false)))
      .subscribe({
        next: response => {
          this.formModalOpen = false;
          this.selectedUser = null;

          if (!editingUser) {
            this.currentPage = 1;
          }

          showSuccess(
            editingUser ? translateUiText('code.features.admin.users.users.usuario_actualizado') : translateUiText('code.features.admin.users.users.usuario_creado'),
            response?.message ||
              (editingUser
                ? translateUiText('code.features.admin.users.users.los_datos_del_usuario_se_actualizaron_correctame')
                : translateUiText('code.features.admin.users.users.el_usuario_se_registro_correctamente'))
          );
          this.loadUsers();
        },
        error: error => {
          showError(
            editingUser ? translateUiText('code.features.admin.users.users.no_se_pudo_actualizar') : translateUiText('code.features.admin.users.users.no_se_pudo_crear'),
            this.userForm
              ? handleFormApiError(this.userForm.form, error, translateUiText('code.features.admin.users.users.no_se_pudo_guardar_el_usuario'))
              : getApiErrorMessage(error, translateUiText('code.features.admin.users.users.no_se_pudo_guardar_el_usuario'))
          );
        }
      });
  }

  openDeleteModal(user: User): void {
    this.userPendingDelete = user;
    this.deleteModalOpen = true;
  }

  closeDeleteModal(): void {
    if (this.deleting) return;
    this.deleteModalOpen = false;
    this.userPendingDelete = null;
  }

  deleteUser(): void {
    if (!this.userPendingDelete || this.deleting) return;

    this.deleting = true;
    this.userService
      .delete(this.userPendingDelete.id)
      .pipe(finalize(() => (this.deleting = false)))
      .subscribe({
        next: response => {
          const shouldGoBack = this.users.length === 1 && this.currentPage > 1;
          this.deleteModalOpen = false;
          this.userPendingDelete = null;
          if (shouldGoBack) this.currentPage--;

          showSuccess(
            translateUiText('code.features.admin.users.users.usuario_eliminado'),
            response?.message || translateUiText('code.features.admin.users.users.el_usuario_fue_eliminado_correctamente')
          );
          this.loadUsers();
        },
        error: error => {
          showError(translateUiText('code.features.admin.users.users.no_se_pudo_eliminar'), this.getErrorMessage(error));
        }
      });
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.loadUsers();
  }

  onSearch(query: string): void {
    this.searchQuery = query;
    this.currentPage = 1;
    this.loadUsers();
  }

  changePageSize(pageSize: number): void {
    this.pageSize = pageSize;
    this.currentPage = 1;
    this.loadUsers();
  }

  getInitials(username: string): string {
    return username
      .split(/[\s._-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(part => part.charAt(0).toUpperCase())
      .join('');
  }

  trackByUserId(_: number, user: User): string {
    return user.id;
  }

  private getErrorMessage(error: any): string {
    const errors = error?.error?.errors;
    if (typeof errors?.detail === 'string') return errors.detail;

    if (errors && typeof errors === 'object') {
      const firstEntry = Object.entries(errors)[0];
      if (firstEntry) {
        const [field, value] = firstEntry;
        const detail = Array.isArray(value) ? value[0] : value;
        const labels: Record<string, string> = {
          username: "Nombre de usuario",
          email: "Correo",
          password: "Contraseña",
          role_ids: "Roles"
        };
        return `${labels[field] ?? field}: ${String(detail)}`;
      }
    }

    return error?.error?.message || translateUiText('code.features.admin.users.users.ocurrio_un_error_inesperado_intentalo_nuevamente');
  }
}
