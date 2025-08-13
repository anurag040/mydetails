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
 * AI Agent responsible for generating comprehensive test suites and QA automation
 */
@Component
public class QATestingAgent implements ProjectAgent {
    
    private static final Logger logger = LoggerFactory.getLogger(QATestingAgent.class);
    
    private final ChatClient chatClient;
    
    private static final String QA_GENERATION_PROMPT = """
        You are a QA engineer and test automation expert. Based on the project blueprint provided, 
        generate comprehensive test suites, automation scripts, and quality assurance configurations.
        
        Project Blueprint: {blueprint}
        
        Generate a JSON object where keys are file paths for test files (e.g., "src/test/java/com/example/MyServiceTest.java")
        and values are the complete content of those test files.
        
        Requirements:
        - Create JUnit 5 tests for all backend services and components.
        - Create Angular unit tests with Jasmine/Karma for frontend components and services.
        - Include both positive and negative test cases.
        - Use modern testing frameworks and tools.
        - Generate production-ready test code.
        
        Return ONLY the JSON object with test file paths and their content.
        """;
    
    public QATestingAgent(ChatClient chatClient) {
        this.chatClient = chatClient;
    }
    
    @Override
    public String getAgentName() {
        return "QA-Testing-Generator";
    }
    
    @Override
    public String getDescription() {
        return "Generates comprehensive test suites, QA automation, and quality assurance configurations";
    }
    
    @Override
    public boolean canProcess(ProjectBlueprint blueprint) {
        // QA agent can process any blueprint - testing is always needed
        return true;
    }
    
    @Override
    public int getPriority() {
        return 70; // After application code and DevOps setup
    }
    
    @Override
    public CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                logger.info("QA Testing Agent starting test generation...");
                
                String blueprintJson = convertBlueprintToJson(blueprint);
                
                PromptTemplate promptTemplate = new PromptTemplate(QA_GENERATION_PROMPT);
                Prompt prompt = promptTemplate.create(Map.of("blueprint", blueprintJson));
                
                String generatedTests = chatClient.prompt(prompt).call().content();
                
                logger.info("QA test generation completed successfully");
                
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.success(getAgentName(), 
                    "QA tests generated successfully", 
                    generatedTests, 
                    processingTime);
                
            } catch (Exception e) {
                logger.error("QA test generation failed", e);
                long processingTime = System.currentTimeMillis() - startTime;
                return AgentResult.failure(getAgentName(), 
                    "QA test generation failed: " + e.getMessage(), 
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
