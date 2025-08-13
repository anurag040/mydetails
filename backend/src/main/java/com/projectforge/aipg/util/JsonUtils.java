package com.projectforge.aipg.util;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.projectforge.aipg.model.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.ArrayList;

/**
 * Utility class for JSON operations
 */
@Component
public class JsonUtils {
    
    private static final Logger logger = LoggerFactory.getLogger(JsonUtils.class);
    
    private final ObjectMapper objectMapper;
    
    public JsonUtils() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
        this.objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    }
    
    /**
     * Convert ProjectBlueprint to JSON string
     */
    public String convertBlueprintToJson(ProjectBlueprint blueprint) {
        try {
            return objectMapper.writeValueAsString(blueprint);
        } catch (JsonProcessingException e) {
            logger.error("Failed to convert blueprint to JSON", e);
            return "{}";
        }
    }
    
    /**
     * Convert JSON string to ProjectBlueprint
     */
    public ProjectBlueprint convertJsonToBlueprint(String json) {
        try {
            // Clean the JSON string from AI response artifacts
            String cleanJson = cleanAIResponseJson(json);
            return objectMapper.readValue(cleanJson, ProjectBlueprint.class);
        } catch (JsonProcessingException e) {
            logger.warn("Direct JSON parsing failed, attempting to fix structure: {}", e.getMessage());
            
            try {
                // Try to fix common JSON structure issues
                String fixedJson = fixBlueprintJsonStructure(json);
                return objectMapper.readValue(fixedJson, ProjectBlueprint.class);
            } catch (JsonProcessingException e2) {
                logger.error("Failed to convert JSON to blueprint even after fixes", e2);
                // Return a minimal valid blueprint as fallback
                return createMinimalBlueprint();
            }
        }
    }
    
    /**
     * Create a minimal valid blueprint as fallback
     */
    private ProjectBlueprint createMinimalBlueprint() {
        ProjectBlueprint blueprint = new ProjectBlueprint();
        
        // Set basic project info
        ProjectInfo projectInfo = new ProjectInfo();
        projectInfo.setName("Generated Project");
        projectInfo.setDescription("AI-generated project from PRD");
        projectInfo.setVersion("1.0.0");
        projectInfo.setPackageName("com.generated.app");
        blueprint.setProjectInfo(projectInfo);
        
        // Set comprehensive technology stack
        TechnologyStack techStack = new TechnologyStack();
        
        TechnologyStack.Backend backend = new TechnologyStack.Backend();
        backend.setFramework("Spring Boot");
        backend.setVersion("3.2.0");
        backend.setLanguage("Java");
        backend.setRuntime("JDK 17");
        techStack.setBackend(backend);
        
        TechnologyStack.Frontend frontend = new TechnologyStack.Frontend();
        frontend.setFramework("Angular");
        frontend.setVersion("17.0.0");
        frontend.setUiLibraries(List.of("Angular Material", "RxJS"));
        techStack.setFrontend(frontend);
        
        TechnologyStack.Database database = new TechnologyStack.Database();
        database.setType("PostgreSQL");
        database.setVersion("15.0");
        database.setAdditional(List.of("Flyway Migration", "Connection Pooling"));
        techStack.setDatabase(database);
        
        techStack.setBuildTool("Maven");
        blueprint.setTechnologyStack(techStack);
        
        // Add realistic features
        List<Feature> features = new ArrayList<>();
        
        Feature userManagement = new Feature();
        userManagement.setId("user-management");
        userManagement.setName("User Management");
        userManagement.setDescription("User registration, authentication, and profile management");
        userManagement.setPriority("HIGH");
        userManagement.setUserStories(List.of(
            "As a user, I want to register an account",
            "As a user, I want to login securely",
            "As a user, I want to manage my profile"
        ));
        features.add(userManagement);
        
        Feature dataManagement = new Feature();
        dataManagement.setId("data-management");
        dataManagement.setName("Data Management");
        dataManagement.setDescription("CRUD operations for core business entities");
        dataManagement.setPriority("HIGH");
        dataManagement.setUserStories(List.of(
            "As a user, I want to create new records",
            "As a user, I want to view existing records",
            "As a user, I want to update records",
            "As a user, I want to delete records"
        ));
        features.add(dataManagement);
        
        Feature dashboard = new Feature();
        dashboard.setId("dashboard");
        dashboard.setName("Dashboard");
        dashboard.setDescription("Overview and analytics dashboard");
        dashboard.setPriority("MEDIUM");
        dashboard.setUserStories(List.of(
            "As a user, I want to see an overview of my data",
            "As a user, I want to view analytics and charts"
        ));
        features.add(dashboard);
        
        blueprint.setFeatures(features);
        
        // Add realistic API endpoints
        List<ApiEndpoint> apiEndpoints = new ArrayList<>();
        
        ApiEndpoint authEndpoint = new ApiEndpoint();
        authEndpoint.setPath("/api/auth/login");
        authEndpoint.setMethod("POST");
        authEndpoint.setDescription("User authentication endpoint");
        apiEndpoints.add(authEndpoint);
        
        ApiEndpoint userEndpoint = new ApiEndpoint();
        userEndpoint.setPath("/api/users");
        userEndpoint.setMethod("GET");
        userEndpoint.setDescription("Get all users");
        apiEndpoints.add(userEndpoint);
        
        ApiEndpoint userCreateEndpoint = new ApiEndpoint();
        userCreateEndpoint.setPath("/api/users");
        userCreateEndpoint.setMethod("POST");
        userCreateEndpoint.setDescription("Create new user");
        apiEndpoints.add(userCreateEndpoint);
        
        ApiEndpoint dataEndpoint = new ApiEndpoint();
        dataEndpoint.setPath("/api/data");
        dataEndpoint.setMethod("GET");
        dataEndpoint.setDescription("Get all data records");
        apiEndpoints.add(dataEndpoint);
        
        blueprint.setApiEndpoints(apiEndpoints);
        
        // Add database schema
        DatabaseSchema databaseSchema = new DatabaseSchema();
        
        List<DatabaseSchema.Entity> entities = new ArrayList<>();
        
        // User entity
        DatabaseSchema.Entity userEntity = new DatabaseSchema.Entity();
        userEntity.setName("User");
        userEntity.setTableName("users");
        
        List<DatabaseSchema.Field> userFields = new ArrayList<>();
        
        DatabaseSchema.Field idField = new DatabaseSchema.Field();
        idField.setName("id");
        idField.setType("BIGINT");
        idField.setPrimaryKey(true);
        idField.setNullable(false);
        userFields.add(idField);
        
        DatabaseSchema.Field usernameField = new DatabaseSchema.Field();
        usernameField.setName("username");
        usernameField.setType("VARCHAR(255)");
        usernameField.setNullable(false);
        userFields.add(usernameField);
        
        DatabaseSchema.Field emailField = new DatabaseSchema.Field();
        emailField.setName("email");
        emailField.setType("VARCHAR(255)");
        emailField.setNullable(false);
        userFields.add(emailField);
        
        DatabaseSchema.Field passwordField = new DatabaseSchema.Field();
        passwordField.setName("password");
        passwordField.setType("VARCHAR(255)");
        passwordField.setNullable(false);
        userFields.add(passwordField);
        
        userEntity.setFields(userFields);
        entities.add(userEntity);
        
        // Data Record entity
        DatabaseSchema.Entity dataEntity = new DatabaseSchema.Entity();
        dataEntity.setName("DataRecord");
        dataEntity.setTableName("data_records");
        
        List<DatabaseSchema.Field> dataFields = new ArrayList<>();
        
        DatabaseSchema.Field dataIdField = new DatabaseSchema.Field();
        dataIdField.setName("id");
        dataIdField.setType("BIGINT");
        dataIdField.setPrimaryKey(true);
        dataIdField.setNullable(false);
        dataFields.add(dataIdField);
        
        DatabaseSchema.Field nameField = new DatabaseSchema.Field();
        nameField.setName("name");
        nameField.setType("VARCHAR(255)");
        nameField.setNullable(false);
        dataFields.add(nameField);
        
        DatabaseSchema.Field descriptionField = new DatabaseSchema.Field();
        descriptionField.setName("description");
        descriptionField.setType("TEXT");
        descriptionField.setNullable(true);
        dataFields.add(descriptionField);
        
        DatabaseSchema.Field userIdField = new DatabaseSchema.Field();
        userIdField.setName("user_id");
        userIdField.setType("BIGINT");
        userIdField.setNullable(true);
        dataFields.add(userIdField);
        
        dataEntity.setFields(dataFields);
        entities.add(dataEntity);
        
        databaseSchema.setEntities(entities);
        blueprint.setDatabaseSchema(databaseSchema);
        
        logger.info("Created comprehensive fallback blueprint with {} features, {} API endpoints, {} database entities", 
                   features.size(), apiEndpoints.size(), entities.size());
        return blueprint;
    }
    
    /**
     * Fix common JSON structure issues in AI-generated blueprint JSON
     */
    private String fixBlueprintJsonStructure(String json) {
        try {
            // Clean the JSON first
            String cleanJson = cleanAIResponseJson(json);
            
            // Parse as generic JSON first
            JsonNode rootNode = objectMapper.readTree(cleanJson);
            
            // Create a new blueprint structure
            ObjectNode fixedBlueprint = objectMapper.createObjectNode();
            
            // Fix project_info
            if (rootNode.has("project_info")) {
                fixedBlueprint.set("project_info", rootNode.get("project_info"));
            } else if (rootNode.has("projectInfo")) {
                fixedBlueprint.set("project_info", rootNode.get("projectInfo"));
            }
            
            // Fix technology_stack
            if (rootNode.has("technology_stack")) {
                JsonNode techStackNode = rootNode.get("technology_stack");
                ObjectNode fixedTechStack = objectMapper.createObjectNode();
                
                // Copy backend and frontend as-is
                if (techStackNode.has("backend")) {
                    fixedTechStack.set("backend", techStackNode.get("backend"));
                }
                if (techStackNode.has("frontend")) {
                    fixedTechStack.set("frontend", techStackNode.get("frontend"));
                }
                
                // Fix database.additional field if it's an object instead of array
                if (techStackNode.has("database")) {
                    JsonNode databaseNode = techStackNode.get("database");
                    ObjectNode fixedDatabase = objectMapper.createObjectNode();
                    
                    // Copy type and version
                    if (databaseNode.has("type")) {
                        fixedDatabase.set("type", databaseNode.get("type"));
                    }
                    if (databaseNode.has("version")) {
                        fixedDatabase.set("version", databaseNode.get("version"));
                    }
                    
                    // Fix additional field
                    if (databaseNode.has("additional")) {
                        JsonNode additionalNode = databaseNode.get("additional");
                        if (additionalNode.isObject() && !additionalNode.isArray()) {
                            // Convert object to array of strings
                            ArrayNode additionalArray = objectMapper.createArrayNode();
                            additionalNode.fields().forEachRemaining(entry -> {
                                additionalArray.add(entry.getKey() + ":" + entry.getValue().asText());
                            });
                            fixedDatabase.set("additional", additionalArray);
                        } else {
                            fixedDatabase.set("additional", additionalNode);
                        }
                    }
                    
                    fixedTechStack.set("database", fixedDatabase);
                }
                
                // Copy buildTool
                if (techStackNode.has("buildTool")) {
                    fixedTechStack.set("buildTool", techStackNode.get("buildTool"));
                }
                
                fixedBlueprint.set("technology_stack", fixedTechStack);
            } else if (rootNode.has("technologyStack")) {
                fixedBlueprint.set("technology_stack", rootNode.get("technologyStack"));
            }
            
            // Fix features - ensure it's an array and fix requirements field
            if (rootNode.has("features")) {
                JsonNode featuresNode = rootNode.get("features");
                if (featuresNode.isObject() && !featuresNode.isArray()) {
                    // Convert object to array
                    ArrayNode featuresArray = objectMapper.createArrayNode();
                    featuresNode.fields().forEachRemaining(entry -> {
                        ObjectNode feature = objectMapper.createObjectNode();
                        feature.put("id", entry.getKey());
                        if (entry.getValue().isObject()) {
                            ObjectNode featureObj = (ObjectNode) entry.getValue();
                            feature.setAll(featureObj);
                        } else {
                            feature.put("description", entry.getValue().asText());
                        }
                        featuresArray.add(feature);
                    });
                    fixedBlueprint.set("features", featuresArray);
                } else if (featuresNode.isArray()) {
                    // Fix requirements field in each feature
                    ArrayNode fixedFeaturesArray = objectMapper.createArrayNode();
                    for (JsonNode featureNode : featuresNode) {
                        ObjectNode fixedFeature = objectMapper.createObjectNode();
                        
                        // Copy all fields
                        featureNode.fields().forEachRemaining(entry -> {
                            String fieldName = entry.getKey();
                            JsonNode fieldValue = entry.getValue();
                            
                            if ("requirements".equals(fieldName) && fieldValue.isArray()) {
                                // Convert array to map
                                ObjectNode requirementsMap = objectMapper.createObjectNode();
                                for (int i = 0; i < fieldValue.size(); i++) {
                                    JsonNode reqItem = fieldValue.get(i);
                                    if (reqItem.isTextual()) {
                                        requirementsMap.put("requirement_" + i, reqItem.asText());
                                    } else if (reqItem.isObject()) {
                                        // If it's already an object, merge it
                                        reqItem.fields().forEachRemaining(subEntry -> {
                                            requirementsMap.set(subEntry.getKey(), subEntry.getValue());
                                        });
                                    }
                                }
                                fixedFeature.set("requirements", requirementsMap);
                            } else {
                                fixedFeature.set(fieldName, fieldValue);
                            }
                        });
                        
                        fixedFeaturesArray.add(fixedFeature);
                    }
                    fixedBlueprint.set("features", fixedFeaturesArray);
                } else {
                    fixedBlueprint.set("features", featuresNode);
                }
            }
            
            // Fix api_endpoints - ensure it's an array
            if (rootNode.has("api_endpoints")) {
                JsonNode apiEndpointsNode = rootNode.get("api_endpoints");
                if (apiEndpointsNode.isObject() && !apiEndpointsNode.isArray()) {
                    // Convert object to array
                    ArrayNode apiEndpointsArray = objectMapper.createArrayNode();
                    apiEndpointsNode.fields().forEachRemaining(entry -> {
                        ObjectNode endpoint = objectMapper.createObjectNode();
                        endpoint.put("path", "/" + entry.getKey());
                        if (entry.getValue().isObject()) {
                            ObjectNode endpointObj = (ObjectNode) entry.getValue();
                            endpoint.setAll(endpointObj);
                        } else {
                            endpoint.put("method", "GET");
                            endpoint.put("description", entry.getValue().asText());
                        }
                        apiEndpointsArray.add(endpoint);
                    });
                    fixedBlueprint.set("api_endpoints", apiEndpointsArray);
                } else {
                    fixedBlueprint.set("api_endpoints", apiEndpointsNode);
                }
            } else if (rootNode.has("apiEndpoints")) {
                JsonNode apiEndpointsNode = rootNode.get("apiEndpoints");
                if (apiEndpointsNode.isObject() && !apiEndpointsNode.isArray()) {
                    // Convert object to array
                    ArrayNode apiEndpointsArray = objectMapper.createArrayNode();
                    apiEndpointsNode.fields().forEachRemaining(entry -> {
                        ObjectNode endpoint = objectMapper.createObjectNode();
                        endpoint.put("path", "/" + entry.getKey());
                        if (entry.getValue().isObject()) {
                            ObjectNode endpointObj = (ObjectNode) entry.getValue();
                            endpoint.setAll(endpointObj);
                        } else {
                            endpoint.put("method", "GET");
                            endpoint.put("description", entry.getValue().asText());
                        }
                        apiEndpointsArray.add(endpoint);
                    });
                    fixedBlueprint.set("api_endpoints", apiEndpointsArray);
                } else {
                    fixedBlueprint.set("api_endpoints", apiEndpointsNode);
                }
            }
            
            // Fix database_schema - ensure it's an object, not an array
            if (rootNode.has("database_schema")) {
                JsonNode databaseSchemaNode = rootNode.get("database_schema");
                if (databaseSchemaNode.isArray()) {
                    // Convert array to object with tables field
                    ObjectNode schemaObject = objectMapper.createObjectNode();
                    schemaObject.set("tables", databaseSchemaNode);
                    fixedBlueprint.set("database_schema", schemaObject);
                } else {
                    fixedBlueprint.set("database_schema", databaseSchemaNode);
                }
            } else if (rootNode.has("databaseSchema")) {
                JsonNode databaseSchemaNode = rootNode.get("databaseSchema");
                if (databaseSchemaNode.isArray()) {
                    ObjectNode schemaObject = objectMapper.createObjectNode();
                    schemaObject.set("tables", databaseSchemaNode);
                    fixedBlueprint.set("database_schema", schemaObject);
                } else {
                    fixedBlueprint.set("database_schema", databaseSchemaNode);
                }
            }
            
            // Copy other fields as-is
            String[] otherFields = {
                "frontend_components", "frontendComponents",
                "business_logic", "businessLogic",
                "authentication", "deployment", "testing_requirements", "testing"
            };
            
            for (String field : otherFields) {
                if (rootNode.has(field)) {
                    String targetField = field.contains("_") ? field : convertToSnakeCase(field);
                    JsonNode fieldNode = rootNode.get(field);
                    
                    // Handle array-like fields that might be objects
                    if (field.contains("components") || field.contains("schema")) {
                        if (fieldNode.isObject() && !fieldNode.isArray()) {
                            // Convert object to array if expected to be array
                            ArrayNode arrayNode = objectMapper.createArrayNode();
                            fieldNode.fields().forEachRemaining(entry -> {
                                ObjectNode item = objectMapper.createObjectNode();
                                item.put("name", entry.getKey());
                                if (entry.getValue().isObject()) {
                                    item.setAll((ObjectNode) entry.getValue());
                                } else {
                                    item.put("description", entry.getValue().asText());
                                }
                                arrayNode.add(item);
                            });
                            fixedBlueprint.set(targetField, arrayNode);
                        } else {
                            fixedBlueprint.set(targetField, fieldNode);
                        }
                    } else {
                        fixedBlueprint.set(targetField, fieldNode);
                    }
                }
            }
            
            return fixedBlueprint.toString();
            
        } catch (Exception e) {
            logger.error("Failed to fix JSON structure", e);
            return json; // Return original if fixing fails
        }
    }
    
    /**
     * Convert camelCase to snake_case
     */
    private String convertToSnakeCase(String camelCase) {
        return camelCase.replaceAll("([a-z])([A-Z])", "$1_$2").toLowerCase();
    }
    
    /**
     * Convert JSON string to specified class
     */
    public <T> T fromJson(String json, Class<T> clazz) {
        try {
            // Clean the JSON string from AI response artifacts
            String cleanJson = cleanAIResponseJson(json);
            return objectMapper.readValue(cleanJson, clazz);
        } catch (JsonProcessingException e) {
            logger.error("Failed to convert JSON to object", e);
            return null;
        }
    }
    
    /**
     * Clean AI response JSON by removing common artifacts
     */
    private String cleanAIResponseJson(String json) {
        if (json == null || json.trim().isEmpty()) {
            return "{}";
        }
        
        // Remove markdown code blocks
        json = json.replaceAll("```json\\s*", "").replaceAll("```\\s*", "");
        
        // Remove leading/trailing backticks
        json = json.replaceAll("^`+", "").replaceAll("`+$", "");
        
        // Find the first { and last } to extract JSON content
        int firstBrace = json.indexOf('{');
        int lastBrace = json.lastIndexOf('}');
        
        if (firstBrace != -1 && lastBrace != -1 && firstBrace < lastBrace) {
            json = json.substring(firstBrace, lastBrace + 1);
        }
        
        // Basic cleanup
        json = json.trim();
        
        // If still not valid JSON, return empty object
        if (!json.startsWith("{") || !json.endsWith("}")) {
            logger.warn("Unable to extract valid JSON from AI response, using empty object");
            return "{}";
        }
        
        return json;
    }
    
    /**
     * Convert any object to JSON string
     */
    public String toJson(Object object) {
        try {
            return objectMapper.writeValueAsString(object);
        } catch (JsonProcessingException e) {
            logger.error("Failed to convert object to JSON", e);
            return "{}";
        }
    }
}
