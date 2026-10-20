import { UiTextPipe } from '../../shared/pipes/ui-text.pipe';
import { CommonModule } from "@angular/common";
import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
  inject
} from "@angular/core";
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators
} from "@angular/forms";
import { Role } from '../../core/interfaces/role.interface';
import { ControlValidationMessageDirective } from '../../shared/directives/control-validation-message.directive';
import { noHtmlValidator } from '../../shared/utils/form-validation';
import {
  User,
  UserCreate,
  UserUpdate
} from '../../core/interfaces/user.interface';

function atLeastOne(control: AbstractControl): ValidationErrors | null {
  return Array.isArray(control.value) && control.value.length > 0
    ? null
    : { atLeastOne: true };
}

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [UiTextPipe, CommonModule, ReactiveFormsModule, ControlValidationMessageDirective],
  templateUrl: './user-form.component.html',
  styleUrl: './user-form.component.scss'
})
export class UserFormComponent implements OnChanges {
  private fb = inject(FormBuilder);

  @Input() user: User | null = null;
  @Input() roles: Role[] = [];
  @Input() saving = false;
  @Output() submitted = new EventEmitter<UserCreate | UserUpdate>();

  showPassword = false;

  form = this.fb.group({
    username: this.fb.nonNullable.control('', [Validators.required, Validators.maxLength(150)]),
    email: this.fb.nonNullable.control('', [Validators.email, Validators.maxLength(254)]),
    password: this.fb.nonNullable.control('', [Validators.required, Validators.minLength(8), noHtmlValidator]),
    is_active: this.fb.nonNullable.control(true),
    role_ids: this.fb.nonNullable.control<string[]>([], [atLeastOne])
  });

  get editing(): boolean {
    return !!this.user;
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['user']) {
      this.prepareForm();
    }
  }

  isRoleSelected(roleId: string): boolean {
    return this.form.controls.role_ids.value.includes(roleId);
  }

  toggleRole(roleId: string): void {
    const current = this.form.controls.role_ids.value;
    const selected = current.includes(roleId);
    this.form.controls.role_ids.setValue(
      selected ? current.filter(id => id !== roleId) : [...current, roleId]
    );
    this.form.controls.role_ids.markAsTouched();
  }

  submit(): void {
    if (this.form.invalid || this.saving) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    if (this.editing) {
      const payload: UserUpdate = {
        username: value.username.trim(),
        email: value.email.trim(),
        is_active: value.is_active,
        role_ids: value.role_ids
      };

      if (value.password) {
        payload.password = value.password;
      }

      this.submitted.emit(payload);
      return;
    }

    this.submitted.emit({
      username: value.username.trim(),
      email: value.email.trim(),
      password: value.password,
      is_active: value.is_active,
      role_ids: value.role_ids
    });
  }

  private prepareForm(): void {
    this.showPassword = false;
    this.form.reset({
      username: this.user?.username ?? '',
      email: this.user?.email ?? '',
      password: '',
      is_active: this.user?.is_active ?? true,
      role_ids: this.user?.role_ids ?? []
    });

    const passwordControl = this.form.controls.password;
    passwordControl.setValidators(
      this.editing
        ? [Validators.minLength(8), noHtmlValidator]
        : [Validators.required, Validators.minLength(8), noHtmlValidator]
    );
    passwordControl.updateValueAndValidity();
  }
}
