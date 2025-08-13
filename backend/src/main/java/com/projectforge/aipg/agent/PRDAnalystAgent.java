package com.projectforge.aipg.agent;

import com.projectforge.aipg.model.ProjectBlueprint;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.stereotype.Component;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * AI Agent responsible for analyzing PRD documents and creating structured blueprints
 */
@Component
public class PRDAnalystAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(PRDAnalystAgent.class);
    
    private final ChatClient chatClient;
    
    private static final String PRD_ANALYSIS_PROMPT = """
        You are an expert software architect and business analyst. Analyze the following PRD (Product Requirements Document) 
        and create a comprehensive JSON blueprint for a software project.
        
        PRD Content: {prdContent}
        Technology Stack: {technologyStack}
        
        Please analyze this PRD and create a detailed JSON blueprint with the following structure:
        
        1. PROJECT_INFO: Extract project name, description, version, and package naming
        2. FEATURES: Identify all features, user stories, and acceptance criteria
        3. DATABASE_SCHEMA: Design entities, relationships, and field specifications
        4. API_ENDPOINTS: Define REST endpoints based on functionality requirements
        5. FRONTEND_COMPONENTS: Identify UI components and their relationships
        6. BUSINESS_LOGIC: Extract business rules and validation requirements
        7. AUTHENTICATION: Determine auth requirements and user roles
        8. DEPLOYMENT: Suggest deployment configuration
        9. TESTING: Define testing strategy and test cases
        
        Return ONLY valid JSON matching the ProjectBlueprint structure. Be comprehensive and detailed.
        Ensure all field names match exactly with the Java model classes.
        
        Focus on creating actionable, specific requirements that other AI agents can use to generate actual code.
        """;
    
    public PRDAnalystAgent(ChatClient chatClient) {
        this.chatClient = chatClient;
    }
    
    @Override
    public String getAgentName() {
        return "PRD-Analyst";
    }
    
    @Override
    public String getDescription() {
        return "Analyzes PRD documents and creates structured project blueprints";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        // This agent is responsible for initial blueprint creation
        return true;
    }
    
    @Override
    public int getPriority() {
        return 1; // Highest priority - runs first
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("PRD Analyst Agent starting analysis...");
                
                // For now, this would take PRD content from somewhere
                // In a real implementation, you'd extract this from the uploaded file
                String prdContent = "Sample PRD content"; // This would come from file processing
                String technologyStack = formatTechnologyStack(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(PRD_ANALYSIS_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of(
                    "prdContent", prdContent,
                    "technologyStack", technologyStack
                ));
                
                String analysis = chatClient.prompt(prompt).call().content();
                
                logger.info("PRD analysis completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "PRD analysis completed successfully", 
                    analysis, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("PRD analysis failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "PRD analysis failed: " + e.getMessage(), 
                    processingTime);
            }
        });
    }
    
    private String formatTechnologyStack(ProjectBlueprint blueprint) {
        if (blueprint.getTechnologyStack() == null) {
            return "Not specified";
        }
        
        StringBuilder sb = new StringBuilder();
        var techStack = blueprint.getTechnologyStack();
        
        if (techStack.getFrontend() != null) {
            sb.append("Frontend: ").append(techStack.getFrontend().getFramework())
              .append(" ").append(techStack.getFrontend().getVersion()).append("\n");
        }
        
        if (techStack.getBackend() != null) {
            sb.append("Backend: ").append(techStack.getBackend().getFramework())
              .append(" ").append(techStack.getBackend().getVersion()).append("\n");
        }
        
        if (techStack.getDatabase() != null) {
            sb.append("Database: ").append(techStack.getDatabase().getType()).append("\n");
        }
        
        return sb.toString();
    }
}
