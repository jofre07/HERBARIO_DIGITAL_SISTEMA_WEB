import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { ChangeDetectionStrategy, Component, Input, inject } from "@angular/core";
import { Params, RouterModule } from "@angular/router";
import { UiTextService } from '../../core/services/ui-text.service';

export interface PublicBreadcrumbItem {
  label: string;
  route?: string | any[];
  queryParams?: Params;
}

@Component({
  selector: 'app-public-breadcrumb',
  standalone: true,
  imports: [UiTextPipe, RouterModule],
  templateUrl: './public-breadcrumb.component.html',
  styleUrl: './public-breadcrumb.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class PublicBreadcrumbComponent {
  private readonly texts = inject(UiTextService);
  @Input() current = '';
  @Input() items: readonly PublicBreadcrumbItem[] = [];

  get levels(): readonly PublicBreadcrumbItem[] {
    if (this.items.length) return this.items;

    return [
      { label: this.texts.get('navigation.home'), route: '/' },
      { label: this.current }
    ];
  }
}
