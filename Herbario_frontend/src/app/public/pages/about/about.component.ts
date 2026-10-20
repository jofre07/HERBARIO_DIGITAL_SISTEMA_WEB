import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { PublicBreadcrumbComponent } from '../../../components';
import { SiteContentService } from '../../../core/services/site-content.service';
import { AboutPageContent, DEFAULT_ABOUT_PAGE_CONTENT } from '../../../core/interfaces/about-page-content.interface';

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [CommonModule, UiTextPipe, PublicBreadcrumbComponent],
  templateUrl: './about.component.html',
  styleUrl: './about.component.scss'
})
export class AboutComponent implements OnInit {
  private readonly siteContentService = inject(SiteContentService);
  content: AboutPageContent = DEFAULT_ABOUT_PAGE_CONTENT;
  readonly impactIcons = ['bi-leaf', 'bi-search', 'bi-mortarboard', 'bi-people'];
  readonly teamIcons = ['bi-person-badge', 'bi-flower1', 'bi-search', 'bi-database'];

  ngOnInit(): void {
    this.siteContentService.getPublicAboutContent().subscribe({
      next: content => { this.content = content; },
      error: () => { this.content = DEFAULT_ABOUT_PAGE_CONTENT; }
    });
  }

  telephoneHref(phone: string): string {
    return `tel:${phone.replace(/[^+\d]/g, '')}`;
  }
}
