import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { unwrapData } from '../helpers/response.helper';
import { AboutPageContent, AboutPageContentUpdate } from '../interfaces/about-page-content.interface';

@Injectable({ providedIn: 'root' })
export class SiteContentService {
  private readonly http = inject(HttpClient);
  private readonly publicUrl = `${environment.apiURL}/public/content/about/`;
  private readonly adminUrl = `${environment.apiURL}/content/about/`;
  private publicRequest?: Observable<AboutPageContent>;

  getPublicAboutContent(refresh = false): Observable<AboutPageContent> {
    if (!this.publicRequest || refresh) {
      this.publicRequest = this.http.get<unknown>(this.publicUrl).pipe(
        unwrapData<AboutPageContent>(),
        shareReplay({ bufferSize: 1, refCount: false })
      );
    }
    return this.publicRequest;
  }

  getAdminAboutContent(): Observable<AboutPageContent> {
    return this.http.get<unknown>(this.adminUrl).pipe(unwrapData<AboutPageContent>());
  }

  updateAboutContent(payload: AboutPageContentUpdate, image?: File | null, removeImage = false): Observable<AboutPageContent> {
    const formData = new FormData();
    Object.entries(payload).forEach(([key, value]) => {
      formData.append(key, Array.isArray(value) ? JSON.stringify(value) : value);
    });
    if (image) formData.append('introduction_image', image);
    formData.append('remove_introduction_image', String(removeImage));
    return this.http.patch<unknown>(this.adminUrl, formData).pipe(
      unwrapData<AboutPageContent>(),
      tap(() => { this.publicRequest = undefined; })
    );
  }
}
