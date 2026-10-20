import { ChangeDetectionStrategy, Component, Input } from "@angular/core";

export type TablePlaceholderColumnKind = 'text' | 'count' | 'badge' | 'image' | 'avatarText' | 'actions';

export interface TablePlaceholderColumn {
  kind?: TablePlaceholderColumnKind;
  width?: number;
  actionCount?: number;
}

@Component({
  selector: "tbody[appTablePlaceholder]",
  standalone: true,
  templateUrl: './table-placeholder.component.html',
  styleUrl: './table-placeholder.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    'aria-hidden': 'true'
  }
})
export class TablePlaceholderComponent {
  @Input() columns = 1;
  @Input() rows = 5;
  @Input() columnConfig: readonly TablePlaceholderColumn[] = [];

  get rowIndexes(): number[] {
    return Array.from({ length: Math.max(1, this.rows) }, (_, index) => index);
  }

  get columnIndexes(): number[] {
    return Array.from({ length: Math.max(1, this.columns) }, (_, index) => index);
  }

  get configuredColumns(): readonly TablePlaceholderColumn[] {
    return this.columnConfig.length
      ? this.columnConfig
      : this.columnIndexes.map(column => ({
          width: this.widthFor(column),
          kind: column === this.columnIndexes.length - 1 ? 'actions' : 'text'
        }));
  }

  widthFor(column: number): number {
    const widths = [74, 58, 86, 66, 48, 78];
    return widths[column % widths.length];
  }

  actionIndexes(column: TablePlaceholderColumn): number[] {
    return Array.from({ length: Math.max(1, column.actionCount ?? 2) }, (_, index) => index);
  }
}
