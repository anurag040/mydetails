package com.projectforge.aipg.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

/**
 * JSON Blueprint representation of a PRD analysis
 * This serves as the communication format between agents
 */
public class ProjectBlueprint {
    
    @JsonProperty("project_info")
    private ProjectInfo projectInfo;
    
    @JsonProperty("technology_stack")
    private TechnologyStack technologyStack;
    
    @JsonProperty("features")
    private List<Feature> features;
    
    @JsonProperty("database_schema")
    private DatabaseSchema databaseSchema;
    
    @JsonProperty("api_endpoints")
    private List<ApiEndpoint> apiEndpoints;
    
    @JsonProperty("frontend_components")
    private List<FrontendComponent> frontendComponents;
    
    @JsonProperty("business_logic")
    private List<BusinessRule> businessLogic;
    
    @JsonProperty("authentication")
    private AuthenticationConfig authentication;
    
    @JsonProperty("deployment")
    private DeploymentConfig deployment;
    
    @JsonProperty("testing_requirements")
    private TestingConfig testing;
    
    // Constructors
    public ProjectBlueprint() {}
    
    // Getters and Setters
    public ProjectInfo getProjectInfo() { return projectInfo; }
    public void setProjectInfo(ProjectInfo projectInfo) { this.projectInfo = projectInfo; }
    
    public TechnologyStack getTechnologyStack() { return technologyStack; }
    public void setTechnologyStack(TechnologyStack technologyStack) { this.technologyStack = technologyStack; }
    
    public List<Feature> getFeatures() { return features; }
    public void setFeatures(List<Feature> features) { this.features = features; }
    
    public DatabaseSchema getDatabaseSchema() { return databaseSchema; }
    public void setDatabaseSchema(DatabaseSchema databaseSchema) { this.databaseSchema = databaseSchema; }
    
    public List<ApiEndpoint> getApiEndpoints() { return apiEndpoints; }
    public void setApiEndpoints(List<ApiEndpoint> apiEndpoints) { this.apiEndpoints = apiEndpoints; }
    
    public List<FrontendComponent> getFrontendComponents() { return frontendComponents; }
    public void setFrontendComponents(List<FrontendComponent> frontendComponents) { this.frontendComponents = frontendComponents; }
    
    public List<BusinessRule> getBusinessLogic() { return businessLogic; }
    public void setBusinessLogic(List<BusinessRule> businessLogic) { this.businessLogic = businessLogic; }
    
    public AuthenticationConfig getAuthentication() { return authentication; }
    public void setAuthentication(AuthenticationConfig authentication) { this.authentication = authentication; }
    
    public DeploymentConfig getDeployment() { return deployment; }
    public void setDeployment(DeploymentConfig deployment) { this.deployment = deployment; }
    
    public TestingConfig getTesting() { return testing; }
    public void setTesting(TestingConfig testing) { this.testing = testing; }
}
