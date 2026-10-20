import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Input,
  OnChanges,
  OnDestroy,
  Output,
  SimpleChanges,
  ViewChild
} from '@angular/core';

@Component({
  selector: 'app-public-filter-drawer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './public-filter-drawer.component.html',
  styleUrl: './public-filter-drawer.component.scss'
})
export class PublicFilterDrawerComponent implements OnChanges, AfterViewInit, OnDestroy {
  @Input() open = false;
  @Input() context = '';
  @Input() title = 'Filtros';
  @Input() description = 'Refina los resultados mostrados';
  @Input() applyLabel = 'Aplicar filtros';
  @Input() clearLabel = 'Limpiar filtros';
  @Input() closeLabel = 'Cerrar filtros';
  @Input() loading = false;
  @Input() canClear = false;

  @Output() closed = new EventEmitter<void>();
  @Output() cleared = new EventEmitter<void>();
  @Output() applied = new EventEmitter<void>();

  @ViewChild('panel') private panel?: ElementRef<HTMLElement>;
  @ViewChild('closeButton') private closeButton?: ElementRef<HTMLButtonElement>;

  private previousActiveElement: HTMLElement | null = null;

  ngAfterViewInit(): void {
    if (this.open) this.activateDrawer();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (!changes['open']) return;
    if (this.open) {
      this.previousActiveElement = document.activeElement as HTMLElement | null;
      document.body.classList.add('public-filter-drawer-open');
      requestAnimationFrame(() => this.activateDrawer());
    } else {
      document.body.classList.remove('public-filter-drawer-open');
    }
  }

  ngOnDestroy(): void {
    document.body.classList.remove('public-filter-drawer-open');
  }

  requestClose(): void {
    if (this.loading) return;
    this.closed.emit();
    requestAnimationFrame(() => this.previousActiveElement?.focus());
  }

  requestApply(): void {
    if (this.loading) return;
    this.applied.emit();
    requestAnimationFrame(() => this.previousActiveElement?.focus());
  }

  @HostListener('document:keydown', ['$event'])
  handleKeyboard(event: KeyboardEvent): void {
    if (!this.open) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      this.requestClose();
      return;
    }
    if (event.key !== 'Tab') return;

    const focusable = this.getFocusableElements();
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  private activateDrawer(): void {
    document.body.classList.add('public-filter-drawer-open');
    this.closeButton?.nativeElement.focus();
  }

  private getFocusableElements(): HTMLElement[] {
    const selector = 'button:not([disabled]), input:not([disabled]), select:not([disabled]), [href], [tabindex]:not([tabindex="-1"])';
    return Array.from(this.panel?.nativeElement.querySelectorAll<HTMLElement>(selector) || [])
      .filter(element => element.offsetParent !== null);
  }
}
