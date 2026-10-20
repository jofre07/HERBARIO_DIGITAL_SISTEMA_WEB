import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import { Component, EventEmitter, Input, Output } from "@angular/core";

type PaginationItem = number | 'ellipsis';

@Component({
  selector: 'app-pagination',
  standalone: true,
  imports: [UiTextPipe, CommonModule],
  templateUrl: './pagination.component.html',
  styleUrl: './pagination.component.scss'
})
export class PaginationComponent {
  @Input() currentPage = 1;
  @Input() totalItems = 0;
  @Input() pageSize = 10;
  @Input() itemLabel = 'registro';
  @Input() itemLabelPlural = 'registros';
  @Output() pageChange = new EventEmitter<number>();

  get displayedItemLabel(): string {
    return this.totalItems === 1 ? this.itemLabel : this.itemLabelPlural;
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.totalItems / this.pageSize));
  }

  get firstItem(): number {
    return this.totalItems ? (this.currentPage - 1) * this.pageSize + 1 : 0;
  }

  get lastItem(): number {
    return Math.min(this.currentPage * this.pageSize, this.totalItems);
  }

  get pages(): PaginationItem[] {
    const total = this.totalPages;
    if (total <= 7) {
      return Array.from({ length: total }, (_, index) => index + 1);
    }

    const pages: PaginationItem[] = [1];
    const start = Math.max(2, this.currentPage - 1);
    const end = Math.min(total - 1, this.currentPage + 1);

    if (start > 2) pages.push('ellipsis');
    for (let page = start; page <= end; page++) pages.push(page);
    if (end < total - 1) pages.push('ellipsis');
    pages.push(total);

    return pages;
  }

  goToPage(page: number): void {
    if (page !== this.currentPage && page >= 1 && page <= this.totalPages) {
      this.pageChange.emit(page);
    }
  }
}
