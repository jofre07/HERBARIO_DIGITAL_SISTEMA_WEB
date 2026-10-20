import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from "@angular/common";
import { RouterModule } from "@angular/router";
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { SiteContentService } from '../../../core/services/site-content.service';
import { DEFAULT_ABOUT_PAGE_CONTENT } from '../../../core/interfaces/about-page-content.interface';

@Component({
  selector: 'app-public-footer',
  standalone: true,
  imports: [CommonModule, RouterModule, UiTextPipe],
  templateUrl: './public-footer.component.html',
  styleUrl: './public-footer.component.scss'
})
export class PublicFooterComponent implements OnInit {
  private readonly siteContentService = inject(SiteContentService);
  readonly currentYear = new Date().getFullYear();
  contact = {
    address: DEFAULT_ABOUT_PAGE_CONTENT.contact_address,
    email: DEFAULT_ABOUT_PAGE_CONTENT.contact_email,
    phone: DEFAULT_ABOUT_PAGE_CONTENT.contact_phone
  };

  ngOnInit(): void {
    this.siteContentService.getPublicAboutContent().subscribe({
      next: content => {
        this.contact = {
          address: content.contact_address,
          email: content.contact_email,
          phone: content.contact_phone
        };
      },
      error: () => undefined
    });
  }

  get telephoneHref(): string {
    return `tel:${this.contact.phone.replace(/[^+\d]/g, '')}`;
  }
}
