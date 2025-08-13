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
        
        Generate the following QA and testing components:
        
        1. UNIT TESTS:
           - Create JUnit 5 tests for all backend services and components
           - Add MockMvc tests for REST controllers
           - Include repository layer tests with @DataJpaTest
           - Create Angular unit tests with Jasmine/Karma
           - Add component and service tests for frontend
           - Include proper mocking and test data setup
        
        2. INTEGRATION TESTS:
           - Create @SpringBootTest integration tests
           - Add database integration tests with Testcontainers
           - Include API integration tests
           - Create end-to-end workflow tests
           - Add cross-service integration validation
        
        3. API TESTING:
           - Create Postman collections for API testing
           - Add REST Assured tests for API validation
           - Include contract testing with Pact
           - Add API performance tests
           - Create OpenAPI/Swagger test specifications
        
        4. END-TO-END TESTING:
           - Create Cypress or Playwright tests for frontend
           - Add user journey and workflow tests
           - Include cross-browser testing scenarios
           - Add mobile responsive testing
           - Create accessibility testing scripts
        
        5. PERFORMANCE TESTING:
           - Create JMeter test plans for load testing
           - Add stress testing scenarios
           - Include database performance tests
           - Add API response time validation
           - Create scalability testing scripts
        
        6. SECURITY TESTING:
           - Add OWASP security test cases
           - Include authentication and authorization tests
           - Create SQL injection and XSS prevention tests
           - Add dependency vulnerability scanning
           - Include security compliance validation
        
        7. TEST DATA MANAGEMENT:
           - Create test data factories and builders
           - Add database seeding for tests
           - Include test data cleanup utilities
           - Create mock data generators
           - Add test environment data management
        
        8. TEST AUTOMATION FRAMEWORK:
           - Set up test execution frameworks
           - Add test reporting and metrics
           - Include continuous testing in CI/CD
           - Create test environment management
           - Add test result analysis tools
        
        9. QUALITY GATES:
           - Define code coverage requirements
           - Add static code analysis (SonarQube)
           - Include performance benchmarks
           - Create quality metrics dashboards
           - Add automated quality checks
        
        Requirements:
        - Generate production-ready test code
        - Follow testing best practices and patterns
        - Include proper test isolation and cleanup
        - Add comprehensive test coverage
        - Use modern testing frameworks and tools
        - Include both positive and negative test cases
        - Add proper error handling and validation
        - Make tests maintainable and reliable
        
        Return the complete test structure as a JSON object with file paths and content.
        Structure: {"files": [{"path": "src/test/java/...", "content": "..."}]}
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
