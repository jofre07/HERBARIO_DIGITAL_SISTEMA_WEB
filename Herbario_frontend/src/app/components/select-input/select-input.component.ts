import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import {
  Component,
  ElementRef,
  HostListener,
  OnDestroy,
  ViewChild,
  computed,
  forwardRef,
  input,
  signal
} from "@angular/core";
import { ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR } from "@angular/forms";
import { translateUiText } from '../../core/services/ui-text.service';

export interface SelectInputOption {
  value: string;
  label: string;
  searchText?: string;
}

let nextSelectInputId = 0;

@Component({
  selector: 'app-select-input',
  standalone: true,
  imports: [UiTextPipe, CommonModule, FormsModule],
  templateUrl: './select-input.component.html',
  styleUrl: './select-input.component.scss',
  providers: [{
    provide: NG_VALUE_ACCESSOR,
    useExisting: forwardRef(() => SelectInputComponent),
    multi: true
  }]
})
export class SelectInputComponent implements ControlValueAccessor, OnDestroy {
  readonly options = input<SelectInputOption[]>([]);
  readonly controlId = input<string>();
  readonly ariaLabel = input<string>();
  readonly placeholder = input("Selecciona una opción");
  readonly searchPlaceholder = input("Buscar...");
  readonly searchable = input(false);
  readonly multiple = input(false);
  readonly panelMode = input<'overlay' | 'inline' | 'fixed'>('overlay');
  readonly emptyText = input("No hay opciones disponibles");
  readonly disabled = input(false);
  readonly maxVisibleChips = input(3);
  readonly listboxId = `select-input-listbox-${nextSelectInputId++}`;

  readonly open = signal(false);
  readonly searchTerm = signal('');
  readonly value = signal<string | string[] | null>(null);
  readonly disabledByForm = signal(false);
  readonly fixedPanelStyle = signal<Record<string, string>>({});
  readonly overlayOpenUpward = signal(false);

  readonly isDisabled = computed(() => this.disabled() || this.disabledByForm());
  readonly filteredOptions = computed(() => {
    const term = this.normalize(this.searchTerm());
    if (!term) return this.options();
    return this.options().filter(option =>
      this.normalize(`${option.label} ${option.searchText || ''}`).includes(term)
    );
  });
  readonly selectedOptions = computed(() =>
    this.options().filter(option => this.isSelected(option.value))
  );
  readonly selectedCount = computed(() => this.selectedOptions().length);
  readonly visibleSelectedOptions = computed(() =>
    this.selectedOptions().slice(0, this.maxVisibleChips())
  );
  readonly hiddenSelectedCount = computed(() =>
    Math.max(0, this.selectedCount() - this.visibleSelectedOptions().length)
  );
  readonly displayValue = computed(() => {
    const selected = this.selectedOptions();
    if (!selected.length) return this.placeholder();
    if (!this.multiple()) return selected[0].label;
    if (selected.length <= 2) return selected.map(option => option.label).join(', ');
    return translateUiText('dynamic.selection.selectedOptions', { count: selected.length });
  });

  @ViewChild('trigger') trigger?: ElementRef<HTMLButtonElement>;

  private onChange: (value: string | string[] | null) => void = () => undefined;
  private onTouched: () => void = () => undefined;

  constructor(private elementRef: ElementRef<HTMLElement>) {}

  ngOnDestroy(): void {
    this.setModalOverlayVisible(false);
  }

  toggleOpen(): void {
    if (this.isDisabled()) return;
    this.open.update(open => !open);
    if (this.panelMode() === 'overlay') this.setModalOverlayVisible(this.open());
    if (this.open() && this.panelMode() === 'fixed') {
      this.fixedPanelStyle.set({});
      requestAnimationFrame(() => this.positionFixedPanel());
    } else if (this.open() && this.panelMode() === 'overlay') {
      requestAnimationFrame(() => this.positionOverlayPanel());
    } else if (!this.open()) {
      this.finishInteraction();
    }
  }

  select(optionValue: string): void {
    if (this.isDisabled()) return;
    const normalizedValue = String(optionValue);

    if (this.multiple()) {
      const current = Array.isArray(this.value()) ? [...(this.value() as string[])].map(String) : [];
      this.value.set(current.includes(normalizedValue)
        ? current.filter(value => value !== normalizedValue)
        : [...current, normalizedValue]);
    } else {
      this.value.set(normalizedValue);
      this.open.set(false);
      this.setModalOverlayVisible(false);
    }

    const currentValue = this.value();
    this.onChange(Array.isArray(currentValue) ? [...currentValue] : currentValue);
    this.onTouched();
  }

