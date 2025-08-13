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
        Generate a complete Spring Boot application. You MUST return ONLY a JSON object with "files" containing ALL files below.
        
        Project Blueprint: {blueprint}
        
        EXACT JSON FORMAT REQUIRED:
        {
          "files": {
            "pom.xml": "complete pom.xml content",
            "src/main/java/com/generated/app/Application.java": "complete file content",
            "src/main/java/com/generated/app/entity/User.java": "complete file content",
            "src/main/java/com/generated/app/entity/DataRecord.java": "complete file content",
            "src/main/java/com/generated/app/repository/UserRepository.java": "complete file content",
            "src/main/java/com/generated/app/repository/DataRecordRepository.java": "complete file content",
            "src/main/java/com/generated/app/service/UserService.java": "complete file content",
            "src/main/java/com/generated/app/service/DataRecordService.java": "complete file content",
            "src/main/java/com/generated/app/controller/AuthController.java": "complete file content",
            "src/main/java/com/generated/app/controller/UserController.java": "complete file content",
            "src/main/java/com/generated/app/controller/DataController.java": "complete file content",
            "src/main/java/com/generated/app/dto/UserDto.java": "complete file content",
            "src/main/java/com/generated/app/dto/DataRecordDto.java": "complete file content",
            "src/main/java/com/generated/app/dto/LoginRequest.java": "complete file content",
            "src/main/java/com/generated/app/config/CorsConfig.java": "complete file content",
            "src/main/resources/application.properties": "complete file content"
          }
        }
        
        MANDATORY: Each file must be complete with all imports, annotations, and working code.
        Use Spring Boot 3.x, JPA, validation, proper REST controllers with CRUD operations.
        
        User entity: id, username, email, password, createdAt, updatedAt
        DataRecord entity: id, name, description, userId, createdAt, updatedAt
        
        Controllers must have endpoints: GET, POST, PUT, DELETE for both entities.
        Include authentication endpoint: POST /api/auth/login
        
        Return ONLY the JSON object - no explanations, no markdown blocks.
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
