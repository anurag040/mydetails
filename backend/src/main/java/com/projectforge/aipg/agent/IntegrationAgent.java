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
        
        Generate the following integration components:
        
        1. PROJECT STRUCTURE:
           - Create complete directory structure for both frontend and backend
           - Add root-level configuration files (package.json, pom.xml, etc.)
           - Include README files with setup and deployment instructions
           - Add license, contributing guidelines, and documentation
        
        2. CONFIGURATION INTEGRATION:
           - Create application.properties/yml with all required configurations
           - Add environment-specific configuration files
           - Include database connection and migration settings
           - Configure security, logging, and monitoring
        
        3. API INTEGRATION:
           - Create API documentation (OpenAPI/Swagger specs)
           - Add CORS configuration for frontend-backend communication
           - Include API versioning and error handling
           - Configure request/response interceptors
        
        4. SECURITY INTEGRATION:
           - Implement authentication and authorization
           - Add JWT token configuration
           - Include role-based access control
           - Configure security headers and CSRF protection
        
        5. FRONTEND-BACKEND INTEGRATION:
           - Create Angular services for API communication
           - Add HTTP interceptors for authentication and error handling
           - Include environment configuration for API endpoints
           - Configure proxy settings for development
        
        6. DATABASE INTEGRATION:
           - Connect JPA entities with database schema
           - Add data initialization scripts
           - Include connection pooling and transaction management
           - Configure database migrations and versioning
        
        7. BUILD INTEGRATION:
           - Create Maven/Gradle multi-module project structure
           - Add build scripts for frontend and backend
           - Include packaging and distribution configurations
           - Configure artifact repositories and dependencies
        
        8. DEPLOYMENT INTEGRATION:
           - Create Docker Compose for full stack deployment
           - Add environment variable configuration
           - Include health check endpoints
           - Configure load balancing and scaling
        
        9. MONITORING INTEGRATION:
           - Add application metrics and health endpoints
           - Include logging configuration and aggregation
           - Configure error tracking and alerting
           - Add performance monitoring dashboards
        
        10. FINAL ASSEMBLY:
            - Create project assembly scripts
            - Add validation and verification scripts
            - Include smoke tests for deployment validation
            - Create ZIP packaging for frontend and backend
        
        Requirements:
        - Ensure all components work together seamlessly
        - Add comprehensive error handling and validation
        - Include proper documentation and setup guides
        - Make the integration production-ready
        - Add monitoring and observability
        - Include security best practices
        - Make the system scalable and maintainable
        
        Return the complete integration structure as a JSON object with file paths and content.
        Structure: {"files": [{"path": "...", "content": "..."}]}
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
