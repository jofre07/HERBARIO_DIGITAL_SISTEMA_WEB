import { translateUiText } from '../../core/services/ui-text.service';
import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import { Component, DestroyRef, EventEmitter, Input, Output, inject } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { Subject, debounceTime, distinctUntilChanged } from 'rxjs';

@Component({
  selector: 'app-table-search',
  standalone: true,
  imports: [UiTextPipe, CommonModule],
  templateUrl: './table-search.component.html',
  styleUrl: './table-search.component.scss'
})
export class TableSearchComponent {
  private readonly destroyRef = inject(DestroyRef);
  private readonly queryChanges = new Subject<string>();

  @Input() query = '';
  @Input() placeholder = translateUiText('code.components.table_search.table_search.buscar_en_la_tabla');
  @Output() queryChange = new EventEmitter<string>();

  constructor() {
    this.queryChanges.pipe(
      debounceTime(350),
      distinctUntilChanged(),
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(query => this.queryChange.emit(query));
  }

  updateQuery(event: Event): void {
    this.queryChanges.next((event.target as HTMLInputElement).value);
  }

  clear(): void {
    this.queryChanges.next('');
  }
}
