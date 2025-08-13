package com.projectforge.aipg.agent;

import com.projectforge.aipg.model.ProjectBlueprint;
import com.projectforge.aipg.service.PRDProcessingService;
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
 * AI Agent responsible for analyzing PRD documents and creating structured blueprints
 */
@Component
public class PRDAnalystAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(PRDAnalystAgent.class);
    
    private final ChatClient chatClient;
    private final JsonUtils jsonUtils;
    
    private static final String PRD_ANALYSIS_PROMPT = """
        You are an expert software architect and business analyst. Analyze the PRD and create a comprehensive JSON blueprint.
        
        PRD Content: {prdContent}
        Current Blueprint: {blueprint}
        
        CRITICAL REQUIREMENTS:
        1. Return ONLY a valid JSON object matching the ProjectBlueprint structure EXACTLY
        2. Extract REAL, SPECIFIC requirements from the PRD - not generic examples
        3. Create comprehensive project structure based on actual PRD content
        
        Required JSON Structure:
        {{
          "project_info": {{
            "name": "extracted from PRD",
            "description": "based on PRD",
            "version": "1.0.0",
            "package_name": "com.extracted.projectname"
          }},
          "technology_stack": {{
            "backend": {{
              "framework": "Spring Boot",
              "version": "3.2.0",
              "language": "Java",
              "runtime": "JDK 17"
            }},
            "frontend": {{
              "framework": "Angular",
              "version": "17.0.0",
              "ui_libraries": ["Angular Material"]
            }},
            "database": {{
              "type": "PostgreSQL",
              "version": "15.0",
              "additional": ["Connection Pooling"]
            }},
            "build_tool": "Maven"
          }},
          "features": [
            {{
              "id": "extracted-feature-1",
              "name": "Feature Name from PRD",
              "description": "Detailed description from PRD",
              "priority": "HIGH/MEDIUM/LOW",
              "user_stories": ["Story 1 from PRD", "Story 2 from PRD"]
            }}
          ],
          "api_endpoints": [
            {{
              "path": "/api/feature-endpoint",
              "method": "GET/POST/PUT/DELETE",
              "description": "Purpose from PRD"
            }}
          ],
          "database_schema": {{
            "entities": [
              {{
                "name": "EntityName",
                "table_name": "entity_table",
                "fields": [
                  {{
                    "name": "field_name",
                    "type": "VARCHAR(255)",
                    "nullable": false,
                    "primary_key": true
                  }}
                ]
              }}
            ]
          }}
        }}
        
        EXTRACT FROM PRD:
        - Project name and purpose
        - Core business entities and their attributes
        - User workflows and features
        - API requirements
        - Data relationships
        - Business rules
        
        RETURN ONLY THE COMPLETE JSON - NO EXPLANATIONS OR MARKDOWN
        """;
    
    public PRDAnalystAgent(ChatClient chatClient, JsonUtils jsonUtils) {
        this.chatClient = chatClient;
        this.jsonUtils = jsonUtils;
    }
    
    @Override
    public String getAgentName() {
        return "PRD-Analyst";
    }
    
    @Override
    public String getDescription() {
        return "Analyzes PRD documents and creates structured project blueprints";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        // This agent is responsible for initial blueprint creation
        return true;
    }
    
    @Override
    public int getPriority() {
        return 1; // Highest priority - runs first
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("PRD Analyst Agent starting analysis...");
                
                // For now, we'll work with the current blueprint structure
                // The PRD content would be injected via a different mechanism
                String prdContent = "Sample PRD content - to be extracted from actual uploaded file";
                String blueprintJson = jsonUtils.convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(PRD_ANALYSIS_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of(
                    "prdContent", prdContent,
                    "blueprint", blueprintJson
                ));
                
                String analysis = chatClient.prompt(prompt).call().content();
                
                logger.info("PRD analysis completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "PRD analysis completed successfully", 
                    analysis, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("PRD analysis failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "PRD analysis failed: " + e.getMessage(), 
                    processingTime);
            }
        });
    }
    
    /**
     * Process PRD with actual content
     */
    public CompletableFuture<AgentResult> processPRDContent(String prdContent, ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("PRD Analyst Agent starting analysis with actual PRD content...");
                
                String blueprintJson = jsonUtils.convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(PRD_ANALYSIS_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of(
                    "prdContent", prdContent,
                    "blueprint", blueprintJson
                ));
                
                String analysis = chatClient.prompt(prompt).call().content();
                
                logger.info("PRD analysis with actual content completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "PRD analysis completed successfully with actual content", 
                    analysis, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("PRD analysis with actual content failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "PRD analysis failed: " + e.getMessage(), 
                    processingTime);
            }
        });
    }
}
