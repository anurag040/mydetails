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
 * AI Agent responsible for generating Angular frontend code
 */
@Component
public class FrontendCodeAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(FrontendCodeAgent.class);
    
    private final ChatClient chatClient;
    
    private static final String FRONTEND_GENERATION_PROMPT = """
        You are an expert Angular developer. Based on the project blueprint provided, 
        generate complete, production-ready Angular frontend code.
        
        Project Blueprint: {blueprint}
        
        Generate the following Angular components:
        
        1. COMPONENTS:
           - Create Angular components for all UI features
           - Include TypeScript, HTML, and CSS files
           - Use Angular best practices (standalone components, signals, etc.)
           - Implement proper component lifecycle
           - Add input/output properties and event handling
        
        2. SERVICES:
           - Create Angular services for API communication
           - Implement HTTP client calls to backend endpoints
           - Add proper error handling and loading states
           - Use dependency injection
        
        3. MODELS/INTERFACES:
           - Create TypeScript interfaces for data models
           - Match backend DTOs and entities
           - Include proper typing for all data structures
        
        4. ROUTING:
           - Set up Angular routing configuration
           - Create route guards if authentication is required
           - Implement lazy loading for feature modules
        
        5. FORMS:
           - Create reactive forms for data input
           - Add form validation (both template and custom validators)
           - Implement proper form submission and error handling
        
        6. UI INTEGRATION:
           - Use specified UI library (Angular Material, PrimeNG, etc.)
           - Create responsive layouts
           - Implement proper styling and theming
           - Add loading indicators and error messages
        
        7. STATE MANAGEMENT:
           - Implement proper state management using signals or services
           - Handle loading, error, and success states
           - Manage user authentication state
        
        Requirements:
        - Use Angular 16+ with standalone components
        - Follow Angular style guide and best practices
        - Use reactive programming with RxJS
        - Implement proper error handling
        - Add comprehensive TypeScript typing
        - Make code production-ready and compilable
        - Include proper component communication
        - Use modern Angular features (signals, control flow, etc.)
        
        Return the complete code structure as a JSON object with file paths and content.
        Structure: {"files": [{"path": "src/app/...", "content": "..."}]}
        """;
    
    public FrontendCodeAgent(ChatClient chatClient) {
        this.chatClient = chatClient;
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
                
                String blueprintJson = convertBlueprintToJson(blueprint);
                
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
    
    private String convertBlueprintToJson(ProjectBlueprint blueprint) {
        // Convert blueprint to JSON string
        // This would use Jackson ObjectMapper in a real implementation
        return "{}"; // Placeholder
    }
}
