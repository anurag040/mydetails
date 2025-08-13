package com.projectforge.aipg.controller;

import com.projectforge.aipg.agent.AgentOrchestrator;
import com.projectforge.aipg.model.ProjectBlueprint;
import com.projectforge.aipg.service.PRDProcessingService;
import com.projectforge.aipg.service.ProjectGenerationService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/**
 * REST Controller for handling PRD uploads and project generation
 */
@RestController
@RequestMapping("/api/projects")
public class ProjectGenerationController {
    
    private static final Logger logger = LoggerFactory.getLogger(ProjectGenerationController.class);
    
    private final PRDProcessingService prdProcessingService;
    private final ProjectGenerationService projectGenerationService;
    private final AgentOrchestrator agentOrchestrator;
    
    public ProjectGenerationController(
            PRDProcessingService prdProcessingService,
            ProjectGenerationService projectGenerationService,
            AgentOrchestrator agentOrchestrator) {
        this.prdProcessingService = prdProcessingService;
        this.projectGenerationService = projectGenerationService;
        this.agentOrchestrator = agentOrchestrator;
    }
    
    /**
     * Upload and process PRD document
     */
    @PostMapping("/upload-prd")
    public ResponseEntity<Map<String, Object>> uploadPRD(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "projectName", required = false) String projectName) {
        
        try {
            logger.info("Received PRD upload: {}", file.getOriginalFilename());
            
            // Validate file
            if (file.isEmpty()) {
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "File is empty"));
            }
            
            // Generate session ID for tracking
            String sessionId = UUID.randomUUID().toString();
            
            // Process PRD asynchronously and automatically start generation when done
            CompletableFuture<ProjectBlueprint> blueprintFuture = 
                prdProcessingService.processPRDAsync(file, projectName, sessionId);
            
            // Chain the project generation after PRD processing completes
            blueprintFuture.thenAccept(blueprint -> {
                if (blueprint != null) {
                    logger.info("PRD processing completed for session: {}, starting project generation", sessionId);
                    // Automatically start project generation with the blueprint
                    projectGenerationService.generateProjectFromBlueprint(sessionId, blueprint);
                } else {
                    logger.error("PRD processing failed for session: {}", sessionId);
                }
            });
            
            return ResponseEntity.accepted()
                .body(Map.of(
                    "sessionId", sessionId,
                    "message", "PRD upload successful. Processing and generation started.",
                    "status", "PROCESSING"
                ));
                
        } catch (Exception e) {
            logger.error("PRD upload failed", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "PRD upload failed: " + e.getMessage()));
        }
    }
    
    /**
     * Get PRD processing status
     */
    @GetMapping("/status/{sessionId}")
    public ResponseEntity<Map<String, Object>> getProcessingStatus(@PathVariable String sessionId) {
        try {
            Map<String, Object> status = projectGenerationService.getGenerationStatus(sessionId);
            return ResponseEntity.ok(status);
        } catch (Exception e) {
            logger.error("Failed to get status for session: {}", sessionId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Failed to get status: " + e.getMessage()));
        }
    }
    
    /**
     * Direct project generation endpoint without PRD upload
     */
    @PostMapping("/generate")
    public ResponseEntity<Map<String, Object>> generateDirectProject(
            @RequestBody Map<String, Object> request) {
        
        try {
            logger.info("Starting direct project generation");
            
            // Generate session ID for tracking
            String sessionId = UUID.randomUUID().toString();
            
            // Extract project configuration from request
            String projectName = (String) request.getOrDefault("projectName", "Generated Project");
            String projectType = (String) request.getOrDefault("projectType", "web-application");
            String description = (String) request.getOrDefault("description", "");
            
            // Start project generation asynchronously
            CompletableFuture<Map<String, String>> generationFuture = 
                projectGenerationService.generateDirectProjectAsync(sessionId, request);
            
            return ResponseEntity.accepted()
                .body(Map.of(
                    "sessionId", sessionId,
                    "message", "Project generation started",
                    "status", "GENERATING",
                    "projectName", projectName,
                    "projectType", projectType
                ));
                
        } catch (Exception e) {
            logger.error("Direct project generation failed", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Project generation failed: " + e.getMessage()));
        }
    }
    
    /**
     * Start project generation from processed PRD
     */
    @PostMapping("/generate/{sessionId}")
    public ResponseEntity<Map<String, Object>> generateProject(
            @PathVariable String sessionId,
            @RequestBody(required = false) Map<String, Object> config) {
        
        try {
            logger.info("Starting project generation for session: {}", sessionId);
            
            // Start project generation asynchronously
            CompletableFuture<Void> generationFuture = 
                projectGenerationService.generateProjectAsync(sessionId, config);
            
            return ResponseEntity.accepted()
                .body(Map.of(
                    "sessionId", sessionId,
                    "message", "Project generation started",
                    "status", "GENERATING"
                ));
                
        } catch (Exception e) {
            logger.error("Project generation failed for session: {}", sessionId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Project generation failed: " + e.getMessage()));
        }
    }
    
    /**
     * Download combined project ZIP (both backend and frontend)
     */
    @GetMapping("/download/{sessionId}")
    public ResponseEntity<byte[]> downloadProjectZip(@PathVariable String sessionId) {
        try {
            byte[] zipData = projectGenerationService.getCombinedProjectZip(sessionId);
            
            if (zipData == null) {
                return ResponseEntity.notFound().build();
            }
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
            headers.setContentDispositionFormData("attachment", sessionId + "-project.zip");
            headers.setContentLength(zipData.length);
            
            return new ResponseEntity<>(zipData, headers, HttpStatus.OK);
            
        } catch (Exception e) {
            logger.error("Project download failed for session: {}", sessionId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Download generated backend ZIP
     */
    @GetMapping("/download/backend/{sessionId}")
    public ResponseEntity<byte[]> downloadBackendZip(@PathVariable String sessionId) {
        try {
            byte[] zipData = projectGenerationService.getBackendZip(sessionId);
            
            if (zipData == null) {
                return ResponseEntity.notFound().build();
            }
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
            headers.setContentDispositionFormData("attachment", sessionId + "-backend.zip");
            headers.setContentLength(zipData.length);
            
            return new ResponseEntity<>(zipData, headers, HttpStatus.OK);
            
        } catch (Exception e) {
            logger.error("Backend download failed for session: {}", sessionId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Download generated frontend ZIP
     */
    @GetMapping("/download/frontend/{sessionId}")
    public ResponseEntity<byte[]> downloadFrontendZip(@PathVariable String sessionId) {
        try {
            byte[] zipData = projectGenerationService.getFrontendZip(sessionId);
            
            if (zipData == null) {
                return ResponseEntity.notFound().build();
            }
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
            headers.setContentDispositionFormData("attachment", sessionId + "-frontend.zip");
            headers.setContentLength(zipData.length);
            
            return new ResponseEntity<>(zipData, headers, HttpStatus.OK);
            
        } catch (Exception e) {
            logger.error("Frontend download failed for session: {}", sessionId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get generated project blueprint
     */
    @GetMapping("/blueprint/{sessionId}")
    public ResponseEntity<ProjectBlueprint> getProjectBlueprint(@PathVariable String sessionId) {
        try {
            ProjectBlueprint blueprint = projectGenerationService.getProjectBlueprint(sessionId);
            
            if (blueprint == null) {
                return ResponseEntity.notFound().build();
            }
            
            return ResponseEntity.ok(blueprint);
            
        } catch (Exception e) {
            logger.error("Blueprint retrieval failed for session: {}", sessionId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Cancel project generation
     */
    @PostMapping("/cancel/{sessionId}")
    public ResponseEntity<Map<String, Object>> cancelGeneration(@PathVariable String sessionId) {
        try {
            boolean cancelled = projectGenerationService.cancelGeneration(sessionId);
            
            if (cancelled) {
                return ResponseEntity.ok(Map.of(
                    "sessionId", sessionId,
                    "message", "Project generation cancelled",
                    "status", "CANCELLED"
                ));
            } else {
                return ResponseEntity.badRequest()
                    .body(Map.of("error", "Could not cancel generation for session: " + sessionId));
            }
            
        } catch (Exception e) {
            logger.error("Cancellation failed for session: {}", sessionId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", "Cancellation failed: " + e.getMessage()));
        }
    }
    
    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        return ResponseEntity.ok(Map.of(
            "status", "UP",
            "service", "AI Project Generator",
            "timestamp", System.currentTimeMillis()
        ));
    }
}
