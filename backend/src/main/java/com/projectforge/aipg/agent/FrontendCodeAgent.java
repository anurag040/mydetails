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
        Generate a complete Angular 17 application. You MUST return ONLY a JSON object with "files" containing ALL files below.
        
        Project Blueprint: {blueprint}
        
        EXACT JSON FORMAT REQUIRED:
        {
          "files": {
            "package.json": "complete package.json with all dependencies",
            "angular.json": "complete Angular workspace configuration",
            "tsconfig.json": "complete TypeScript configuration",
            "src/index.html": "complete HTML file",
            "src/main.ts": "complete bootstrap file",
            "src/styles.css": "complete global styles",
            "src/app/app.component.ts": "complete root component",
            "src/app/app.component.html": "complete root template",
            "src/app/app.component.css": "complete root styles",
            "src/app/app.config.ts": "complete app configuration",
            "src/app/app.routes.ts": "complete routing configuration",
            "src/app/models/user.model.ts": "complete User interface",
            "src/app/models/data-record.model.ts": "complete DataRecord interface",
            "src/app/services/auth.service.ts": "complete authentication service",
            "src/app/services/user.service.ts": "complete user service",
            "src/app/services/data.service.ts": "complete data service",
            "src/app/components/login/login.component.ts": "complete login component",
            "src/app/components/login/login.component.html": "complete login template",
            "src/app/components/login/login.component.css": "complete login styles",
            "src/app/components/dashboard/dashboard.component.ts": "complete dashboard component",
            "src/app/components/dashboard/dashboard.component.html": "complete dashboard template",
            "src/app/components/dashboard/dashboard.component.css": "complete dashboard styles",
            "src/app/components/user-list/user-list.component.ts": "complete user list component",
            "src/app/components/user-list/user-list.component.html": "complete user list template",
            "src/app/components/user-list/user-list.component.css": "complete user list styles",
            "src/app/components/data-list/data-list.component.ts": "complete data list component",
            "src/app/components/data-list/data-list.component.html": "complete data list template",
            "src/app/components/data-list/data-list.component.css": "complete data list styles"
          }
        }
        
        MANDATORY REQUIREMENTS:
        - Use Angular 17 standalone components
        - Include Angular Material for UI
        - Implement reactive forms with validation
        - Add HTTP interceptors for authentication
        - Create complete CRUD operations for User and DataRecord
        - Add routing with guards
        - Include proper error handling and loading states
        - Make all code production-ready and compilable
        
        SPECIFIC FEATURES:
        - Login page with email/password
        - Dashboard with overview
        - User management (list, create, edit, delete)
        - Data record management (list, create, edit, delete)
        - Responsive design with Material UI
        
        Return ONLY the JSON object - no explanations, no markdown blocks.
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
