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
 * AI Agent responsible for final project integration, configuration, and assembly
 */
@Component
public class IntegrationAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(IntegrationAgent.class);
    
    private final ChatClient chatClient;
    
    private static final String INTEGRATION_PROMPT = """
        You are a system integration specialist and project architect. Based on the project blueprint 
        and generated code components, create the final integration layer and project assembly.
        
        Project Blueprint: {blueprint}
        
        Generate a JSON object where keys are file paths and values are the content of those files.
        This should include configuration files, build scripts, and integration components.
        
        Requirements:
        - Create complete directory structure for both frontend and backend.
        - Add root-level configuration files (package.json, pom.xml, etc.).
        - Include README files with setup and deployment instructions.
        - Create application.properties/yml with all required configurations.
        - Create API documentation (e.g., OpenAPI/Swagger specs).
        - Ensure all components work together seamlessly.
        
        Return ONLY the JSON object with file paths and their content.
        """;
    
    public IntegrationAgent(ChatClient chatClient) {
        this.chatClient = chatClient;
    }
    
    @Override
    public String getAgentName() {
        return "Integration-Assembly-Agent";
    }
    
    @Override
    public String getDescription() {
        return "Handles final project integration, configuration, and assembly";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        // Integration agent runs last and processes any blueprint
        return true;
    }
    
    @Override
    public int getPriority() {
        return 90; // Lowest priority - runs last
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("Integration Agent starting final assembly...");
                
                String blueprintJson = convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(INTEGRATION_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of("blueprint", blueprintJson));
                
                String integrationConfig = chatClient.prompt(prompt).call().content();
                
                logger.info("Project integration completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "Project integration completed successfully", 
                    integrationConfig, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("Project integration failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "Project integration failed: " + e.getMessage(), 
                    processingTime);
            }
        });
    }
    
    private String convertBlueprintToJson(ProjectBlueprint blueprint) {
        // Convert blueprint to JSON string
        // This would use Jackson ObjectMapper in a real implementation
        return "{}"; // Placeholder
    }
}
