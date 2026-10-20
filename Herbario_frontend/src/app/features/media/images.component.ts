import { translateUiText } from '../../core/services/ui-text.service';
import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { Component, HostListener, OnDestroy, OnInit, inject } from "@angular/core";
import { FormModalComponent, HasPermissionDirective, ModalComponent, PageSizeSelectorComponent, PaginationComponent, TableActionsComponent, TablePlaceholderColumn, TablePlaceholderComponent, TableSearchComponent } from '../../components';
import { CommonModule } from "@angular/common";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { HerbariumImageService } from '../../core/services/herbarium-image.service';
import { showConfirm, showError, showSuccess } from '../../shared/utils/alerts';
import { ControlValidationMessageDirective } from '../../shared/directives/control-validation-message.directive';
import { handleFormApiError, noHtmlValidator } from '../../shared/utils/form-validation';
import { forkJoin } from 'rxjs';
import { AdminImageAsset, AdminImageListItem, AdminSpecimenOption } from '../../core/interfaces/herbarium-image.interface';

@Component({
  selector: 'app-images',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective, PaginationComponent, PageSizeSelectorComponent, TableActionsComponent, TablePlaceholderComponent, FormModalComponent, ModalComponent, HasPermissionDirective, TableSearchComponent],
  templateUrl: './images.component.html',
  styleUrl: './images.component.scss'
})
export class ImagesComponent implements OnInit, OnDestroy {
  readonly maxImagesPerSpecimen = 5;
  readonly maxFileSize = 10 * 1024 * 1024;
  readonly acceptedImageTypes = ['image/jpeg', 'image/png', 'image/webp'];
  private service = inject(HerbariumImageService);
  private fb = inject(FormBuilder);

  items: AdminImageListItem[] = [];
  specimens: AdminSpecimenOption[] = [];
  selectedFiles: File[] = [];
  imagePreviews: string[] = [];
  editingImages: AdminImageAsset[] = [];
  deletingImageId: string | null = null;
  addingToExisting = false;
  fileError = '';
  specimenImageCount = 0;
  checkingImageCount = false;
  loadingSpecimens = false;
  selectedId: string | null = null;
  previewedImage: AdminImageListItem | null = null;
  previewImages: AdminImageAsset[] = [];
  loadingImageDetail = false;
  previewImageIndex = 0;
  formModalOpen = false;
  loading = false;
  saving = false;
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  searchQuery = '';
  readonly tablePlaceholderColumns: readonly TablePlaceholderColumn[] = [
    { kind: 'text', width: 82 },
    { kind: 'image' },
    { kind: 'text', width: 72 },
    { kind: 'actions', actionCount: 2 }
  ];

  form = this.fb.group({
    specimen_id: ['', Validators.required],
    credit: ['', [Validators.maxLength(255), noHtmlValidator]]
  });

  ngOnInit(): void {
    this.loadData();
  }

  ngOnDestroy(): void {
    this.clearPreviews();
  }

  get remainingSlots(): number {
    return Math.max(0, this.maxImagesPerSpecimen - this.specimenImageCount);
  }

  get galleryImages(): AdminImageAsset[] {
    return this.previewImages;
  }

  get hasMultipleImages(): boolean {
    return this.galleryImages.length > 1;
  }

  get activePreviewImage(): AdminImageAsset | null {
    return this.galleryImages[this.previewImageIndex] || null;
  }

  loadData(): void {
    this.loading = true;
    this.service.getAdminList(this.currentPage, this.pageSize, this.searchQuery, {}, true).subscribe({
      next: (res) => {
        this.items = res.results || [];
        this.totalItems = res.count || 0;
        this.loading = false;
      },
      error: () => this.loading = false
    });
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.loadData();
  }

  onSearch(query: string): void {
    this.searchQuery = query;
    this.currentPage = 1;
    this.loadData();
  }

  openImagePreview(item: AdminImageListItem): void {
    this.previewedImage = item;
    this.previewImageIndex = 0;
    this.previewImages = [];
    this.loadingImageDetail = true;
    this.service.getAdminDetail(item.specimen_id, true).subscribe({
      next: detail => {
        this.previewImages = detail.images;
        this.loadingImageDetail = false;
      },
      error: () => {
        this.loadingImageDetail = false;
        this.closeImagePreview();
        showError('Error', 'No se pudieron cargar las imágenes del espécimen.');
      }
    });
  }

