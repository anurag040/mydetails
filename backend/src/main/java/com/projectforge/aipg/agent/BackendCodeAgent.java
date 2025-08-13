package com.projectforge.aipg.agent;

import com.projectforge.aipg.model.ProjectBlueprint;
import com.projectforge.aipg.util.JsonUtils;
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
    private final JsonUtils jsonUtils;
    
    private static final String BACKEND_GENERATION_PROMPT = """
        You are an expert Spring Boot developer. Generate a complete, production-ready Spring Boot application based on the detailed blueprint.
        
        Project Blueprint: {blueprint}
        
        CRITICAL REQUIREMENTS:
        1. Return ONLY a JSON object with this exact structure:
        {{
          "files": {{
            "filepath1": "complete file content",
            "filepath2": "complete file content"
          }}
        }}
        
        2. Generate ALL these files with complete, working code:
           - pom.xml (with all required dependencies)
           - src/main/java/APPLICATION_PACKAGE/Application.java (main class)
           - src/main/java/APPLICATION_PACKAGE/controller/*.java (REST controllers for ALL API endpoints)
           - src/main/java/APPLICATION_PACKAGE/service/*.java (service classes for ALL features)
           - src/main/java/APPLICATION_PACKAGE/repository/*.java (JPA repositories for ALL entities)
           - src/main/java/APPLICATION_PACKAGE/entity/*.java (JPA entities for ALL database entities)
           - src/main/java/APPLICATION_PACKAGE/dto/*.java (DTOs for ALL API requests/responses)
           - src/main/java/APPLICATION_PACKAGE/config/*.java (security, CORS, database config)
           - src/main/resources/application.properties (database, server config)
           - src/main/resources/data.sql (sample data)
        
        3. Extract requirements from blueprint:
           - Use blueprint.projectInfo.packageName as base package
           - Create entities from blueprint.databaseSchema.entities
           - Generate controllers for blueprint.apiEndpoints
           - Implement services for blueprint.features
           - Use blueprint.technologyStack.database for config
        
        4. MAKE ALL CODE PRODUCTION-READY:
           - Proper error handling and validation
           - Comprehensive CRUD operations
           - Security configurations
           - Database relationships
           - Proper HTTP status codes
           - Complete request/response DTOs
        
        5. Generate working code that compiles and runs immediately
        
        RETURN ONLY THE JSON OBJECT WITH COMPLETE FILES - NO EXPLANATIONS OR MARKDOWN
        """;
    
    public BackendCodeAgent(ChatClient chatClient, JsonUtils jsonUtils) {
        this.chatClient = chatClient;
        this.jsonUtils = jsonUtils;
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
                
                String blueprintJson = jsonUtils.convertBlueprintToJson(blueprint);
                
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
        return jsonUtils.convertBlueprintToJson(blueprint);
    }
}
