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
        
        Generate the following DevOps components:
        
        1. DOCKER CONFIGURATION:
           - Create Dockerfile for backend application
           - Create Dockerfile for frontend application
           - Add docker-compose.yml for local development
           - Include multi-stage builds for optimization
           - Add proper health checks and security configurations
        
        2. CI/CD PIPELINES:
           - Create GitHub Actions workflows (.github/workflows/)
           - Include build, test, and deployment stages
           - Add automated security scanning
           - Configure environment-specific deployments
           - Include rollback mechanisms
        
        3. KUBERNETES MANIFESTS:
           - Create deployment, service, and ingress YAML files
           - Add ConfigMaps and Secrets for configuration
           - Include horizontal pod autoscaling
           - Add resource limits and requests
           - Configure health checks and probes
        
        4. INFRASTRUCTURE AS CODE:
           - Create Terraform configurations for cloud resources
           - Include modules for reusability
           - Add proper variable management
           - Configure state management and backends
        
        5. MONITORING & LOGGING:
           - Add Prometheus metrics configuration
           - Create Grafana dashboards
           - Configure log aggregation (ELK stack)
           - Add alerting rules and notifications
        
        6. ENVIRONMENT CONFIGURATION:
           - Create environment-specific configuration files
           - Add configuration for dev, staging, and production
           - Include secret management
           - Configure environment variables
        
        7. BUILD SCRIPTS:
           - Create Maven/Gradle build configurations
           - Add npm/yarn scripts for frontend
           - Include test automation scripts
           - Add code quality and coverage tools
        
        8. DEPLOYMENT SCRIPTS:
           - Create deployment automation scripts
           - Add database migration scripts
           - Include environment setup scripts
           - Add backup and recovery procedures
        
        Requirements:
        - Use industry best practices for CI/CD
        - Include security scanning and compliance
        - Add proper error handling and rollback
        - Use infrastructure as code principles
        - Include monitoring and observability
        - Make configurations cloud-agnostic where possible
        - Add comprehensive documentation
        
        Return the complete DevOps structure as a JSON object with file paths and content.
        Structure: {"files": [{"path": ".github/workflows/...", "content": "..."}]}
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
