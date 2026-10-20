import { CommonModule } from "@angular/common";
import { Component, EventEmitter, Input, Output } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';

@Component({
  selector: 'app-page-size-selector',
  standalone: true,
  imports: [CommonModule, FormsModule, UiTextPipe],
  template: "\n    <label class=\"page-size-control\">\n      <span>{{ 'dynamic.pageSize.show' | uiText }}</span>\n      <select\n        class=\"form-select form-select-sm\"\n        [ngModel]=\"pageSize\"\n        (ngModelChange)=\"changePageSize($event)\"\n        [attr.aria-label]=\"'dynamic.pageSize.ariaLabel' | uiText\"\n      >\n        <option *ngFor=\"let option of options\" [ngValue]=\"option\">{{ option }}</option>\n      </select>\n      <span>{{ 'dynamic.pageSize.records' | uiText }}</span>\n    </label>\n  ",
  styles: ["\n    .page-size-control {\n      display: inline-flex;\n      align-items: center;\n      gap: .55rem;\n      margin: 0;\n      color: #64748b;\n      font-size: .875rem;\n      white-space: nowrap;\n    }\n\n    .form-select {\n      width: 4.75rem;\n      min-height: 2.25rem;\n      color: #334155;\n      font-weight: 600;\n      border-color: #dbe3ec;\n      border-radius: .65rem;\n      box-shadow: none;\n    }\n\n    .form-select:focus {\n      border-color: var(--green-500);\n      box-shadow: 0 0 0 .2rem rgba(76, 175, 80, .12);\n    }\n  "]
})
export class PageSizeSelectorComponent {
  @Input() pageSize = 10;
  @Input() options: number[] = [5, 10, 20, 50];
  @Output() pageSizeChange = new EventEmitter<number>();

  changePageSize(value: number | string): void {
    const parsedValue = Number(value);
    if (Number.isFinite(parsedValue) && parsedValue > 0 && parsedValue !== this.pageSize) {
      this.pageSizeChange.emit(parsedValue);
    }
  }
}
