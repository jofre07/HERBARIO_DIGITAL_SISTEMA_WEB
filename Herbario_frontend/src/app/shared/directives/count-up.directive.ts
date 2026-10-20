import { Directive, ElementRef, Input, NgZone, OnChanges, OnDestroy, inject } from "@angular/core";

@Directive({
  selector: "[appCountUp]",
  standalone: true
})
export class CountUpDirective implements OnChanges, OnDestroy {
  private readonly element = inject(ElementRef<HTMLElement>);
  private readonly zone = inject(NgZone);
  private readonly formatter = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
  private animationFrame: number | null = null;

  @Input({ required: true }) appCountUp: number | string | null | undefined = 0;
  @Input() countUpDuration = 1000;

  ngOnChanges(): void {
    this.startAnimation();
  }

  ngOnDestroy(): void {
    this.cancelAnimation();
  }

  private startAnimation(): void {
    this.cancelAnimation();

    const parsedValue = Number(this.appCountUp ?? 0);
    const target = Number.isFinite(parsedValue) ? Math.max(0, Math.round(parsedValue)) : 0;
    const reduceMotion = typeof window === 'undefined'
      || window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reduceMotion || target === 0 || this.countUpDuration <= 0) {
      this.render(target);
      return;
    }

    this.render(0);
    this.zone.runOutsideAngular(() => {
      const startedAt = performance.now();

      const update = (now: number): void => {
        const progress = Math.min((now - startedAt) / this.countUpDuration, 1);
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        this.render(Math.round(target * easedProgress));

        if (progress < 1) {
          this.animationFrame = requestAnimationFrame(update);
        } else {
          this.animationFrame = null;
        }
      };

      this.animationFrame = requestAnimationFrame(update);
    });
  }

  private render(value: number): void {
    this.element.nativeElement.textContent = this.formatter.format(value);
  }

  private cancelAnimation(): void {
    if (this.animationFrame !== null && typeof cancelAnimationFrame !== 'undefined') {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
  }
}
