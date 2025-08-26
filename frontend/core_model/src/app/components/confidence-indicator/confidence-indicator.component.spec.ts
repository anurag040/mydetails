import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { ConfidenceIndicatorComponent } from './confidence-indicator.component';

describe('ConfidenceIndicatorComponent', () => {
  let component: ConfidenceIndicatorComponent;
  let fixture: ComponentFixture<ConfidenceIndicatorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConfidenceIndicatorComponent, NoopAnimationsModule]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConfidenceIndicatorComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should calculate confidence metrics correctly', () => {
    component.confidence = {
      score: 0.85,
      explanation: 'Test explanation',
      factors: ['Factor 1', 'Factor 2']
    };
    
    component.ngOnInit();
    
    expect(component.confidencePercentage).toBe(85);
    expect(component.confidenceLevel).toBe('High');
    expect(component.confidenceColor).toBe('#8bc34a');
  });

  it('should handle different confidence levels', () => {
    const testCases = [
      { score: 0.95, expectedLevel: 'Excellent', expectedColor: '#4caf50' },
      { score: 0.85, expectedLevel: 'High', expectedColor: '#8bc34a' },
      { score: 0.75, expectedLevel: 'Good', expectedColor: '#ffc107' },
      { score: 0.65, expectedLevel: 'Moderate', expectedColor: '#ff9800' },
      { score: 0.45, expectedLevel: 'Low', expectedColor: '#f44336' }
    ];

    testCases.forEach(testCase => {
      component.confidence = {
        score: testCase.score,
        explanation: 'Test',
        factors: []
      };
      
      component.ngOnInit();
      
      expect(component.confidenceLevel).toBe(testCase.expectedLevel);
      expect(component.confidenceColor).toBe(testCase.expectedColor);
    });
  });
});
