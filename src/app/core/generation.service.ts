import { Injectable } from '@angular/core';
import { ProjectBlueprintPayload } from '../models/project-blueprint';

@Injectable({ providedIn: 'root' })
export class GenerationService {
  // Placeholder method: integrate HTTP call later
  generate(payload: ProjectBlueprintPayload) {
    console.log('[GenerationService] would call backend with:', payload);
    // Return fake promise to simulate async
    return Promise.resolve(payload);
  }
}
