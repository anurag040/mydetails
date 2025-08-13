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
 * AI Agent responsible for generating DevOps configuration and CI/CD pipelines
 */
@Component
public class DevOpsAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(DevOpsAgent.class);
    
    private final ChatClient chatClient;
    
    private static final String DEVOPS_GENERATION_PROMPT = """
        You are a DevOps engineer and infrastructure expert. Based on the project blueprint provided, 
        generate complete CI/CD pipelines, containerization, and deployment configurations.
        
        Project Blueprint: {blueprint}
        
        Generate a JSON object where keys are file paths (e.g., "Dockerfile", ".github/workflows/main.yml") 
        and values are the complete content of those files.
        
        Requirements:
        - Create Dockerfiles for backend and frontend applications.
        - Create a docker-compose.yml for local development.
        - Create GitHub Actions workflows for CI/CD.
        - Use industry best practices for CI/CD, including security scanning.
        - Make configurations cloud-agnostic where possible.
        - Add comprehensive documentation within the files where appropriate.
        
        Return ONLY the JSON object with file paths and their content.
        """;
    
    public DevOpsAgent(ChatClient chatClient) {
        this.chatClient = chatClient;
    }
    
    @Override
    public String getAgentName() {
        return "DevOps-Pipeline-Generator";
    }
    
    @Override
    public String getDescription() {
        return "Generates CI/CD pipelines, Docker configuration, and deployment scripts";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        return blueprint.getDeployment() != null ||
               (blueprint.getTechnologyStack() != null && 
                blueprint.getTechnologyStack().getBackend() != null);
    }
    
    @Override
    public int getPriority() {
        return 60; // After application code is generated
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("DevOps Agent starting pipeline generation...");
                
                String blueprintJson = convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(DEVOPS_GENERATION_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of("blueprint", blueprintJson));
                
                String generatedConfig = chatClient.prompt(prompt).call().content();
                
                logger.info("DevOps configuration generation completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "DevOps configuration generated successfully", 
                    generatedConfig, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("DevOps configuration generation failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "DevOps configuration generation failed: " + e.getMessage(), 
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
