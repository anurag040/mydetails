package com.projectforge.aipg.service;

import com.projectforge.aipg.agent.AgentOrchestrator;
import com.projectforge.aipg.agent.AgentResult;
import com.projectforge.aipg.model.ProjectBlueprint;
import com.projectforge.aipg.model.ProjectInfo;
import com.projectforge.aipg.model.TechnologyStack;
import com.projectforge.aipg.model.Feature;
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
     * Generate project from an existing blueprint (used after PRD processing)
     */
    public CompletableFuture<Void> generateProjectFromBlueprint(String sessionId, ProjectBlueprint blueprint) {
        return CompletableFuture.runAsync(() -> {
            try {
                logger.info("Starting project generation from blueprint for session: {}", sessionId);
                
                // Store the blueprint
                blueprintCache.put(sessionId, blueprint);
                
                // Initialize generation session
                GenerationSession session = new GenerationSession(sessionId);
                session.setStatus(GenerationStatus.GENERATING);
                session.setStartTime(System.currentTimeMillis());
                sessionCache.put(sessionId, session);
                
                // Generate the project using the orchestrator
                List<AgentResult> results = agentOrchestrator.orchestrateProject(blueprint);
                
                // Process results and create ZIP files
                createProjectZips(sessionId, results);
                
                // Update session status to COMPLETED
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
            }
        });
    }

    /**
     * Start direct project generation process asynchronously without PRD
     */
    public CompletableFuture<Map<String, String>> generateDirectProjectAsync(String sessionId, Map<String, Object> config) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                logger.info("Starting direct project generation for session: {}", sessionId);
                
                // Create a simple blueprint from the configuration
                ProjectBlueprint blueprint = createBlueprintFromConfig(config);
                blueprintCache.put(sessionId, blueprint);
                
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
                
                logger.info("Direct project generation completed for session: {}", sessionId);
                
                // Return download URLs
                Map<String, String> downloadUrls = new HashMap<>();
                downloadUrls.put("backendUrl", "/api/projects/download/backend/" + sessionId);
                downloadUrls.put("frontendUrl", "/api/projects/download/frontend/" + sessionId);
                downloadUrls.put("status", "COMPLETED");
                downloadUrls.put("sessionId", sessionId);
                
                return downloadUrls;
                
            } catch (Exception e) {
                logger.error("Direct project generation failed for session: {}", sessionId, e);
                
                GenerationSession session = sessionCache.get(sessionId);
                if (session != null) {
                    session.setStatus(GenerationStatus.FAILED);
                    session.setError(e.getMessage());
                    session.setEndTime(System.currentTimeMillis());
                }
                
                throw new RuntimeException("Direct project generation failed", e);
            }
        });
    }
    
    /**
     * Create a basic project blueprint from configuration
     */
    private ProjectBlueprint createBlueprintFromConfig(Map<String, Object> config) {
        ProjectBlueprint blueprint = new ProjectBlueprint();
        
        // Basic project information
        String projectName = (String) config.getOrDefault("projectName", "Generated Project");
        String projectType = (String) config.getOrDefault("projectType", "web-application");
        String description = (String) config.getOrDefault("description", "AI Generated Project");
        
        // Set project info
        ProjectInfo projectInfo = new ProjectInfo();
        projectInfo.setName(projectName);
        projectInfo.setDescription(description);
        projectInfo.setVersion("1.0.0");
        projectInfo.setPackageName("com.generated." + projectName.toLowerCase().replaceAll(" ", ""));
        blueprint.setProjectInfo(projectInfo);
        
        // Set basic technology stack based on project type
        blueprint.setTechnologyStack(createDefaultTechnologyStack(projectType));
        
        // Add default features based on project type
        blueprint.setFeatures(createDefaultFeatures(projectType));
        
        return blueprint;
    }
    
    /**
     * Create default technology stack based on project type
     */
    private TechnologyStack createDefaultTechnologyStack(String projectType) {
        TechnologyStack stack = new TechnologyStack();
        
        // Create backend configuration
        TechnologyStack.Backend backend = new TechnologyStack.Backend();
        backend.setFramework("Spring Boot");
        backend.setVersion("3.2.0");
        backend.setLanguage("Java");
        backend.setRuntime("JDK 17");
        
        // Create frontend configuration
        TechnologyStack.Frontend frontend = new TechnologyStack.Frontend();
        
        // Create database configuration
        TechnologyStack.Database database = new TechnologyStack.Database();
        
        switch (projectType.toLowerCase()) {
            case "web-application":
                frontend.setFramework("React");
                frontend.setVersion("18.0");
                frontend.setUiLibraries(java.util.Arrays.asList("Material-UI", "Axios"));
                database.setType("PostgreSQL");
                database.setVersion("15.0");
                stack.setBuildTool("Maven");
                break;
            case "microservice":
                frontend.setFramework("React");
                frontend.setVersion("18.0");
                database.setType("MongoDB");
                database.setVersion("7.0");
                stack.setBuildTool("Maven");
                break;
            case "mobile-app":
                frontend.setFramework("React Native");
                frontend.setVersion("0.72");
                database.setType("Firebase");
                database.setVersion("10.0");
                stack.setBuildTool("Gradle");
                break;
            default:
                frontend.setFramework("Angular");
                frontend.setVersion("17.0");
                frontend.setUiLibraries(java.util.Arrays.asList("Angular Material"));
                database.setType("H2");
                database.setVersion("2.2");
                stack.setBuildTool("Maven");
        }
        
        stack.setBackend(backend);
        stack.setFrontend(frontend);
        stack.setDatabase(database);
        
        return stack;
    }
    
    /**
     * Create default features based on project type
     */
    private List<Feature> createDefaultFeatures(String projectType) {
        List<Feature> features = new ArrayList<>();
        
        // Add common features
        Feature userManagement = new Feature();
        userManagement.setId("user-mgmt");
        userManagement.setName("User Management");
        userManagement.setDescription("User registration, login, and profile management");
        userManagement.setPriority("HIGH");
        userManagement.setUserStories(java.util.Arrays.asList(
            "As a user, I want to register with email and password",
            "As a user, I want to login to access my account",
            "As a user, I want to update my profile information"
        ));
        features.add(userManagement);
        
        Feature dashboard = new Feature();
        dashboard.setId("dashboard");
        dashboard.setName("Dashboard");
        dashboard.setDescription("Main application dashboard with key metrics");
        dashboard.setPriority("MEDIUM");
        dashboard.setUserStories(java.util.Arrays.asList(
            "As a user, I want to see an overview of my data",
            "As a user, I want to view key metrics and statistics"
        ));
        features.add(dashboard);
        
        // Add type-specific features
        if ("web-application".equals(projectType)) {
            Feature crud = new Feature();
            crud.setId("crud-ops");
            crud.setName("CRUD Operations");
            crud.setDescription("Create, Read, Update, Delete operations for main entities");
            crud.setPriority("HIGH");
            crud.setUserStories(java.util.Arrays.asList(
                "As a user, I want to create new records",
                "As a user, I want to view existing records",
                "As a user, I want to update record information",
                "As a user, I want to delete unwanted records"
            ));
            features.add(crud);
        } else if ("microservice".equals(projectType)) {
            Feature apiGateway = new Feature();
            apiGateway.setId("api-gateway");
            apiGateway.setName("API Gateway");
            apiGateway.setDescription("Centralized API gateway for microservice communication");
            apiGateway.setPriority("HIGH");
            apiGateway.setUserStories(java.util.Arrays.asList(
                "As a system, I want to route requests to appropriate services",
                "As a system, I want to handle authentication centrally"
            ));
            features.add(apiGateway);
        }
        
        return features;
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
     * Get combined project ZIP (both backend and frontend)
     */
    public byte[] getCombinedProjectZip(String sessionId) {
        try {
            byte[] backendZip = backendZipCache.get(sessionId);
            byte[] frontendZip = frontendZipCache.get(sessionId);
            
            if (backendZip == null && frontendZip == null) {
                return null;
            }
            
            // Create a combined ZIP file
            Map<String, byte[]> zipFiles = new HashMap<>();
            
            if (backendZip != null) {
                zipFiles.put("backend.zip", backendZip);
            }
            
            if (frontendZip != null) {
                zipFiles.put("frontend.zip", frontendZip);
            }
            
            return createZipFromZipFiles(zipFiles);
            
        } catch (Exception e) {
            logger.error("Failed to create combined ZIP for session: {}", sessionId, e);
            return null;
        }
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
        logger.debug("Processing {} agent results for session: {}", results.size(), sessionId);
        
        Map<String, String> backendFiles = new HashMap<>();
        Map<String, String> frontendFiles = new HashMap<>();
        
        // Process agent results and categorize files
        for (AgentResult result : results) {
            logger.debug("Processing agent result: {} - Success: {} - Output length: {}", 
                result.getAgentName(), result.isSuccess(), 
                result.getOutput() != null ? result.getOutput().toString().length() : 0);
            
            if (result.isSuccess() && result.getOutput() != null) {
                categorizeGeneratedFiles(result, backendFiles, frontendFiles);
            } else {
                logger.warn("Agent {} failed or returned empty output - skipping file generation. Error: {}", result.getAgentName(), result.getMessage());
            }
        }
        
        logger.info("File categorization completed - Backend files: {}, Frontend files: {}", 
            backendFiles.size(), frontendFiles.size());
        
        // Log file names for debugging
        if (logger.isDebugEnabled()) {
            backendFiles.keySet().forEach(file -> logger.debug("Backend file added: {}", file));
            frontendFiles.keySet().forEach(file -> logger.debug("Frontend file added: {}", file));
        }
        
        // Create backend ZIP
        if (!backendFiles.isEmpty()) {
            byte[] backendZip = createZipFromFiles(backendFiles);
            backendZipCache.put(sessionId, backendZip);
            logger.info("Backend ZIP created: {} bytes, {} files", backendZip.length, backendFiles.size());
        } else {
            logger.warn("No backend files were generated for session: {}", sessionId);
        }
        
        // Create frontend ZIP
        if (!frontendFiles.isEmpty()) {
            byte[] frontendZip = createZipFromFiles(frontendFiles);
            frontendZipCache.put(sessionId, frontendZip);
            logger.info("Frontend ZIP created: {} bytes, {} files", frontendZip.length, frontendFiles.size());
        } else {
            logger.warn("No frontend files were generated for session: {}", sessionId);
        }
        
        // Create dependency and setup files
        createDependencyFiles(sessionId, backendFiles, frontendFiles);
        
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
        
        logger.debug("Categorizing files from agent: {} - Output length: {}", agentName, output.length());
        
        if (output.isEmpty()) {
            logger.warn("Agent {} returned empty output", agentName);
            return;
        }
        
        // Log first 200 characters of output for debugging
        if (logger.isDebugEnabled()) {
            String preview = output.length() > 200 ? output.substring(0, 200) + "..." : output;
            logger.debug("Agent {} output preview: {}", agentName, preview);
        }
        
        // Try to parse agent output as JSON first
        try {
            // Check if output is JSON format with "files" structure
            if (output.trim().startsWith("{") && output.contains("\"files\"")) {
                logger.debug("Agent {} output appears to be structured JSON, attempting to parse", agentName);
                parseStructuredAgentOutput(output, agentName, backendFiles, frontendFiles);
                return;
            } else {
                logger.debug("Agent {} output is not structured JSON, using fallback parsing", agentName);
            }
        } catch (Exception e) {
            logger.warn("Failed to parse structured output from agent {}, falling back to text parsing: {}", 
                agentName, e.getMessage());
        }
        
        // Fallback to text-based parsing for agents that don't return structured JSON
        if (agentName.contains("Backend-Code-Generator")) {
            logger.debug("Using backend code parser for agent: {}", agentName);
            parseBackendCodeOutput(output, backendFiles);
        } else if (agentName.contains("Frontend-Code-Generator")) {
            logger.debug("Using frontend code parser for agent: {}", agentName);
            parseFrontendCodeOutput(output, frontendFiles);
        } else if (agentName.contains("Database-Agent")) {
            logger.debug("Using database parser for agent: {}", agentName);
            parseDatabaseOutput(output, backendFiles);
        } else if (agentName.contains("DevOps-Configuration")) {
            logger.debug("Using DevOps parser for agent: {}", agentName);
            parseDevOpsOutput(output, backendFiles, frontendFiles);
        } else if (agentName.contains("QA-Testing-Generator")) {
            logger.debug("Using testing parser for agent: {}", agentName);
            parseTestingOutput(output, backendFiles, frontendFiles);
        } else if (agentName.contains("Integration-Assembly")) {
            logger.debug("Using integration parser for agent: {}", agentName);
            parseIntegrationOutput(output, backendFiles, frontendFiles);
        } else {
            // Fallback: add as documentation
            logger.debug("Using fallback documentation parser for agent: {}", agentName);
            backendFiles.put("docs/" + agentName.replaceAll("[^a-zA-Z0-9]", "-") + ".md", output);
        }
        
        logger.debug("Agent {} processing completed", agentName);
    }
    
    /**
     * Parse structured JSON output from agents
     */
    private void parseStructuredAgentOutput(String jsonOutput, String agentName, 
                                          Map<String, String> backendFiles, 
                                          Map<String, String> frontendFiles) {
        
        logger.debug("Parsing structured JSON output from agent: {} (length: {})", agentName, jsonOutput.length());
        
        try {
            // Log first 200 characters of JSON for debugging
            if (logger.isDebugEnabled()) {
                String preview = jsonOutput.length() > 200 ? jsonOutput.substring(0, 200) + "..." : jsonOutput;
                logger.debug("Agent {} JSON preview: {}", agentName, preview);
            }
            
            // Clean JSON and try to parse
            String cleanJson = cleanJsonOutput(jsonOutput);
            logger.debug("Cleaned JSON for agent: {} (original: {}, cleaned: {})", 
                agentName, jsonOutput.length(), cleanJson.length());
            
            // Extract files section
            if (cleanJson.contains("\"files\"")) {
                logger.debug("Found 'files' section in agent {} output", agentName);
                String filesSection = extractJsonSection(cleanJson, "files");
                if (filesSection != null) {
                    logger.debug("Extracted files section for agent: {} (length: {})", agentName, filesSection.length());
                    
                    // Determine target based on agent type and file paths
                    if (agentName.contains("Backend") || agentName.contains("Database")) {
                        logger.debug("Parsing files as backend for agent: {}", agentName);
                        parseJsonFiles(filesSection, backendFiles);
                    } else if (agentName.contains("Frontend")) {
                        logger.debug("Parsing files as frontend for agent: {}", agentName);
                        parseJsonFiles(filesSection, frontendFiles);
                    } else {
                        // Parse into both for agents like DevOps
                        logger.debug("Parsing files as both backend and frontend for agent: {}", agentName);
                        parseJsonFiles(filesSection, backendFiles);
                        parseJsonFiles(filesSection, frontendFiles);
                    }
                } else {
                    logger.warn("Failed to extract files section from agent {} output", agentName);
                }
            } else {
                logger.warn("No 'files' section found in agent {} output", agentName);
            }
            
            // Handle dependencies if present
            if (cleanJson.contains("\"dependencies\"")) {
                logger.debug("Found 'dependencies' section in agent {} output", agentName);
                String dependencies = extractJsonSection(cleanJson, "dependencies");
                if (dependencies != null) {
                    logger.debug("Extracted dependencies for agent: {} (length: {})", agentName, dependencies.length());
                    if (agentName.contains("Backend")) {
                        backendFiles.put("DEPENDENCIES.txt", "Backend Dependencies:\n" + dependencies);
                        logger.debug("Added backend dependencies file for agent: {}", agentName);
                    } else if (agentName.contains("Frontend")) {
                        frontendFiles.put("DEPENDENCIES.txt", "Frontend Dependencies:\n" + dependencies);
                        logger.debug("Added frontend dependencies file for agent: {}", agentName);
                    }
                } else {
                    logger.warn("Failed to extract dependencies section from agent {} output", agentName);
                }
            }
            
            logger.debug("Successfully completed parsing structured output from agent: {}", agentName);
            
        } catch (Exception e) {
            logger.error("Failed to parse structured JSON output from agent {}: {}", agentName, e.getMessage(), e);
            // Fallback to text parsing
            logger.info("Falling back to text parsing for agent {}", agentName);
            if (agentName.contains("Backend")) {
                parseBackendCodeOutput(jsonOutput, backendFiles);
            } else if (agentName.contains("Frontend")) {
                parseFrontendCodeOutput(jsonOutput, frontendFiles);
            }
        }
    }
    
    /**
     * Clean JSON output from AI agents
     */
    private String cleanJsonOutput(String jsonOutput) {
        // Remove markdown code blocks
        jsonOutput = jsonOutput.replaceAll("```json\\s*", "").replaceAll("```\\s*", "");
        
        // Remove leading/trailing backticks  
        jsonOutput = jsonOutput.replaceAll("^`+", "").replaceAll("`+$", "");
        
        // Find the first { and last } to extract JSON content
        int firstBrace = jsonOutput.indexOf('{');
        int lastBrace = jsonOutput.lastIndexOf('}');
        
        if (firstBrace != -1 && lastBrace != -1 && firstBrace < lastBrace) {
            jsonOutput = jsonOutput.substring(firstBrace, lastBrace + 1);
        }
        
        return jsonOutput.trim();
    }
    
    /**
     * Extract a JSON section (simple implementation)
     */
    private String extractJsonSection(String json, String sectionName) {
        try {
            String pattern = "\"" + sectionName + "\"\\s*:\\s*\\{";
            int start = json.indexOf("\"" + sectionName + "\"");
            if (start == -1) return null;
            
            int braceStart = json.indexOf("{", start);
            if (braceStart == -1) return null;
            
            int braceCount = 1;
            int pos = braceStart + 1;
            
            while (pos < json.length() && braceCount > 0) {
                char c = json.charAt(pos);
                if (c == '{') braceCount++;
                else if (c == '}') braceCount--;
                pos++;
            }
            
            if (braceCount == 0) {
                return json.substring(braceStart, pos);
            }
        } catch (Exception e) {
            logger.warn("Failed to extract JSON section {}", sectionName, e);
        }
        return null;
    }
    
    /**
     * Parse JSON files section into file map
     */
    private void parseJsonFiles(String filesJson, Map<String, String> targetFiles) {
        logger.debug("Parsing JSON files section (length: {}, current files: {})", 
            filesJson.length(), targetFiles.size());
        
        try {
            // Simple JSON parsing for file paths and content
            String[] lines = filesJson.split("\n");
            String currentPath = null;
            StringBuilder currentContent = new StringBuilder();
            int filesProcessed = 0;
            
            logger.debug("Processing {} lines of JSON files section", lines.length);
            
            for (String line : lines) {
                line = line.trim();
                if (line.contains("\":") && line.startsWith("\"")) {
                    // Save previous file if exists
                    if (currentPath != null && currentContent.length() > 0) {
                        String content = cleanFileContent(currentContent.toString());
                        targetFiles.put(currentPath, content);
                        logger.debug("Added file: {} (content length: {})", currentPath, content.length());
                        filesProcessed++;
                    }
                    
                    // Extract new file path
                    int colonIndex = line.indexOf("\":");
                    if (colonIndex > 0) {
                        currentPath = line.substring(1, colonIndex);
                        logger.debug("Starting new file: {}", currentPath);
                        // Extract content start
                        String contentStart = line.substring(colonIndex + 2).trim();
                        if (contentStart.startsWith("\"")) {
                            contentStart = contentStart.substring(1);
                        }
                        currentContent = new StringBuilder(contentStart);
                    }
                } else if (currentPath != null) {
                    // Append to current content
                    currentContent.append("\n").append(line);
                }
            }
            
            // Save last file
            if (currentPath != null && currentContent.length() > 0) {
                String content = cleanFileContent(currentContent.toString());
                targetFiles.put(currentPath, content);
                logger.debug("Added final file: {} (content length: {})", currentPath, content.length());
                filesProcessed++;
            }
            
            logger.debug("Successfully processed {} files from JSON section", filesProcessed);
            
        } catch (Exception e) {
            logger.error("Failed to parse JSON files section: {}", e.getMessage(), e);
        }
    }
    
    private String cleanFileContent(String content) {
        // Clean up JSON escape characters
        content = content.replaceAll("\\\\n", "\n")
                       .replaceAll("\\\\\"", "\"")
                       .replaceAll("\\\\\\\\", "\\\\");
        // Remove trailing quotes and commas
        content = content.replaceAll("[\"\\,}]*$", "");
        return content;
    }
    
    private void parseBackendCodeOutput(String output, Map<String, String> backendFiles) {
        // If agents return non-JSON output, provide basic structure
        if (!output.trim().startsWith("{")) {
            backendFiles.put("generated-backend-output.txt", output);
            
            // Create basic Spring Boot structure based on project name
            String packageName = "com.generated.app";
            String basePath = "src/main/java/" + packageName.replace(".", "/");
            
            backendFiles.put(basePath + "/Application.java", createBasicSpringBootApp(packageName));
            backendFiles.put("src/main/resources/application.properties", createBasicApplicationProperties());
            backendFiles.put("pom.xml", createBasicPomXml());
        }
    }
    
    private void parseFrontendCodeOutput(String output, Map<String, String> frontendFiles) {
        // If agents return non-JSON output, provide basic structure
        if (!output.trim().startsWith("{")) {
            frontendFiles.put("generated-frontend-output.txt", output);
            
            // Create basic Angular structure
            frontendFiles.put("src/app/app.component.ts", createBasicAngularComponent());
            frontendFiles.put("src/app/app.component.html", createBasicAngularTemplate());
            frontendFiles.put("src/main.ts", createBasicAngularMain());
            frontendFiles.put("package.json", createBasicPackageJson());
        }
    }
    
    private void parseDatabaseOutput(String output, Map<String, String> backendFiles) {
        backendFiles.put("docs/database-design.md", output);
    }
    
    private void parseDevOpsOutput(String output, Map<String, String> backendFiles, Map<String, String> frontendFiles) {
        backendFiles.put("Dockerfile", createBasicDockerfile());
        frontendFiles.put("Dockerfile", createBasicAngularDockerfile());
        backendFiles.put("docker-compose.yml", createBasicDockerCompose());
    }
    
    private void parseTestingOutput(String output, Map<String, String> backendFiles, Map<String, String> frontendFiles) {
        backendFiles.put("docs/testing-strategy.md", output);
        frontendFiles.put("docs/testing-strategy.md", output);
    }
    
    private void parseIntegrationOutput(String output, Map<String, String> backendFiles, Map<String, String> frontendFiles) {
        backendFiles.put("README.md", createBasicReadme());
        frontendFiles.put("README.md", createBasicReadme());
    }
    
    // Helper methods for basic file creation
    private String createBasicSpringBootApp(String packageName) {
        return """
            package %s;
            
            import org.springframework.boot.SpringApplication;
            import org.springframework.boot.autoconfigure.SpringBootApplication;
            
            @SpringBootApplication
            public class Application {
                public static void main(String[] args) {
                    SpringApplication.run(Application.class, args);
                }
            }
            """.formatted(packageName);
    }
    
    private String createBasicApplicationProperties() {
        return """
            server.port=8080
            spring.datasource.url=jdbc:h2:mem:testdb
            spring.datasource.driver-class-name=org.h2.Driver
            spring.jpa.hibernate.ddl-auto=create-drop
            spring.h2.console.enabled=true
            """;
    }
    
    private String createBasicPomXml() {
        return """
            <?xml version="1.0" encoding="UTF-8"?>
            <project xmlns="http://maven.apache.org/POM/4.0.0">
                <modelVersion>4.0.0</modelVersion>
                <parent>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-starter-parent</artifactId>
                    <version>3.2.0</version>
                </parent>
                <groupId>com.generated</groupId>
                <artifactId>app</artifactId>
                <version>1.0.0</version>
                <dependencies>
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-web</artifactId>
                    </dependency>
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-data-jpa</artifactId>
                    </dependency>
                    <dependency>
                        <groupId>com.h2database</groupId>
                        <artifactId>h2</artifactId>
                        <scope>runtime</scope>
                    </dependency>
                </dependencies>
            </project>
            """;
    }
    
    private String createBasicAngularComponent() {
        return """
            import { Component } from '@angular/core';
            
            @Component({
              selector: 'app-root',
              templateUrl: './app.component.html',
              styleUrls: ['./app.component.css']
            })
            export class AppComponent {
              title = 'Generated App';
            }
            """;
    }
    
    private String createBasicAngularTemplate() {
        return """
            <div>
              <h1>{{ title }}</h1>
              <p>Welcome to your generated application!</p>
            </div>
            """;
    }
    
    private String createBasicAngularMain() {
        return """
            import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
            import { AppModule } from './app/app.module';
            
            platformBrowserDynamic().bootstrapModule(AppModule)
              .catch(err => console.error(err));
            """;
    }
    
    private String createBasicPackageJson() {
        return """
            {
              "name": "generated-app",
              "version": "1.0.0",
              "dependencies": {
                "@angular/core": "^17.0.0",
                "@angular/common": "^17.0.0",
                "@angular/platform-browser": "^17.0.0"
              },
              "scripts": {
                "start": "ng serve",
                "build": "ng build"
              }
            }
            """;
    }
    
    private String createBasicDockerfile() {
        return """
            FROM openjdk:17-jdk-slim
            COPY target/*.jar app.jar
            EXPOSE 8080
            ENTRYPOINT ["java", "-jar", "/app.jar"]
            """;
    }
    
    private String createBasicAngularDockerfile() {
        return """
            FROM node:18-alpine AS build
            WORKDIR /app
            COPY package*.json ./
            RUN npm install
            COPY . .
            RUN npm run build
            
            FROM nginx:alpine
            COPY --from=build /app/dist/* /usr/share/nginx/html/
            """;
    }
    
    private String createBasicDockerCompose() {
        return """
            version: '3.8'
            services:
              backend:
                build: .
                ports:
                  - "8080:8080"
              frontend:
                build: ./frontend
                ports:
                  - "80:80"
            """;
    }
    
    private String createBasicReadme() {
        return """
            # Generated Project
            
            This project was generated by the AI Project Generator.
            
            ## Getting Started
            
            ### Backend
            ```bash
            mvn spring-boot:run
            ```
            
            ### Frontend
            ```bash
            npm install
            ng serve
            ```
            """;
    }
    
    /**
     * Create ZIP file from file map
     */
    private byte[] createZipFromFiles(Map<String, String> files) throws IOException {
        logger.debug("Creating ZIP from {} files", files.size());
        
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        int filesAdded = 0;
        long totalSize = 0;
        
        try (ZipOutputStream zos = new ZipOutputStream(baos)) {
            for (Map.Entry<String, String> entry : files.entrySet()) {
                String fileName = entry.getKey();
                String content = entry.getValue();
                
                logger.debug("Adding file to ZIP: {} (content length: {})", fileName, content.length());
                
                ZipEntry zipEntry = new ZipEntry(fileName);
                zos.putNextEntry(zipEntry);
                byte[] contentBytes = content.getBytes();
                zos.write(contentBytes);
                zos.closeEntry();
                
                filesAdded++;
                totalSize += contentBytes.length;
            }
        }
        
        byte[] zipBytes = baos.toByteArray();
        logger.debug("ZIP creation completed: {} files added, {} bytes total content, {} bytes ZIP size", 
            filesAdded, totalSize, zipBytes.length);
        
        return zipBytes;
    }
    
    /**
     * Create ZIP file from existing ZIP files
     */
    private byte[] createZipFromZipFiles(Map<String, byte[]> zipFiles) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        
        try (ZipOutputStream zos = new ZipOutputStream(baos)) {
            for (Map.Entry<String, byte[]> entry : zipFiles.entrySet()) {
                ZipEntry zipEntry = new ZipEntry(entry.getKey());
                zos.putNextEntry(zipEntry);
                zos.write(entry.getValue());
                zos.closeEntry();
            }
        }
        
        return baos.toByteArray();
    }
    
    /**
     * Create dependency and setup instruction files
     */
    private void createDependencyFiles(String sessionId, Map<String, String> backendFiles, Map<String, String> frontendFiles) {
        // Backend setup instructions
        backendFiles.put("BACKEND_SETUP.md", """
            # Backend Setup Instructions
            
            ## Prerequisites
            - Java 17 or higher
            - Maven 3.6+
            - PostgreSQL 15+ (or H2 for development)
            
            ## Installation
            ```bash
            # Build the project
            mvn clean compile
            
            # Run tests
            mvn test
            
            # Start the application
            mvn spring-boot:run
            ```
            
            ## Dependencies
            This project uses the following key dependencies:
            - Spring Boot 3.2.0
            - Spring Data JPA
            - Spring Web
            - PostgreSQL Driver
            - H2 Database (for development)
            - Spring Boot Validation
            
            ## Configuration
            Update application.properties with your database settings.
            
            ## API Documentation
            Once running, access the application at: http://localhost:8080
            """);
            
        // Frontend setup instructions
        frontendFiles.put("FRONTEND_SETUP.md", """
            # Frontend Setup Instructions
            
            ## Prerequisites
            - Node.js 18+ 
            - npm 9+
            - Angular CLI
            
            ## Installation
            ```bash
            # Install Angular CLI globally
            npm install -g @angular/cli
            
            # Install project dependencies
            npm install
            
            # Start development server
            ng serve
            ```
            
            ## Dependencies
            This project uses Angular 17 with Material UI.
            
            ## Access
            Development server: http://localhost:4200
            """);
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
