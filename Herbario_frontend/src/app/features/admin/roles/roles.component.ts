import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, computed, inject, signal } from "@angular/core";
import {
  FormModalComponent,
  HasPermissionDirective,
  PageSizeSelectorComponent,
  PaginationComponent,
  SelectInputComponent,
  SelectInputOption,
  TableActionsComponent,
  TablePlaceholderColumn,
  TablePlaceholderComponent,
  TableSearchComponent
} from '../../../components';
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { RoleService } from '../../../core/services/role.service';
import { Permission } from '../../../core/interfaces/permission.interface';
import { translatePermission } from '../../../core/helpers/permission-label.helper';
import { showConfirm, showError, showSuccess } from '../../../shared/utils/alerts';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';
import { handleFormApiError, lettersSpacesValidator } from '../../../shared/utils/form-validation';

@Component({
  selector: 'app-roles',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, SelectInputComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './roles.component.html',
  styleUrl: './roles.component.scss'
})
export class RolesComponent implements OnInit {
  private service = inject(RoleService);
  private fb = inject(FormBuilder);

  items: any[] = [];
  readonly permissions = signal<Permission[]>([]);
  readonly loadingPermissions = signal(false);
  readonly expandedRoleIds = signal<ReadonlySet<string>>(new Set<string>());
  selectedId: string | null = null;
  readonly formModalOpen = signal(false);
  loading = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 58 },
    { kind: 'badge' },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(150), lettersSpacesValidator]],
    permission_ids: [[] as string[]]
  });

  readonly permissionOptions = computed<SelectInputOption[]>(() =>
    this.permissions()
      .map(permission => ({
        value: permission.id,
        label: translatePermission(permission).optionLabel,
        searchText: `${permission.name} ${permission.codename} ${permission.permission}`
      }))
      .sort((a, b) => a.label.localeCompare(b.label, 'es'))
  );

  permissionLabel(permission: string): string {
    return translatePermission(permission).label;
  }

  visiblePermissions(item: any): string[] {
    const permissions = item.permissions || [];
    return this.isExpanded(item.id) ? permissions : permissions.slice(0, 4);
  }

  remainingPermissions(item: any): number {
    return Math.max(0, (item.permissions || []).length - 4);
  }

  isExpanded(roleId: string): boolean {
    return this.expandedRoleIds().has(roleId);
  }

  togglePermissions(roleId: string): void {
    this.expandedRoleIds.update(current => {
      const next = new Set(current);
      next.has(roleId) ? next.delete(roleId) : next.add(roleId);
      return next;
    });
  }

  ngOnInit(): void {
    this.loadData();
    this.loadPermissions();
  }

  loadPermissions(): void {
    this.loadingPermissions.set(true);
    this.service.getPermissions().subscribe({
      next: res => {
        this.permissions.set(res.results || []);
        this.loadingPermissions.set(false);
      },
      error: err => {
        this.permissions.set([]);
        this.loadingPermissions.set(false);
        showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.admin.roles.roles.no_se_pudieron_cargar_los_permisos'));
      }
    });
  }

  loadData(): void {
    this.loading = true;
    this.service.getAll(this.currentPage, this.pageSize, this.searchQuery).subscribe({
      next: (res) => {
        this.items = res.results || [];
        console.log(this.items);
        this.totalItems = res.count || 0;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.loadData();
  }

  onSearch(query: string): void {
    this.searchQuery = query;
    this.currentPage = 1;
    this.loadData();
  }
  openCreateModal(): void {
    this.selectedId = null;
    this.form.reset({ name: '', permission_ids: [] });
    this.formModalOpen.set(true);
  }


  edit(item: any): void {
    this.selectedId = item.id;
    this.form.patchValue({
      name: item.name,
      permission_ids: item.permission_ids || []
    });
    this.formModalOpen.set(true);
  }

  resetForm(): void {
    this.selectedId = null;
    this.form.reset({ permission_ids: [] });
    this.formModalOpen.set(false);
  }

  save(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.form.value as any;
    if (this.selectedId) {
      this.service.update(this.selectedId, payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.admin.roles.roles.actualizado'), res.message || translateUiText('code.features.admin.roles.roles.rol_actualizado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.admin.roles.roles.error_al_actualizar_rol')))
      });
    } else {
      this.service.create(payload).subscribe({
        next: (res) => {
          showSuccess(translateUiText('code.features.admin.roles.roles.creado'), res.message || translateUiText('code.features.admin.roles.roles.rol_creado_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.admin.roles.roles.error_al_crear_rol')))
      });
    }
  }

  async remove(item: any): Promise<void> {
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.admin.roles.roles.estas_seguro_de_eliminar_este_rol'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.admin.roles.roles.eliminado'), res.message || translateUiText('code.features.admin.roles.roles.rol_eliminado_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.admin.roles.roles.error_al_eliminar_rol'))
    });
  }
}
