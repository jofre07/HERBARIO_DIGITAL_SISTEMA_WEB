import { Directive, Input, TemplateRef, ViewContainerRef, inject } from "@angular/core";
import { TokenService } from '../../core/services/token.service';

@Directive({
  selector: "[appHasPermission]",
  standalone: true
})
export class HasPermissionDirective {
  private templateRef = inject(TemplateRef<unknown>);
  private viewContainer = inject(ViewContainerRef);
  private tokenService = inject(TokenService);
  private rendered = false;

  @Input() set appHasPermission(permission: string) {
    const allowed = this.tokenService.hasPermission(permission);
    if (allowed && !this.rendered) {
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.rendered = true;
    } else if (!allowed && this.rendered) {
      this.viewContainer.clear();
      this.rendered = false;
    }
  }
}
