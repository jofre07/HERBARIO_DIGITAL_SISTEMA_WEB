import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ControlValidationMessageDirective } from './control-validation-message.directive';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, ControlValidationMessageDirective],
  template: '<form [formGroup]="form"><input formControlName="name" /></form>'
})
class TestFormComponent {
  form = new FormGroup({ name: new FormControl('', Validators.required) });
}

describe('ControlValidationMessageDirective', () => {
  let fixture: ComponentFixture<TestFormComponent>;
  let component: TestFormComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [TestFormComponent] }).compileComponents();
    fixture = TestBed.createComponent(TestFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('removes an obsolete message and marks a corrected input as valid', () => {
    const input: HTMLInputElement = fixture.nativeElement.querySelector('input');
    const control = component.form.controls.name;

    control.markAsTouched();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.auto-validation-message')).not.toBeNull();
    expect(input.classList).toContain('is-invalid');

    control.setValue('Español');
    control.markAsDirty();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.auto-validation-message')).toBeNull();
    expect(input.classList).not.toContain('is-invalid');
    expect(input.classList).toContain('is-valid');
  });

  it('clears validation state when the form is reset', () => {
    const input: HTMLInputElement = fixture.nativeElement.querySelector('input');
    const control = component.form.controls.name;
    control.markAsTouched();
    fixture.detectChanges();

    component.form.reset();
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.auto-validation-message')).toBeNull();
    expect(input.classList).not.toContain('is-invalid');
    expect(input.classList).not.toContain('is-valid');
  });
});
