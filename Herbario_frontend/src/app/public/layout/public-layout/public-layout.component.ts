import { Component } from "@angular/core";
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { PublicHeaderComponent } from '../public-header/public-header.component';
import { PublicFooterComponent } from '../public-footer/public-footer.component';

@Component({
  selector: 'app-public-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, PublicHeaderComponent, PublicFooterComponent],
  template: "\n    <a class=\"skip-link\" href=\"#main-content\">Saltar al contenido principal</a>\n    <app-public-header />\n    <div class=\"public-page-content\" id=\"main-content\" tabindex=\"-1\">\n      <router-outlet />\n    </div>\n    <app-public-footer />\n  ",
  styles: ["\n    :host { display: flex; flex-direction: column; min-height: 100vh; min-height: 100dvh; }\n    .public-page-content { flex: 1 0 auto; }\n    .skip-link { position: fixed; z-index: 3000; top: .75rem; left: .75rem; padding: .7rem 1rem; color: #12351c; font-weight: 700; text-decoration: none; background: #fff; border-radius: .4rem; box-shadow: 0 8px 24px rgba(0,0,0,.2); transform: translateY(-160%); }\n    .skip-link:focus { transform: translateY(0); }\n    app-public-footer { flex-shrink: 0; }\n  "]
})
export class PublicLayoutComponent {}
