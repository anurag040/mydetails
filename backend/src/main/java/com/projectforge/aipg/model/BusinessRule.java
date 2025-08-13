package com.projectforge.aipg.model;

import java.util.List;

/**
 * Business rule definition
 */
public class BusinessRule {
    private String id;
    private String name;
    private String description;
    private String condition;
    private String action;
    private String priority;
    private List<String> dependencies;
    
    public BusinessRule() {}
    
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public String getCondition() { return condition; }
    public void setCondition(String condition) { this.condition = condition; }
    
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    
    public String getPriority() { return priority; }
    public void setPriority(String priority) { this.priority = priority; }
    
    public List<String> getDependencies() { return dependencies; }
    public void setDependencies(List<String> dependencies) { this.dependencies = dependencies; }
}
