import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-paint-splash-pill',
  templateUrl: './paint-splash-pill.component.html',
  styleUrls: ['./paint-splash-pill.component.scss']
})
export class PaintSplashPillComponent {
  @Input() text: string = '';
}
