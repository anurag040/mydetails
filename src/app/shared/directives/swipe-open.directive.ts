import { Directive, Output, EventEmitter, HostListener } from '@angular/core';

export type SwipeDirection = 'left' | 'right' | 'up' | 'down';

@Directive({
  selector: '[appSwipeOpen]'
})
export class SwipeOpenDirective {
  private startX = 0;
  private startY = 0;
  private startTime = 0;
  private threshold = 50; // min distance px
  private allowedTime = 500; // max time ms

  @Output() swipeOpen = new EventEmitter<SwipeDirection>();

  @HostListener('pointerdown', ['$event'])
  onPointerDown(e: PointerEvent) {
    this.startX = e.clientX;
    this.startY = e.clientY;
    this.startTime = Date.now();
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  }

  @HostListener('pointerup', ['$event'])
  onPointerUp(e: PointerEvent) {
    const dx = e.clientX - this.startX;
    const dy = e.clientY - this.startY;
    const dt = Date.now() - this.startTime;
    if (dt > this.allowedTime) return;
    if (Math.abs(dx) >= this.threshold && Math.abs(dx) > Math.abs(dy)) {
      this.swipeOpen.emit(dx > 0 ? 'right' : 'left');
    } else if (Math.abs(dy) >= this.threshold && Math.abs(dy) > Math.abs(dx)) {
      this.swipeOpen.emit(dy > 0 ? 'down' : 'up');
    }
  }
}