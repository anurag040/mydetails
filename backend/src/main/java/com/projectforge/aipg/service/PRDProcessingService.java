package com.projectforge.aipg.service;

import com.projectforge.aipg.agent.PRDAnalystAgent;
import com.projectforge.aipg.agent.AgentResult;
import com.projectforge.aipg.model.ProjectBlueprint;
import com.projectforge.aipg.model.ProjectInfo;
import com.projectforge.aipg.model.TechnologyStack;
import com.projectforge.aipg.model.Feature;
import com.projectforge.aipg.util.JsonUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.CompletableFuture;

/**
 * Service for processing PRD documents and extracting project blueprints
 */
@Service
public class PRDProcessingService {
    
    private static final Logger logger = LoggerFactory.getLogger(PRDProcessingService.class);
    
    private final ChatClient chatClient;
    private final PRDAnalystAgent prdAnalystAgent;
    private final JsonUtils jsonUtils;
    
    // Temporary storage for PRD content - in production, use Redis or database
    private final Map<String, String> prdContentCache = new java.util.concurrent.ConcurrentHashMap<>();
    
    public PRDProcessingService(ChatClient chatClient, PRDAnalystAgent prdAnalystAgent, JsonUtils jsonUtils) {
        this.chatClient = chatClient;
        this.prdAnalystAgent = prdAnalystAgent;
        this.jsonUtils = jsonUtils;
    }
    
