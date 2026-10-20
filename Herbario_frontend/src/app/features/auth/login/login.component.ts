import { translateUiText } from '../../../core/services/ui-text.service';
import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { Router, RouterLink } from "@angular/router";
import { AuthService } from '../../../core/services/auth.service';
import { showError } from '../../../shared/utils/alerts';
import { handleFormApiError } from '../../../shared/utils/form-validation';
import { SiteContentService } from '../../../core/services/site-content.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent implements OnInit {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);
  private siteContentService = inject(SiteContentService);

  loading = false;
  showPassword = false;
  menuOpen = false;
  aboutImageUrl: string | null = null;

  form = this.fb.group({
    username: ['', [Validators.required, Validators.maxLength(150)]],
    password: ['', [Validators.required]]
  });

  ngOnInit(): void {
    this.siteContentService.getPublicAboutContent().subscribe({
      next: content => { this.aboutImageUrl = content.introduction_image_url; },
      error: () => { this.aboutImageUrl = null; }
    });
  }

  closeMenu(): void {
    this.menuOpen = false;
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading = true;

    this.authService.login(this.form.getRawValue() as any).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/admin/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        const msg = handleFormApiError(this.form, err, translateUiText('messages.loginFailed'));
        showError(translateUiText('messages.accessDenied'), msg);
      }
    });
  }
}
