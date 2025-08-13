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
 * AI Agent responsible for generating Spring Boot backend code
 */
@Component
public class BackendCodeAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(BackendCodeAgent.class);
    
    private final ChatClient chatClient;
    
    private static final String BACKEND_GENERATION_PROMPT = """
        You are an expert Spring Boot developer. Based on the project blueprint provided, 
        generate complete, production-ready Spring Boot backend code.
        
        Project Blueprint: {blueprint}
        
        Generate the following Spring Boot components:
        
        1. ENTITIES (JPA):
           - Create @Entity classes for all database entities
           - Include proper annotations (@Id, @GeneratedValue, @Column, etc.)
           - Add relationships (@OneToMany, @ManyToOne, etc.)
           - Include validation annotations
        
        2. REPOSITORIES:
           - Create @Repository interfaces extending JpaRepository
           - Add custom query methods as needed
           - Include proper method naming conventions
        
        3. SERVICES:
           - Create @Service classes with business logic
           - Implement all CRUD operations
           - Add proper error handling and validation
           - Include transaction management
        
        4. CONTROLLERS:
           - Create @RestController classes for all API endpoints
           - Implement proper HTTP methods (GET, POST, PUT, DELETE)
           - Add request/response DTOs
           - Include proper status codes and error handling
           - Add validation and documentation annotations
        
        5. DTOS:
           - Create request and response DTOs
           - Add proper validation annotations
           - Include mapping between entities and DTOs
        
        6. CONFIGURATION:
           - Database configuration
           - Security configuration (if auth is required)
           - CORS configuration
           - Application properties
        
        Requirements:
        - Use Spring Boot 3.x
        - Follow Spring best practices
        - Include proper exception handling
        - Add comprehensive logging
        - Use proper HTTP status codes
        - Include input validation
        - Follow REST API conventions
        - Make code production-ready and compilable
        
        Return the complete code structure as a JSON object with file paths and content.
        Structure: {"files": [{"path": "src/main/java/...", "content": "..."}]}
        """;
    
    public BackendCodeAgent(ChatClient chatClient) {
        this.chatClient = chatClient;
    }
    
    @Override
    public String getAgentName() {
        return "Backend-Code-Generator";
    }
    
    @Override
    public String getDescription() {
        return "Generates complete Spring Boot backend code based on project blueprint";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        return blueprint.getTechnologyStack() != null && 
               blueprint.getTechnologyStack().getBackend() != null &&
               "Spring Boot".equalsIgnoreCase(blueprint.getTechnologyStack().getBackend().getFramework());
    }
    
    @Override
    public int getPriority() {
        return 30; // After PRD analysis and architecture design
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("Backend Code Agent starting code generation...");
                
                String blueprintJson = convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(BACKEND_GENERATION_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of("blueprint", blueprintJson));
                
                String generatedCode = chatClient.prompt(prompt).call().content();
                
                logger.info("Backend code generation completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "Backend code generated successfully", 
                    generatedCode, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("Backend code generation failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "Backend code generation failed: " + e.getMessage(), 
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