    /**
     * Process PRD document asynchronously
     */
    public CompletableFuture<ProjectBlueprint> processPRDAsync(
            MultipartFile file, String projectName, String sessionId) {
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                logger.info("Processing PRD for session: {}", sessionId);
                
                // Extract text content from file
                String prdContent = extractTextContent(file);
                
                // Store PRD content for use by PRD Analyst Agent
                prdContentCache.put(sessionId, prdContent);
                
                // Create initial blueprint with basic info
                ProjectBlueprint initialBlueprint = createInitialBlueprint(projectName, prdContent);
                
                // Use PRD Analyst Agent to analyze and enhance the blueprint
                AgentResult analysisResult = prdAnalystAgent.processPRDContent(prdContent, initialBlueprint).join();
                
                ProjectBlueprint finalBlueprint;
                if (analysisResult.isSuccess() && analysisResult.getOutput() != null) {
                    // Try to parse the agent output as JSON blueprint
                    try {
                        String jsonOutput = analysisResult.getOutput().toString();
                        logger.info("PRD Analysis output received, attempting to parse as blueprint");
                        finalBlueprint = jsonUtils.convertJsonToBlueprint(jsonOutput);
                        if (finalBlueprint == null || finalBlueprint.getProjectInfo() == null) {
                            logger.warn("Parsed blueprint is incomplete, using initial blueprint with enhancements");
                            finalBlueprint = enhanceInitialBlueprint(initialBlueprint, prdContent);
                        } else {
                            logger.info("Successfully parsed enhanced blueprint from PRD analysis");
                        }
                    } catch (Exception e) {
                        logger.warn("Failed to parse agent analysis result, using enhanced initial blueprint", e);
                        finalBlueprint = enhanceInitialBlueprint(initialBlueprint, prdContent);
                    }
                } else {
                    logger.warn("PRD analysis agent failed, using enhanced initial blueprint");
                    finalBlueprint = enhanceInitialBlueprint(initialBlueprint, prdContent);
                }
                
                logger.info("PRD processing completed for session: {}", sessionId);
                return finalBlueprint;
                
            } catch (Exception e) {
                logger.error("PRD processing failed for session: {}", sessionId, e);
                throw new RuntimeException("PRD processing failed", e);
            }
        });
    }
    
    /**
     * Get stored PRD content for a session
     */
    public String getPRDContent(String sessionId) {
        return prdContentCache.get(sessionId);
    }
    
    /**
     * Create initial blueprint from project name and PRD content
     */
    private ProjectBlueprint createInitialBlueprint(String projectName, String prdContent) {
        ProjectBlueprint blueprint = new ProjectBlueprint();
        
        // Set basic project info
        ProjectInfo projectInfo = new ProjectInfo();
        projectInfo.setName(projectName != null ? projectName : "Generated Project");
        projectInfo.setDescription("Project generated from PRD");
        projectInfo.setVersion("1.0.0");
        
        // Generate package name from project name
        String packageName = "com.generated." + 
            (projectName != null ? projectName.toLowerCase().replaceAll("[^a-zA-Z0-9]", "") : "project");
        projectInfo.setPackageName(packageName);
        
        blueprint.setProjectInfo(projectInfo);
        
        // Set default technology stack
        TechnologyStack techStack = new TechnologyStack();
        
        TechnologyStack.Backend backend = new TechnologyStack.Backend();
        backend.setFramework("Spring Boot");
        backend.setVersion("3.2.0");
        backend.setLanguage("Java");
        backend.setRuntime("JDK 17");
        techStack.setBackend(backend);
        
        TechnologyStack.Frontend frontend = new TechnologyStack.Frontend();
        frontend.setFramework("Angular");
        frontend.setVersion("17.0");
        frontend.setUiLibraries(java.util.Arrays.asList("Angular Material"));
        techStack.setFrontend(frontend);
        
        TechnologyStack.Database database = new TechnologyStack.Database();
        database.setType("PostgreSQL");
        database.setVersion("15.0");
        techStack.setDatabase(database);
        
        techStack.setBuildTool("Maven");
        blueprint.setTechnologyStack(techStack);
        
        return blueprint;
    }
    
    /**
     * Enhance initial blueprint with basic PRD analysis when AI parsing fails
     */
    private ProjectBlueprint enhanceInitialBlueprint(ProjectBlueprint initialBlueprint, String prdContent) {
        // Simple text analysis to extract project name and features
        try {
            // Extract project name from PRD content
            String projectName = extractProjectNameFromPRD(prdContent);
            if (projectName != null && !projectName.trim().isEmpty()) {
                if (initialBlueprint.getProjectInfo() != null) {
                    initialBlueprint.getProjectInfo().setName(projectName);
                    initialBlueprint.getProjectInfo().setPackageName(
                        "com.generated." + projectName.toLowerCase().replaceAll("[^a-zA-Z0-9]", "")
                    );
                }
            }
            
            // Extract basic features from PRD
            List<Feature> extractedFeatures = extractFeaturesFromPRD(prdContent);
            if (extractedFeatures != null && !extractedFeatures.isEmpty()) {
                initialBlueprint.setFeatures(extractedFeatures);
            }
            
        } catch (Exception e) {
            logger.warn("Failed to enhance initial blueprint, using as-is", e);
        }
        
        return initialBlueprint;
    }
    
    /**
     * Extract project name from PRD content using simple text analysis
     */
    private String extractProjectNameFromPRD(String prdContent) {
        if (prdContent == null || prdContent.trim().isEmpty()) {
            return null;
        }
        
        // Look for common patterns
        String[] patterns = {
            "Project Name:\\s*(.+)",
            "Application:\\s*(.+)",
            "System:\\s*(.+)",
            "Product:\\s*(.+)"
        };
        
        for (String pattern : patterns) {
            java.util.regex.Pattern p = java.util.regex.Pattern.compile(pattern, java.util.regex.Pattern.CASE_INSENSITIVE);
            java.util.regex.Matcher m = p.matcher(prdContent);
            if (m.find()) {
                return m.group(1).trim();
            }
        }
        
        // Fallback: use first line if it looks like a title
        String[] lines = prdContent.split("\n");
        if (lines.length > 0) {
            String firstLine = lines[0].trim();
            if (firstLine.length() > 0 && firstLine.length() < 100 && !firstLine.toLowerCase().startsWith("prd")) {
                return firstLine;
            }
        }
        
        return "Generated Project";
    }
    
    /**
     * Extract features from PRD content using simple text analysis
     */
    private List<Feature> extractFeaturesFromPRD(String prdContent) {
        List<Feature> features = new ArrayList<>();
        
        try {
            // Look for feature sections
            String[] featureKeywords = {"feature", "functionality", "requirement", "capability", "module"};
            
            String[] lines = prdContent.split("\n");
            for (int i = 0; i < lines.length; i++) {
                String line = lines[i].trim().toLowerCase();
                
                for (String keyword : featureKeywords) {
                    if (line.contains(keyword) && line.length() < 150) {
                        Feature feature = new Feature();
                        feature.setId("feature-" + (features.size() + 1));
                        feature.setName(lines[i].trim());
                        feature.setDescription("Feature extracted from PRD");
                        feature.setPriority("MEDIUM");
                        feature.setUserStories(List.of("As a user, I want to use this feature"));
                        features.add(feature);
                        break;
                    }
                }
            }
            
            // If no features found, add default ones
            if (features.isEmpty()) {
                Feature defaultFeature = new Feature();
                defaultFeature.setId("core-functionality");
                defaultFeature.setName("Core Functionality");
                defaultFeature.setDescription("Core application functionality based on PRD");
                defaultFeature.setPriority("HIGH");
                defaultFeature.setUserStories(List.of("As a user, I want to access core functionality"));
                features.add(defaultFeature);
            }
            
        } catch (Exception e) {
            logger.warn("Failed to extract features from PRD", e);
        }
        
        return features;
    }
    
    /**
     * Extract text content from uploaded file
     */
    private String extractTextContent(MultipartFile file) throws IOException {
        String filename = file.getOriginalFilename();
        
        if (filename == null) {
            throw new IllegalArgumentException("File name is null");
        }
        
        String extension = filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
        
        switch (extension) {
            case "txt":
                return new String(file.getBytes(), StandardCharsets.UTF_8);
            
            case "pdf":
                return extractFromPDF(file);
            
            case "doc":
            case "docx":
                return extractFromWord(file);
            
            default:
                throw new IllegalArgumentException("Unsupported file type: " + extension);
        }
    }
    
    /**
     * Extract text from PDF file
     */
    private String extractFromPDF(MultipartFile file) throws IOException {
        // Implementation would use Apache PDFBox or similar library
        // For now, return placeholder
        logger.info("Extracting text from PDF: {}", file.getOriginalFilename());
        return "PDF content extraction placeholder";
    }
    
    /**
     * Extract text from Word document
     */
    private String extractFromWord(MultipartFile file) throws IOException {
        // Implementation would use Apache POI
        // For now, return placeholder
        logger.info("Extracting text from Word document: {}", file.getOriginalFilename());
        return "Word document content extraction placeholder";
    }
}
