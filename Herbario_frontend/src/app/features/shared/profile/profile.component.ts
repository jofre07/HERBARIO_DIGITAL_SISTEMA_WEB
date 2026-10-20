import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { TokenService } from '../../../core/services/token.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [UiTextPipe, CommonModule],
  templateUrl: './profile.component.html',
  styleUrl: './profile.component.scss'
})
export class ProfileComponent {
  private tokenService = inject(TokenService);
  user = this.tokenService.getUser();
}
