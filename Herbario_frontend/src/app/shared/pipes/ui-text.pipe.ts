import { Pipe, PipeTransform, inject } from "@angular/core";
import { UiTextParameters, UiTextService } from '../../core/services/ui-text.service';

@Pipe({
  name: "uiText",
  standalone: true
})
export class UiTextPipe implements PipeTransform {
  private readonly texts = inject(UiTextService);

  transform(key: string, parameters?: UiTextParameters): string {
    return this.texts.get(key, parameters);
  }
}