  removeSelection(event: MouseEvent, optionValue: string): void {
    event.preventDefault();
    event.stopPropagation();
    if (this.isDisabled() || !this.isSelected(optionValue)) return;
    this.select(optionValue);
  }

  selectFromKeyboard(event: KeyboardEvent, optionValue: string): void {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    event.preventDefault();
    event.stopPropagation();
    this.select(optionValue);
  }

  removeSelectionFromKeyboard(event: KeyboardEvent, optionValue: string): void {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    event.preventDefault();
    event.stopPropagation();
    if (this.isDisabled() || !this.isSelected(optionValue)) return;
    this.select(optionValue);
  }

  isSelected(optionValue: string): boolean {
    const normalizedValue = String(optionValue);
    const currentValue = this.value();
    return Array.isArray(currentValue)
      ? currentValue.map(String).includes(normalizedValue)
      : currentValue != null && String(currentValue) === normalizedValue;
  }

  writeValue(value: string | string[] | null): void {
    this.value.set(Array.isArray(value)
      ? [...value].map(String)
      : value == null
        ? (this.multiple() ? [] : null)
        : String(value));
  }

  registerOnChange(fn: (value: string | string[] | null) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(disabled: boolean): void {
    this.disabledByForm.set(disabled);
    if (disabled) this.open.set(false);
  }

  @HostListener("document:click", ["$event"])
  closeFromOutside(event: MouseEvent): void {
    if (this.open() && !this.elementRef.nativeElement.contains(event.target as Node)) {
      this.open.set(false);
      this.finishInteraction();
    }
  }

  @HostListener("window:resize")
  repositionOnResize(): void {
    if (!this.open()) return;
    if (this.panelMode() === 'fixed') this.positionFixedPanel();
    if (this.panelMode() === 'overlay') this.positionOverlayPanel();
  }

  updateSearchTerm(term: string): void {
    this.searchTerm.set(term);
    if (this.panelMode() === 'fixed') {
      requestAnimationFrame(() => this.positionFixedPanel());
    } else if (this.panelMode() === 'overlay') {
      requestAnimationFrame(() => this.positionOverlayPanel());
    }
  }

  private finishInteraction(): void {
    this.setModalOverlayVisible(false);
    this.searchTerm.set('');
    this.onTouched();
  }

  private setModalOverlayVisible(visible: boolean): void {
    const modalPanel = this.elementRef.nativeElement.closest<HTMLElement>('.app-modal-panel');
    modalPanel?.classList.toggle('select-overlay-open', visible);
  }

  private normalize(value: string): string {
    return value.normalize("NFD").replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  }

  private positionOverlayPanel(): void {
    const trigger = this.trigger?.nativeElement;
    const panel = this.elementRef.nativeElement.querySelector<HTMLElement>('.select-panel');
    if (!trigger || !panel) return;

    const boundary = this.elementRef.nativeElement.closest<HTMLElement>('.app-modal-body, .drawer-body');
    const triggerRect = trigger.getBoundingClientRect();
    const boundaryRect = boundary?.getBoundingClientRect()
      ?? { top: 0, bottom: window.innerHeight };
    const desiredHeight = Math.min(panel.scrollHeight, 280);
    const spaceBelow = boundaryRect.bottom - triggerRect.bottom - 8;
    const spaceAbove = triggerRect.top - boundaryRect.top - 8;

    this.overlayOpenUpward.set(spaceBelow < desiredHeight && spaceAbove > spaceBelow);
  }

  private positionFixedPanel(): void {
    const trigger = this.trigger?.nativeElement;
    if (!trigger) return;
    const rect = trigger.getBoundingClientRect();
    const panel = this.elementRef.nativeElement.querySelector<HTMLElement>('.select-panel');
    if (!panel) return;
    const viewportPadding = 12;
    const maximumPanelHeight = Math.min(330, window.innerHeight - viewportPadding * 2);
    const panelHeight = Math.min(panel.scrollHeight, maximumPanelHeight);
    const spaceBelow = window.innerHeight - rect.bottom - viewportPadding;
    const openUpward = spaceBelow < panelHeight && rect.top > spaceBelow;
    const top = openUpward
      ? Math.max(viewportPadding, rect.top - panelHeight - 6)
      : Math.min(rect.bottom + 6, window.innerHeight - panelHeight - viewportPadding);

    this.fixedPanelStyle.set({
      top: `${top}px`,
      left: `${rect.left}px`,
      width: `${rect.width}px`,
      maxHeight: `${maximumPanelHeight}px`
    });
  }
}
