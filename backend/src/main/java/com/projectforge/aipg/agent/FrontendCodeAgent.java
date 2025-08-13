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
 * AI Agent responsible for generating Angular frontend code
 */
@Component
public class FrontendCodeAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(FrontendCodeAgent.class);
    
    private final ChatClient chatClient;
    private final JsonUtils jsonUtils;
    
    private static final String FRONTEND_GENERATION_PROMPT = """
        You are an expert Angular developer. Generate a complete, production-ready Angular application based on the detailed blueprint.
        
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
           - package.json (with all required dependencies)
           - angular.json (Angular workspace configuration)
           - tsconfig.json (TypeScript configuration)
           - src/main.ts (Bootstrap file)
           - src/index.html (Main HTML)
           - src/styles.css (Global styles)
           - src/app/app.component.* (Root component with template, styles, spec)
           - src/app/app.config.ts (App configuration)
           - src/app/app.routes.ts (Routing configuration)
           - src/app/components/*/*.* (Components for ALL features from blueprint)
           - src/app/services/*.service.ts (Services for ALL API endpoints)
           - src/app/models/*.ts (TypeScript interfaces for ALL entities)
           - src/app/guards/*.guard.ts (Route guards if authentication required)
        
        3. Extract requirements from blueprint:
           - Create components for blueprint.features
           - Generate services for blueprint.apiEndpoints
           - Create models from blueprint.databaseSchema.entities
           - Use blueprint.technologyStack.frontend.uiLibraries for UI
           - Implement routing between all components
        
        4. MAKE ALL CODE PRODUCTION-READY:
           - Reactive forms with validation
           - HTTP error handling
           - Loading states and spinners
           - Responsive design with Angular Material
           - Proper TypeScript types
           - Authentication handling
           - CRUD operations for all entities
        
        5. Generate working code that compiles and runs immediately
        
        RETURN ONLY THE JSON OBJECT WITH COMPLETE FILES - NO EXPLANATIONS OR MARKDOWN
        """;
    
    public FrontendCodeAgent(ChatClient chatClient, JsonUtils jsonUtils) {
        this.chatClient = chatClient;
        this.jsonUtils = jsonUtils;
    }
    
    @Override
    public String getAgentName() {
        return "Frontend-Code-Generator";
    }
    
    @Override
    public String getDescription() {
        return "Generates complete Angular frontend code based on project blueprint";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        return blueprint.getTechnologyStack() != null && 
               blueprint.getTechnologyStack().getFrontend() != null &&
               "Angular".equalsIgnoreCase(blueprint.getTechnologyStack().getFrontend().getFramework());
    }
    
    @Override
    public int getPriority() {
        return 40; // After backend code generation
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("Frontend Code Agent starting code generation...");
                
                String blueprintJson = jsonUtils.convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(FRONTEND_GENERATION_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of("blueprint", blueprintJson));
                
                String generatedCode = chatClient.prompt(prompt).call().content();
                
                logger.info("Frontend code generation completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "Frontend code generated successfully", 
                    generatedCode, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("Frontend code generation failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "Frontend code generation failed: " + e.getMessage(), 
                    processingTime);
            }
        });
    }
}