  closeImagePreview(): void {
    this.previewedImage = null;
    this.previewImageIndex = 0;
    this.previewImages = [];
    this.loadingImageDetail = false;
  }

  showPreviousImage(): void {
    this.moveImagePreview(-1);
  }

  showNextImage(): void {
    this.moveImagePreview(1);
  }

  showImageAt(index: number): void {
    if (this.galleryImages[index]) this.previewImageIndex = index;
  }

  @HostListener('document:keydown.arrowleft', ['$event'])
  onPreviousImageKey(event: KeyboardEvent): void {
    if (!this.previewedImage || !this.hasMultipleImages) return;
    event.preventDefault();
    this.showPreviousImage();
  }

  @HostListener('document:keydown.arrowright', ['$event'])
  onNextImageKey(event: KeyboardEvent): void {
    if (!this.previewedImage || !this.hasMultipleImages) return;
    event.preventDefault();
    this.showNextImage();
  }
  openCreateModal(): void {
    this.selectedId = null;
    this.editingImages = [];
    this.addingToExisting = false;
    this.form.reset();
    this.resetSelectedFiles();
    this.specimenImageCount = 0;
    this.formModalOpen = true;
    this.ensureSpecimenOptions();
  }


  edit(item: AdminImageListItem): void {
    this.editingImages = [];
    this.selectedId = item.cover?.id || null;
    this.addingToExisting = true;
    this.form.patchValue({
      specimen_id: item.specimen_id,
      credit: ''
    });
    this.resetSelectedFiles();
    this.specimenImageCount = item.image_count;
    this.loadingImageDetail = true;
    this.formModalOpen = true;
    this.ensureSpecimenOptions();
    this.service.getAdminDetail(item.specimen_id, true).subscribe({
      next: detail => {
        this.editingImages = detail.images;
        this.selectedId = detail.images[0]?.id || null;
        this.loadingImageDetail = false;
      },
      error: () => {
        this.loadingImageDetail = false;
        this.resetForm();
        showError('Error', 'No se pudieron cargar las imágenes del espécimen.');
      }
    });
  }

  resetForm(): void {
    this.selectedId = null;
    this.form.reset();
    this.resetSelectedFiles();
    this.specimenImageCount = 0;
    this.editingImages = [];
    this.deletingImageId = null;
    this.addingToExisting = false;
    this.loadingImageDetail = false;
    this.formModalOpen = false;
  }

  async removeExistingImage(image: AdminImageAsset): Promise<void> {
    const confirmed = await showConfirm('Eliminar imagen', '¿Estás seguro de eliminar esta imagen?');
    if (!confirmed.isConfirmed) return;

    this.deletingImageId = image.id;
    this.service.delete(image.id).subscribe({
      next: () => {
        this.editingImages = this.editingImages.filter(item => item.id !== image.id);
        this.specimenImageCount = Math.max(0, this.specimenImageCount - 1);
        this.deletingImageId = null;
        this.resetSelectedFiles();
        if (!this.editingImages.length) {
          this.resetForm();
        } else if (this.selectedId === image.id) {
          this.selectedId = this.editingImages[0].id;
        }
        this.loadData();
        showSuccess('Imagen eliminada', 'La imagen se eliminó correctamente.');
      },
      error: (err) => {
        this.deletingImageId = null;
        showError('Error', err.error?.message || 'No se pudo eliminar la imagen.');
      }
    });
  }

  onSpecimenChange(specimenId: string): void {
    this.resetSelectedFiles();
    this.loadSpecimenImageCount(specimenId);
  }

  onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = Array.from(input.files || []);
    input.value = '';
    this.fileError = '';

    if (!this.form.controls.specimen_id.value) {
      this.fileError = 'Selecciona primero un espécimen.';
      return;
    }
    const invalidType = files.find(file => !this.acceptedImageTypes.includes(file.type));
    if (invalidType) {
      this.fileError = 'Solo se permiten imágenes JPG, PNG o WEBP.';
      return;
    }
    const oversized = files.find(file => file.size > this.maxFileSize);
    if (oversized) {
      this.fileError = 'Cada imagen debe pesar como máximo 10 MB.';
      return;
    }
    const allowedFiles = this.remainingSlots;
    if (files.length > allowedFiles) {
      this.fileError = `Este espécimen solo tiene ${allowedFiles} cupo(s) disponible(s).`;
      return;
    }

