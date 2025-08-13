package com.projectforge.aipg.service;

import com.projectforge.aipg.agent.AgentOrchestrator;
import com.projectforge.aipg.agent.AgentResult;
import com.projectforge.aipg.model.ProjectBlueprint;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * Service for managing project generation lifecycle and file assembly
 */
@Service
public class ProjectGenerationService {
    
    private static final Logger logger = LoggerFactory.getLogger(ProjectGenerationService.class);
    
    private final AgentOrchestrator agentOrchestrator;
    
    // In-memory storage for session data (use Redis or database in production)
    private final Map<String, ProjectBlueprint> blueprintCache = new ConcurrentHashMap<>();
    private final Map<String, GenerationSession> sessionCache = new ConcurrentHashMap<>();
    private final Map<String, byte[]> backendZipCache = new ConcurrentHashMap<>();
    private final Map<String, byte[]> frontendZipCache = new ConcurrentHashMap<>();
    
    public ProjectGenerationService(AgentOrchestrator agentOrchestrator) {
        this.agentOrchestrator = agentOrchestrator;
    }
    
    /**
     * Start project generation process asynchronously
     */
    public CompletableFuture<Void> generateProjectAsync(String sessionId, Map<String, Object> config) {
        return CompletableFuture.runAsync(() -> {
            try {
                logger.info("Starting project generation for session: {}", sessionId);
                
                ProjectBlueprint blueprint = blueprintCache.get(sessionId);
                if (blueprint == null) {
                    throw new IllegalStateException("No blueprint found for session: " + sessionId);
                }
                
                // Initialize generation session
                GenerationSession session = new GenerationSession(sessionId);
                session.setStatus(GenerationStatus.GENERATING);
                session.setStartTime(System.currentTimeMillis());
                sessionCache.put(sessionId, session);
                
                // Run all agents through orchestrator
                List<AgentResult> results = agentOrchestrator.orchestrateProject(blueprint);
                
                // Process agent results and create ZIP files
                createProjectZips(sessionId, results);
                
                // Update session status
                session.setStatus(GenerationStatus.COMPLETED);
                session.setEndTime(System.currentTimeMillis());
                session.setResults(results);
                
                logger.info("Project generation completed for session: {}", sessionId);
                
            } catch (Exception e) {
                logger.error("Project generation failed for session: {}", sessionId, e);
                
                GenerationSession session = sessionCache.get(sessionId);
                if (session != null) {
                    session.setStatus(GenerationStatus.FAILED);
                    session.setError(e.getMessage());
                    session.setEndTime(System.currentTimeMillis());
                }
                
                throw new RuntimeException("Project generation failed", e);
            }
        });
    }
    
    /**
     * Get generation status for a session
     */
    public Map<String, Object> getGenerationStatus(String sessionId) {
        GenerationSession session = sessionCache.get(sessionId);
        
        if (session == null) {
            return Map.of(
                "sessionId", sessionId,
                "status", "NOT_FOUND",
                "error", "Session not found"
            );
        }
        
        Map<String, Object> status = new HashMap<>();
        status.put("sessionId", sessionId);
        status.put("status", session.getStatus().name());
        status.put("startTime", session.getStartTime());
        
        if (session.getEndTime() != null) {
            status.put("endTime", session.getEndTime());
            status.put("duration", session.getEndTime() - session.getStartTime());
        }
        
        if (session.getError() != null) {
            status.put("error", session.getError());
        }
        
        if (session.getResults() != null) {
            status.put("agentResults", session.getResults().size());
            status.put("successfulAgents", 
                session.getResults().stream().mapToLong(r -> r.isSuccess() ? 1 : 0).sum());
        }
        
        return status;
    }
    
    /**
     * Get generated backend ZIP
     */
    public byte[] getBackendZip(String sessionId) {
        return backendZipCache.get(sessionId);
    }
    
    /**
     * Get generated frontend ZIP
     */
    public byte[] getFrontendZip(String sessionId) {
        return frontendZipCache.get(sessionId);
    }
    
    /**
     * Get project blueprint for session
     */
    public ProjectBlueprint getProjectBlueprint(String sessionId) {
        return blueprintCache.get(sessionId);
    }
    
