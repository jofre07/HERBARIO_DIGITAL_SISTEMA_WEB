import { CommonModule } from '@angular/common';
import { Component, HostListener, OnDestroy, OnInit, inject } from '@angular/core';
import { FormArray, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ModalComponent } from '../../../components';
import { AboutContentCard, AboutPageContent, AboutPageContentUpdate } from '../../../core/interfaces/about-page-content.interface';
import { SiteContentService } from '../../../core/services/site-content.service';
import { TokenService } from '../../../core/services/token.service';
import { showError, showSuccess } from '../../../shared/utils/alerts';
import { ControlValidationMessageDirective } from '../../../shared/directives/control-validation-message.directive';

type CardForm = FormGroup<{
  title: FormControl<string>;
  description: FormControl<string>;
}>;

@Component({
  selector: 'app-about-content',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ModalComponent, ControlValidationMessageDirective],
  templateUrl: './about-content.component.html',
  styleUrl: './about-content.component.scss'
})
export class AboutContentComponent implements OnInit, OnDestroy {
  private readonly service = inject(SiteContentService);
  private readonly tokenService = inject(TokenService);
  private objectUrl: string | null = null;

  readonly canEdit = this.tokenService.hasPermission('site_content.change_aboutpagecontent');
  loading = true;
  saving = false;
  loadError = false;
  previewOpen = false;
  currentImageUrl: string | null = null;
  selectedImage: File | null = null;
  removeImage = false;
  imageError = '';

  readonly form = new FormGroup({
    introduction_title: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(160)] }),
    introduction_body: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(2000)] }),
    impact_items: new FormArray<CardForm>([]),
    mission: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(1500)] }),
    vision: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(1500)] }),
    values: new FormArray<FormControl<string>>([]),
    team_title: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(160)] }),
    team_subtitle: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(300)] }),
    team_members: new FormArray<CardForm>([]),
    contact_address: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(300)] }),
    contact_email: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.email] }),
    contact_phone: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(40)] }),
    institution: new FormControl('', { nonNullable: true, validators: [Validators.required, Validators.maxLength(160)] })
  });

  get impactItems(): FormArray<CardForm> { return this.form.controls.impact_items; }
  get teamMembers(): FormArray<CardForm> { return this.form.controls.team_members; }
  get values(): FormArray<FormControl<string>> { return this.form.controls.values; }
  get displayedImage(): string | null { return this.objectUrl || (!this.removeImage ? this.currentImageUrl : null); }

  ngOnInit(): void { this.loadContent(); }

  ngOnDestroy(): void { this.releaseObjectUrl(); }

  @HostListener('window:beforeunload', ['$event'])
  protectUnsavedChanges(event: BeforeUnloadEvent): void {
    if (this.form.dirty && !this.saving) event.preventDefault();
  }

  loadContent(): void {
    this.loading = true;
    this.loadError = false;
    this.service.getAdminAboutContent().subscribe({
      next: content => {
        this.fillForm(content);
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.loadError = true;
      }
    });
  }

  addValue(value = ''): void {
    if (this.values.length >= 10) return;
    this.values.push(new FormControl(value, { nonNullable: true, validators: [Validators.required, Validators.maxLength(120)] }));
    if (value === '') this.form.markAsDirty();
  }

  removeValue(index: number): void {
    if (this.values.length <= 1) return;
    this.values.removeAt(index);
    this.form.markAsDirty();
  }

  selectImage(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 10 * 1024 * 1024) {
      this.imageError = 'Selecciona una imagen JPG, PNG o WebP de máximo 10 MB.';
      input.value = '';
      return;
    }
    this.releaseObjectUrl();
    this.objectUrl = URL.createObjectURL(file);
    this.selectedImage = file;
    this.removeImage = false;
    this.imageError = '';
    this.form.markAsDirty();
  }

  clearImage(): void {
    this.releaseObjectUrl();
    this.selectedImage = null;
    this.removeImage = Boolean(this.currentImageUrl);
    this.form.markAsDirty();
  }

  save(): void {
    if (!this.canEdit || this.saving) return;
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      showError('Revisa el formulario', 'Completa correctamente todos los campos obligatorios.');
      return;
    }
    this.saving = true;
    this.service.updateAboutContent(this.form.getRawValue() as AboutPageContentUpdate, this.selectedImage, this.removeImage).subscribe({
      next: content => {
        this.fillForm(content);
        this.saving = false;
        showSuccess('Contenido actualizado', 'Los cambios ya están disponibles en la página pública.');
      },
      error: error => {
        this.saving = false;
        showError('No se pudo guardar', error?.error?.message || 'Verifica los datos e inténtalo nuevamente.');
      }
    });
  }

  private fillForm(content: AboutPageContent): void {
    this.impactItems.clear();
    content.impact_items.forEach(item => this.impactItems.push(this.createCard(item)));
    this.teamMembers.clear();
    content.team_members.forEach(item => this.teamMembers.push(this.createCard(item)));
    this.values.clear();
    content.values.forEach(value => this.addValue(value));
    this.form.patchValue(content);
    this.currentImageUrl = content.introduction_image_url;
    this.selectedImage = null;
    this.removeImage = false;
    this.releaseObjectUrl();
    this.form.markAsPristine();
  }

  private createCard(item: AboutContentCard): CardForm {
    return new FormGroup({
      title: new FormControl(item.title, { nonNullable: true, validators: [Validators.required, Validators.maxLength(160)] }),
      description: new FormControl(item.description, { nonNullable: true, validators: [Validators.required, Validators.maxLength(500)] })
    });
  }

  private releaseObjectUrl(): void {
    if (this.objectUrl) URL.revokeObjectURL(this.objectUrl);
    this.objectUrl = null;
  }
}
