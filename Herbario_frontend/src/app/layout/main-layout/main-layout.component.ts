import { translateUiText } from '../../core/services/ui-text.service';
import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { Component, HostListener, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule, Router } from "@angular/router";
import { TokenService } from '../../core/services/token.service';
import { AuthService } from '../../core/services/auth.service';
import { ModalComponent } from '../../components';
import { showConfirm } from '../../shared/utils/alerts';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [UiTextPipe, CommonModule, RouterModule, ModalComponent],
  templateUrl: './main-layout.component.html',
  styleUrl: './main-layout.component.scss'
})
export class MainLayoutComponent {
  private tokenService = inject(TokenService);
  private authService = inject(AuthService);
  private router = inject(Router);

  user = this.tokenService.getUser();
  sidebarCollapsed = false;
  mobileSidebarOpen = false;
  profileModalOpen = false;

  toggleSidebar(): void {
    if (this.isMobileViewport()) {
      this.mobileSidebarOpen = !this.mobileSidebarOpen;
      return;
    }
    this.sidebarCollapsed = !this.sidebarCollapsed;
  }

  closeMobileSidebar(): void {
    this.mobileSidebarOpen = false;
  }

  @HostListener('window:resize')
  onViewportResize(): void {
    if (this.isMobileViewport()) {
      this.sidebarCollapsed = false;
    } else {
      this.mobileSidebarOpen = false;
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.closeMobileSidebar();
  }

  async logout(): Promise<void> {
    const confirmed = await showConfirm(
      'Cerrar sesión',
      '¿Estás seguro de que quieres cerrar tu sesión?'
    );
    if (!confirmed.isConfirmed) return;

    this.profileModalOpen = false;
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  openProfileModal(): void {
    this.profileModalOpen = true;
  }

  closeProfileModal(): void {
    this.profileModalOpen = false;
  }

  get userInitials(): string {
    const username = this.user?.username?.trim();
    return username ? username.slice(0, 2).toUpperCase() : translateUiText('code.layout.main_layout.main_layout.us');
  }

  get isUserActive(): boolean {
    return this.user?.is_active !== false;
  }

  get isSidebarExpanded(): boolean {
    return this.isMobileViewport() ? this.mobileSidebarOpen : !this.sidebarCollapsed;
  }

  hasRole(roles: string[]): boolean {
    return this.tokenService.hasRole(roles);
  }

  hasPermission(permission: string): boolean {
    return this.tokenService.hasPermission(permission);
  }

  private isMobileViewport(): boolean {
    return window.matchMedia('(max-width: 991.98px)').matches;
  }
}