    /**
     * Cancel generation for session
     */
    public boolean cancelGeneration(String sessionId) {
        GenerationSession session = sessionCache.get(sessionId);
        
        if (session != null && session.getStatus() == GenerationStatus.GENERATING) {
            session.setStatus(GenerationStatus.CANCELLED);
            session.setEndTime(System.currentTimeMillis());
            return true;
        }
        
        return false;
    }
    
    /**
     * Store blueprint for session
     */
    public void storeBlueprintForSession(String sessionId, ProjectBlueprint blueprint) {
        blueprintCache.put(sessionId, blueprint);
    }
    
    /**
     * Create ZIP files from agent results
     */
    private void createProjectZips(String sessionId, List<AgentResult> results) throws IOException {
        logger.info("Creating project ZIP files for session: {}", sessionId);
        
        Map<String, String> backendFiles = new HashMap<>();
        Map<String, String> frontendFiles = new HashMap<>();
        
        // Process agent results and categorize files
        for (AgentResult result : results) {
            if (result.isSuccess()) {
                categorizeGeneratedFiles(result, backendFiles, frontendFiles);
            }
        }
        
        // Create backend ZIP
        byte[] backendZip = createZipFromFiles(backendFiles);
        backendZipCache.put(sessionId, backendZip);
        
        // Create frontend ZIP
        byte[] frontendZip = createZipFromFiles(frontendFiles);
        frontendZipCache.put(sessionId, frontendZip);
        
        logger.info("ZIP files created successfully for session: {}", sessionId);
    }
    
    /**
     * Categorize generated files into backend and frontend
     */
    private void categorizeGeneratedFiles(AgentResult result, 
                                        Map<String, String> backendFiles, 
                                        Map<String, String> frontendFiles) {
        
        String agentName = result.getAgentName();
        Object outputObj = result.getOutput();
        String output = outputObj != null ? outputObj.toString() : "";
        
        // Parse agent output and extract files
        // This would involve parsing JSON or structured output from agents
        
        if (agentName.contains("Backend") || agentName.contains("Database") || agentName.contains("DevOps")) {
            // Add to backend files
            backendFiles.put("generated/" + agentName + ".txt", output);
        } else if (agentName.contains("Frontend")) {
            // Add to frontend files
            frontendFiles.put("generated/" + agentName + ".txt", output);
        } else {
            // Add to both (shared configurations, documentation, etc.)
            backendFiles.put("shared/" + agentName + ".txt", output);
            frontendFiles.put("shared/" + agentName + ".txt", output);
        }
    }
    
    /**
     * Create ZIP file from file map
     */
    private byte[] createZipFromFiles(Map<String, String> files) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        
        try (ZipOutputStream zos = new ZipOutputStream(baos)) {
            for (Map.Entry<String, String> entry : files.entrySet()) {
                ZipEntry zipEntry = new ZipEntry(entry.getKey());
                zos.putNextEntry(zipEntry);
                zos.write(entry.getValue().getBytes());
                zos.closeEntry();
            }
        }
        
        return baos.toByteArray();
    }
    
    /**
     * Generation session tracking
     */
    private static class GenerationSession {
        private String sessionId;
        private GenerationStatus status;
        private Long startTime;
        private Long endTime;
        private String error;
        private List<AgentResult> results;
        
        public GenerationSession(String sessionId) {
            this.sessionId = sessionId;
        }
        
        // Getters and setters
        public String getSessionId() { return sessionId; }
        public GenerationStatus getStatus() { return status; }
        public void setStatus(GenerationStatus status) { this.status = status; }
        public Long getStartTime() { return startTime; }
        public void setStartTime(Long startTime) { this.startTime = startTime; }
        public Long getEndTime() { return endTime; }
        public void setEndTime(Long endTime) { this.endTime = endTime; }
        public String getError() { return error; }
        public void setError(String error) { this.error = error; }
        public List<AgentResult> getResults() { return results; }
        public void setResults(List<AgentResult> results) { this.results = results; }
    }
    
    /**
     * Generation status enumeration
     */
    private enum GenerationStatus {
        PROCESSING, GENERATING, COMPLETED, FAILED, CANCELLED
    }
}
