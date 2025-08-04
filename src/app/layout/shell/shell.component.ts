import { Component, OnInit, OnDestroy } from '@angular/core';
import { BreakpointObserver } from '@angular/cdk/layout';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { ThemeService } from '../../core/theme.service';

@Component({
  selector: 'app-shell',
  templateUrl: './shell.component.html',
  styleUrls: ['./shell.component.scss']
})
export class ShellComponent implements OnInit, OnDestroy {
  isMobile = false;
  private destroy$ = new Subject<void>();

  constructor(
    public theme: ThemeService,
    private breakpointObserver: BreakpointObserver
  ) {}

  ngOnInit() {
    // Watch for mobile breakpoint changes
    this.breakpointObserver.observe(['(max-width: 768px)']) // Changed to 768px to match CSS
      .pipe(takeUntil(this.destroy$))
      .subscribe(result => {
        this.isMobile = result.matches;
        console.log('isMobile:', this.isMobile, 'screen width check:', result.matches); // Debug log
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}