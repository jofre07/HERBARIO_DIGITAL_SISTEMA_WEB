import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { CommonModule, DOCUMENT } from "@angular/common";
import {
  Component,
  EventEmitter,
  HostListener,
  Inject,
  Input,
  OnChanges,
  OnDestroy,
  Output,
  SimpleChanges,
  ViewChild,
  ElementRef
} from "@angular/core";

let nextModalId = 0;

@Component({
  selector: 'app-modal',
  standalone: true,
  imports: [UiTextPipe, CommonModule],
  templateUrl: './modal.component.html',
  styleUrl: './modal.component.scss'
})
export class ModalComponent implements OnChanges, OnDestroy {
  @Input() open = false;
  @Input() title = '';
  @Input() subtitle = '';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() appearance: 'default' | 'lightbox' = 'default';
  @Input() closeDisabled = false;
  @Output() closed = new EventEmitter<void>();

  @ViewChild('modalPanel') modalPanel?: ElementRef<HTMLElement>;

  readonly titleId = `app-modal-title-${nextModalId}`;
  readonly subtitleId = `app-modal-subtitle-${nextModalId++}`;
  private previouslyFocusedElement: HTMLElement | null = null;

  constructor(@Inject(DOCUMENT) private document: Document) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['open']) {
      this.document.body.classList.toggle('app-modal-open', this.open);
      if (this.open) {
        this.previouslyFocusedElement = this.document.activeElement as HTMLElement | null;
        setTimeout(() => this.modalPanel?.nativeElement.focus());
      } else {
        this.restoreFocus();
      }
    }
  }

  ngOnDestroy(): void {
    this.document.body.classList.remove('app-modal-open');
    this.restoreFocus();
  }

  @HostListener('document:keydown', ['$event'])
  onDocumentKeydown(event: KeyboardEvent): void {
    if (!this.open) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      if (this.document.activeElement?.classList.contains('app-modal-close')) {
        this.modalPanel?.nativeElement.focus({ preventScroll: true });
      }
      return;
    }
    if (event.key === 'Tab') this.trapFocus(event);
  }

  close(): void {
    if (!this.open || this.closeDisabled) return;
    this.closed.emit();
  }

  private trapFocus(event: KeyboardEvent): void {
    const panel = this.modalPanel?.nativeElement;
    if (!panel) return;
    const focusableElements = Array.from(panel.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ));
    if (!focusableElements.length) {
      event.preventDefault();
      panel.focus();
      return;
    }
    const first = focusableElements[0];
    const last = focusableElements[focusableElements.length - 1];
    if (this.document.activeElement === panel) {
      event.preventDefault();
      (event.shiftKey ? last : first).focus();
    } else if (event.shiftKey && this.document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && this.document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  private restoreFocus(): void {
    if (this.previouslyFocusedElement?.isConnected) this.previouslyFocusedElement.focus();
    this.previouslyFocusedElement = null;
  }
}
