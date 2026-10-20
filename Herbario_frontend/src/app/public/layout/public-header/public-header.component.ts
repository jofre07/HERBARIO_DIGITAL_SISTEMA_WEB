import { Component, HostListener } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';

@Component({
  selector: 'app-public-header',
  standalone: true,
  imports: [CommonModule, RouterModule, UiTextPipe],
  templateUrl: './public-header.component.html',
  styleUrl: './public-header.component.scss'
})
export class PublicHeaderComponent {
  scrolled = false;
  isMenuOpen = false;

  @HostListener("window:scroll")
  onScroll(): void {
    this.scrolled = window.scrollY > 50;
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.closeMenu();
  }

  @HostListener('window:resize')
  onResize(): void {
    if (window.innerWidth >= 992) this.closeMenu();
  }

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  closeMenu(): void {
    this.isMenuOpen = false;
  }
}
