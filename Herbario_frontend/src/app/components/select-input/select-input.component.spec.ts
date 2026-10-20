import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SelectInputComponent } from './select-input.component';

describe('SelectInputComponent', () => {
  let fixture: ComponentFixture<SelectInputComponent>;
  let component: SelectInputComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [SelectInputComponent] }).compileComponents();
    fixture = TestBed.createComponent(SelectInputComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('options', [
      { value: 'one', label: 'Primera opción' },
      { value: 'two', label: 'Segunda opción' }
    ]);
    fixture.componentRef.setInput('ariaLabel', 'Selector de prueba');
    fixture.detectChanges();
  });

  it('exposes an accessible label and listbox relationship', () => {
    const trigger = fixture.nativeElement.querySelector('.select-trigger') as HTMLButtonElement;

    expect(trigger.getAttribute('aria-label')).toBe('Selector de prueba');
    expect(trigger.getAttribute('aria-controls')).toBe(component.listboxId);
  });

  it('selects an option with the keyboard', () => {
    const trigger = fixture.nativeElement.querySelector('.select-trigger') as HTMLButtonElement;
    trigger.click();
    fixture.detectChanges();

    const option = fixture.nativeElement.querySelector('.option') as HTMLElement;
    option.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    fixture.detectChanges();

    expect(component.value()).toBe('one');
    expect(component.open()).toBeFalse();
  });
});
