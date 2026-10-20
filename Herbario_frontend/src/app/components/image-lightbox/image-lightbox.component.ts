import { CommonModule } from '@angular/common';
import { AfterViewInit, Component, ElementRef, EventEmitter, HostListener, Input, OnDestroy, Output, ViewChild } from '@angular/core';

export interface LightboxImage {
  url: string;
  alt: string;
  title?: string;
  subtitle?: string;
}

@Component({
  selector: 'app-image-lightbox',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './image-lightbox.component.html',
  styleUrl: './image-lightbox.component.scss'
})
export class ImageLightboxComponent implements AfterViewInit, OnDestroy {
  @Input({ required: true }) images: LightboxImage[] = [];
  @Input() initialIndex = 0;
  @Output() closed = new EventEmitter<void>();
  @ViewChild('closeButton') private closeButton?: ElementRef<HTMLButtonElement>;
  @ViewChild('lightboxPanel') private lightboxPanel?: ElementRef<HTMLElement>;

  index = 0;
  private previouslyFocused: HTMLElement | null = null;

  ngAfterViewInit(): void {
    this.index = Math.min(Math.max(this.initialIndex, 0), Math.max(this.images.length - 1, 0));
    this.previouslyFocused = document.activeElement as HTMLElement | null;
    document.body.style.overflow = 'hidden';
    queueMicrotask(() => this.closeButton?.nativeElement.focus());
  }

  ngOnDestroy(): void {
    document.body.style.overflow = '';
    this.previouslyFocused?.focus();
  }

  get currentImage(): LightboxImage | null {
    return this.images[this.index] || null;
  }

  close(): void {
    this.closed.emit();
  }

  previous(): void {
    this.move(-1);
  }

  next(): void {
    this.move(1);
  }

  private move(direction: -1 | 1): void {
    if (this.images.length < 2) return;
    this.index = (this.index + direction + this.images.length) % this.images.length;
  }

  @HostListener('document:keydown', ['$event'])
  handleKeyboard(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
      event.preventDefault();
      if (document.activeElement === this.closeButton?.nativeElement) {
        this.lightboxPanel?.nativeElement.focus({ preventScroll: true });
      }
      return;
    }
    if (event.key === 'ArrowLeft') this.previous();
    if (event.key === 'ArrowRight') this.next();
    if (event.key === 'Tab') {
      const controls = Array.from(this.lightboxPanel?.nativeElement.querySelectorAll<HTMLButtonElement>('button:not(:disabled)') || []);
      if (!controls.length) return;
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  }
}
