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
 * AI Agent responsible for generating database schema and migrations
 */
@Component
public class DatabaseAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(DatabaseAgent.class);
    
    private final ChatClient chatClient;
    
    private static final String DATABASE_GENERATION_PROMPT = """
        You are a database architect and SQL expert. Based on the project blueprint provided, 
        generate complete database schema, migrations, and related database code.
        
        Project Blueprint: {blueprint}
        
        Generate the following database components as a JSON object with file paths as keys and content as values:
        
        1. DATABASE SCHEMA:
           - Create SQL DDL statements for all tables
           - Define proper primary keys, foreign keys, and indexes
           - Add constraints (NOT NULL, UNIQUE, CHECK, etc.)
           - Design normalized schema following database best practices
           - Include audit fields (created_at, updated_at, etc.)
        
        2. MIGRATION SCRIPTS:
           - Create Flyway or Liquibase migration files
           - Include proper versioning (V1__Initial_schema.sql, etc.)
           - Add rollback scripts where applicable
           - Include data seeding for reference tables
        
        3. JPA ENTITIES:
           - Create JPA entity classes matching database schema
           - Include proper annotations (@Entity, @Table, @Column, etc.)
           - Define relationships (@OneToMany, @ManyToOne, etc.)
           - Add validation annotations
           - Include proper constructors and methods
        
        4. REPOSITORY INTERFACES:
           - Create Spring Data JPA repository interfaces
           - Add custom query methods with @Query annotations
           - Include derived query methods
           - Add pagination and sorting support
        
        Requirements:
        - Generate production-ready SQL code
        - Follow database naming conventions
        - Use appropriate data types for each database system
        - Include proper error handling
        - Add comprehensive documentation
        - Make schema scalable and maintainable
        - Include security considerations (permissions, etc.)
        
        Return the complete database structure with schema files and migration scripts.
        Format the response as organized sections with clear file names and working SQL/migration content.
        Include all necessary database setup, tables, indexes, and data migration files.
        """;
    
    public DatabaseAgent(ChatClient chatClient) {
        this.chatClient = chatClient;
    }
    
    @Override
    public String getAgentName() {
        return "Database-Schema-Generator";
    }
    
    @Override
    public String getDescription() {
        return "Generates database schema, migrations, and JPA entities";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        return blueprint.getDatabaseSchema() != null && 
               !blueprint.getDatabaseSchema().getEntities().isEmpty();
    }
    
    @Override
    public int getPriority() {
        return 20; // High priority - needed before backend code
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("Database Agent starting schema generation...");
                
                String blueprintJson = convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(DATABASE_GENERATION_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of("blueprint", blueprintJson));
                
                String generatedSchema = chatClient.prompt(prompt).call().content();
                
                logger.info("Database schema generation completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "Database schema generated successfully", 
                    generatedSchema, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("Database schema generation failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "Database schema generation failed: " + e.getMessage(), 
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
