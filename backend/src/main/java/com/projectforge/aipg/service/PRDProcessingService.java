package com.projectforge.aipg.service;

import com.projectforge.aipg.model.ProjectBlueprint;
import com.projectforge.aipg.model.ProjectInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.chat.prompt.PromptTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Service for processing PRD documents and extracting project blueprints
 */
@Service
public class PRDProcessingService {
    
    private static final Logger logger = LoggerFactory.getLogger(PRDProcessingService.class);
    
    private final ChatClient chatClient;
    
    private static final String PRD_ANALYSIS_PROMPT = """
        You are a senior business analyst and software architect. Analyze the provided PRD (Product Requirements Document) 
        and extract a comprehensive project blueprint that can be used to generate complete frontend and backend code.
        
        PRD Content: {prdContent}
        Project Name: {projectName}
        
        Create a detailed project blueprint that includes:
        
        1. PROJECT OVERVIEW:
           - Extract project name, description, and objectives
           - Identify target users and use cases
           - Determine project scope and constraints
        
        2. FUNCTIONAL REQUIREMENTS:
           - List all features and capabilities
           - Define user stories and acceptance criteria
           - Identify business rules and validation logic
           - Extract workflow and process definitions
        
        3. TECHNICAL ARCHITECTURE:
           - Recommend technology stack (Spring Boot + Angular)
           - Define system architecture and components
           - Identify integration points and dependencies
           - Specify performance and scalability requirements
        
        4. DATABASE DESIGN:
           - Extract data entities and relationships
           - Define database schema and constraints
           - Identify data validation rules
           - Specify data migration and seeding requirements
        
        5. API SPECIFICATION:
           - Define REST API endpoints and operations
           - Specify request/response models
           - Identify authentication and authorization requirements
           - Define error handling and status codes
        
        6. USER INTERFACE:
           - Extract UI/UX requirements and layouts
           - Define user interaction flows
           - Identify form structures and validation
           - Specify responsive design requirements
        
        7. SECURITY REQUIREMENTS:
           - Identify authentication mechanisms
           - Define authorization and access control
           - Specify data protection requirements
           - Extract compliance and audit needs
        
        8. DEPLOYMENT CONFIGURATION:
           - Recommend deployment architecture
           - Define environment configurations
           - Specify monitoring and logging requirements
           - Identify backup and disaster recovery needs
        
        Return the analysis as a structured JSON object that matches the ProjectBlueprint model structure.
        Ensure all extracted information is comprehensive and actionable for code generation.
        
        If any information is missing or unclear, make reasonable assumptions based on industry best practices.
        """;
    
    public PRDProcessingService(ChatClient chatClient) {
        this.chatClient = chatClient;
    }
    
    /**
     * Process PRD document asynchronously
     */
    public CompletableFuture<ProjectBlueprint> processPRDAsync(
            MultipartFile file, String projectName, String sessionId) {
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                logger.info("Processing PRD for session: {}", sessionId);
                
                // Extract text content from file
                String prdContent = extractTextContent(file);
                
                // Use AI to analyze PRD and create blueprint
                ProjectBlueprint blueprint = analyzePRDWithAI(prdContent, projectName);
                
                // Store blueprint for later use
                // In a real implementation, this would be stored in a database or cache
                
                logger.info("PRD processing completed for session: {}", sessionId);
                return blueprint;
                
            } catch (Exception e) {
                logger.error("PRD processing failed for session: {}", sessionId, e);
                throw new RuntimeException("PRD processing failed", e);
            }
        });
    }
    
    /**
     * Extract text content from uploaded file
     */
    private String extractTextContent(MultipartFile file) throws IOException {
        String filename = file.getOriginalFilename();
        
        if (filename == null) {
            throw new IllegalArgumentException("File name is null");
        }
        
        String extension = filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
        
        switch (extension) {
            case "txt":
                return new String(file.getBytes(), StandardCharsets.UTF_8);
            
            case "pdf":
                return extractFromPDF(file);
            
            case "doc":
            case "docx":
                return extractFromWord(file);
            
            default:
                throw new IllegalArgumentException("Unsupported file type: " + extension);
        }
    }
    
    /**
     * Extract text from PDF file
     */
    private String extractFromPDF(MultipartFile file) throws IOException {
        // Implementation would use Apache PDFBox or similar library
        // For now, return placeholder
        logger.info("Extracting text from PDF: {}", file.getOriginalFilename());
        return "PDF content extraction placeholder";
    }
    
    /**
     * Extract text from Word document
     */
    private String extractFromWord(MultipartFile file) throws IOException {
        // Implementation would use Apache POI
        // For now, return placeholder
        logger.info("Extracting text from Word document: {}", file.getOriginalFilename());
        return "Word document content extraction placeholder";
    }
    
    /**
     * Use AI to analyze PRD content and create project blueprint
     */
    private ProjectBlueprint analyzePRDWithAI(String prdContent, String projectName) {
        try {
            logger.info("Analyzing PRD content with AI...");
            
            PromptTemplate promptTemplate = new PromptTemplate(PRD_ANALYSIS_PROMPT);
            Prompt prompt = promptTemplate.create(Map.of(
                "prdContent", prdContent,
                "projectName", projectName != null ? projectName : "Generated Project"
            ));
            
            String analysisResult = chatClient.prompt(prompt).call().content();
            
            // Parse AI response into ProjectBlueprint object
            ProjectBlueprint blueprint = parseAnalysisResult(analysisResult);
            
            logger.info("PRD analysis completed successfully");
            return blueprint;
            
        } catch (Exception e) {
            logger.error("AI analysis failed", e);
            throw new RuntimeException("PRD analysis failed", e);
        }
    }
    
    /**
     * Parse AI analysis result into ProjectBlueprint object
     */
    private ProjectBlueprint parseAnalysisResult(String analysisResult) {
        // In a real implementation, this would parse the JSON response
        // and create a proper ProjectBlueprint object
        
        ProjectBlueprint blueprint = new ProjectBlueprint();
        
        // Create and set project info
        ProjectInfo projectInfo = new ProjectInfo();
        projectInfo.setName("Sample Project");
        projectInfo.setDescription("Generated from PRD analysis");
        projectInfo.setVersion("1.0.0");
        blueprint.setProjectInfo(projectInfo);
        
        // Set other properties based on analysis result
        // This would involve JSON parsing and object mapping
        
        return blueprint;
    }
}
