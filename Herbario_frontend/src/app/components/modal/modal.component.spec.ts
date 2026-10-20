import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ModalComponent } from './modal.component';

describe('ModalComponent', () => {
  let fixture: ComponentFixture<ModalComponent>;
  let component: ModalComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModalComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ModalComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('open', true);
    fixture.componentRef.setInput('title', 'Modal de prueba');
    fixture.detectChanges();
  });

  afterEach(() => fixture.destroy());

  it('does not close when the backdrop is clicked', () => {
    const closedSpy = spyOn(component.closed, 'emit');
    const backdrop = fixture.nativeElement.querySelector('.app-modal-backdrop') as HTMLElement;

    backdrop.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(closedSpy).not.toHaveBeenCalled();
  });

  it('does not close when Escape is pressed', () => {
    const closedSpy = spyOn(component.closed, 'emit');
    const panel = fixture.nativeElement.querySelector('.app-modal-panel') as HTMLElement;
    const closeButton = fixture.nativeElement.querySelector('.app-modal-close') as HTMLButtonElement;
    closeButton.focus();

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));

    expect(closedSpy).not.toHaveBeenCalled();
    expect(document.activeElement).toBe(panel);
  });

  it('keeps initial focus on the dialog instead of the close button', async () => {
    await new Promise<void>((resolve) => setTimeout(resolve));

    const panel = fixture.nativeElement.querySelector('.app-modal-panel') as HTMLElement;
    expect(document.activeElement).toBe(panel);

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));

    expect(document.activeElement).toBe(panel);
  });

  it('closes from the close button', () => {
    const closedSpy = spyOn(component.closed, 'emit');
    const closeButton = fixture.nativeElement.querySelector('.app-modal-close') as HTMLButtonElement;

    closeButton.click();

    expect(closedSpy).toHaveBeenCalledTimes(1);
  });
});
