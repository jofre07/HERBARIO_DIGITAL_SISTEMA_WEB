import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
  name: "tableFilter",
  standalone: true
})
export class TableFilterPipe implements PipeTransform {
  transform<T>(items: readonly T[] | null | undefined, query: string): T[] {
    if (!items) return [];

    const normalizedQuery = this.normalize(query.trim());
    if (!normalizedQuery) return [...items];

    return items.filter(item => this.normalize(this.toSearchText(item)).includes(normalizedQuery));
  }

  private toSearchText(value: unknown): string {
    if (value == null) return '';
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      return String(value);
    }
    if (Array.isArray(value)) return value.map(item => this.toSearchText(item)).join(' ');
    if (typeof value === 'object') {
      return Object.values(value as Record<string, unknown>)
        .map(item => this.toSearchText(item))
        .join(' ');
    }
    return '';
  }

  private normalize(value: string): string {
    return value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, '')
      .toLocaleLowerCase('es');
  }
}
