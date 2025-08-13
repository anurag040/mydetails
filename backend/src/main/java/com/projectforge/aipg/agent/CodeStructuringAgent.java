package com.projectforge.aipg.agent;

import com.projectforge.aipg.model.ProjectBlueprint;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.stereotype.Component;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * AI Agent responsible for structuring generated code into proper file system layout
 */
@Component
public class CodeStructuringAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(CodeStructuringAgent.class);
    
    private final ChatClient chatClient;
    
    private static final String CODE_STRUCTURING_PROMPT = """
        You are an expert in project structure and file organization. Given the following agent outputs,
        create a proper JSON structure that maps file paths to their content for both backend and frontend.
        
        Backend Code Output: {backendCode}
        Frontend Code Output: {frontendCode}
        Database Output: {databaseCode}
        DevOps Output: {devopsCode}
        Project Blueprint: {blueprint}
        
        Create a JSON structure with three keys: "backend_files", "frontend_files", and "dependency_files".
        "backend_files" and "frontend_files" should be objects mapping file paths to their content.
        "dependency_files" should be an object containing dependency lists and setup instructions.
        
        Requirements:
        1. Extract all actual code from agent outputs
        2. Organize into proper file/folder structure
        3. Ensure file paths follow conventions (src/main/java for Spring Boot, src/app for Angular)
        4. Include all configuration files (application.properties, package.json, pom.xml, etc.)
        5. Create separate dependency files listing all required packages
        6. Include setup instructions for running the application
        7. Make sure all generated code is complete and compilable
        8. Handle both Maven and npm dependencies properly
        
        Return ONLY the JSON structure with no additional text.
        """;
    
    public CodeStructuringAgent(ChatClient chatClient) {
        this.chatClient = chatClient;
    }
    
    @Override
    public String getAgentName() {
        return "Code-Structuring-Agent";
    }
    
    @Override
    public String getDescription() {
        return "Structures and organizes generated code into proper file system layout";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        return true; // Always can process to structure code
    }
    
    @Override
    public int getPriority() {
        return 80; // Run after all code generation agents
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("Code Structuring Agent starting organization...");
                
                // This will be populated by the orchestrator with other agent outputs
                String backendCode = "";
                String frontendCode = "";
                String databaseCode = "";
                String devopsCode = "";
                String blueprintJson = convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(CODE_STRUCTURING_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of(
                    "backendCode", backendCode,
                    "frontendCode", frontendCode,
                    "databaseCode", databaseCode,
                    "devopsCode", devopsCode,
                    "blueprint", blueprintJson
                ));
                
                String structuredOutput = chatClient.prompt(prompt).call().content();
                
                logger.info("Code structuring completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "Code structured successfully", 
                    structuredOutput, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("Code structuring failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "Code structuring failed: " + e.getMessage(), 
                    processingTime);
            }
        });
    }
    
    private String convertBlueprintToJson(ProjectBlueprint blueprint) {
        // TODO: Implement proper JSON conversion using ObjectMapper
        return "{}"; // Placeholder for now
    }
}