    this.setSelectedFiles(files);
  }

  removeSelectedFile(index: number): void {
    this.setSelectedFiles(this.selectedFiles.filter((_, fileIndex) => fileIndex !== index));
  }

  save(): void {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const specimenId = this.form.controls.specimen_id.value as string;
    const credit = this.form.controls.credit.value || '';
    if (!this.selectedFiles.length) {
      this.fileError = 'Selecciona al menos una imagen.';
      return;
    }
    if (this.selectedId && !this.addingToExisting) {
      this.saving = true;
      this.service.update(this.selectedId, {
        specimen_id: specimenId,
        image: this.selectedFiles[0],
        credit
      }).subscribe({
        next: (res) => {
          this.saving = false;
          showSuccess(translateUiText('code.features.collections.collections.actualizada'), res.message || translateUiText('code.features.media.images.imagen_actualizada_correctamente'));
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => {
          this.saving = false;
          showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.media.images.error_al_actualizar_imagen')));
        }
      });
    } else {
      const uploads = this.selectedFiles.map(image => this.service.create({
        specimen_id: specimenId,
        image,
        credit
      }));
      this.saving = true;
      forkJoin(uploads).subscribe({
        next: () => {
          this.saving = false;
          showSuccess(
            translateUiText('code.features.collections.collections.creada'),
            translateUiText('code.features.media.images.imagen_creada_correctamente'),
          );
          this.resetForm();
          this.currentPage = 1;
          this.loadData();
        },
        error: (err) => {
          this.saving = false;
          showError(translateUiText('code.features.admin.roles.roles.error'), handleFormApiError(this.form, err, translateUiText('code.features.media.images.error_al_crear_imagen')));
        }
      });
    }
  }

  async remove(item: AdminImageListItem): Promise<void> {
    if (!item.cover) return;
    const confirmed = await showConfirm(translateUiText('actions.delete'), translateUiText('code.features.media.images.estas_seguro_de_eliminar_esta_imagen'));
    if (!confirmed.isConfirmed) return;
    this.service.delete(item.cover.id).subscribe({
      next: (res) => {
        showSuccess(translateUiText('code.features.collections.collections.eliminada'), res.message || translateUiText('code.features.media.images.imagen_eliminada_correctamente'));
        if (this.items.length === 1 && this.currentPage > 1) this.currentPage--;
        this.loadData();
      },
      error: (err) => showError(translateUiText('code.features.admin.roles.roles.error'), err.error?.message || translateUiText('code.features.media.images.error_al_eliminar_imagen'))
    });
  }

  private loadSpecimenImageCount(specimenId: string): void {
    if (!specimenId) {
      this.specimenImageCount = 0;
      return;
    }
    this.checkingImageCount = true;
    this.service.getAdminDetail(specimenId, true).subscribe({
      next: detail => {
        this.specimenImageCount = detail.images.length;
        this.checkingImageCount = false;
      },
      error: () => {
        this.specimenImageCount = 0;
        this.checkingImageCount = false;
      }
    });
  }

  private ensureSpecimenOptions(): void {
    if (this.specimens.length || this.loadingSpecimens) return;

    this.loadingSpecimens = true;
    this.service.getAdminSpecimenOptions().subscribe({
      next: specimens => {
        this.specimens = specimens;
        this.loadingSpecimens = false;
      },
      error: () => {
        this.loadingSpecimens = false;
        showError('Error', 'No se pudo cargar la lista de especímenes.');
      }
    });
  }

  private moveImagePreview(direction: -1 | 1): void {
    if (!this.galleryImages.length) return;
    this.previewImageIndex = (this.previewImageIndex + direction + this.galleryImages.length) % this.galleryImages.length;
  }

  private setSelectedFiles(files: File[]): void {
    this.clearPreviews();
    this.selectedFiles = files;
    this.imagePreviews = files.map(file => URL.createObjectURL(file));
  }

  private resetSelectedFiles(): void {
    this.setSelectedFiles([]);
    this.fileError = '';
  }

  private clearPreviews(): void {
    this.imagePreviews.forEach(preview => URL.revokeObjectURL(preview));
    this.imagePreviews = [];
  }
}
