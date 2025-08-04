import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IncidentListComponent } from './incident-list.component';

describe('IncidentListComponent', () => {
  let component: IncidentListComponent;
  let fixture: ComponentFixture<IncidentListComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [IncidentListComponent]
    });
    fixture = TestBed.createComponent(IncidentListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
