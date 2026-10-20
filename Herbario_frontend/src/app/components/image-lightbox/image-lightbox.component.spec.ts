import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ImageLightboxComponent } from './image-lightbox.component';

describe('ImageLightboxComponent', () => {
  let fixture: ComponentFixture<ImageLightboxComponent>;
  let component: ImageLightboxComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImageLightboxComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ImageLightboxComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('images', [{ url: 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==', alt: 'Imagen de prueba' }]);
    fixture.detectChanges();
  });

  afterEach(() => fixture.destroy());

  it('does not close when the backdrop is clicked', () => {
    const closedSpy = spyOn(component.closed, 'emit');
    const backdrop = fixture.nativeElement.querySelector('.lightbox') as HTMLElement;

    backdrop.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));

    expect(closedSpy).not.toHaveBeenCalled();
  });

  it('does not close when Escape is pressed', () => {
    const closedSpy = spyOn(component.closed, 'emit');
    const panel = fixture.nativeElement.querySelector('.lightbox-panel') as HTMLElement;
    const closeButton = fixture.nativeElement.querySelector('.lightbox-close') as HTMLButtonElement;
    closeButton.focus();

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));

    expect(closedSpy).not.toHaveBeenCalled();
    expect(document.activeElement).toBe(panel);
  });

  it('closes from the close button', () => {
    const closedSpy = spyOn(component.closed, 'emit');
    const closeButton = fixture.nativeElement.querySelector('.lightbox-close') as HTMLButtonElement;

    closeButton.click();

    expect(closedSpy).toHaveBeenCalledTimes(1);
  });
});
