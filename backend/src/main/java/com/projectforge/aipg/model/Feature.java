package com.projectforge.aipg.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;
import java.util.Map;

/**
 * Represents a feature from the PRD
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class Feature {
    private String id;
    private String name;
    private String description;
    private String priority;
    private List<String> userStories;
    private List<String> acceptanceCriteria;
    private Map<String, Object> requirements;
    
    public Feature() {}
    
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public String getPriority() { return priority; }
    public void setPriority(String priority) { this.priority = priority; }
    
    public List<String> getUserStories() { return userStories; }
    public void setUserStories(List<String> userStories) { this.userStories = userStories; }
    
    public List<String> getAcceptanceCriteria() { return acceptanceCriteria; }
    public void setAcceptanceCriteria(List<String> acceptanceCriteria) { this.acceptanceCriteria = acceptanceCriteria; }
    
    public Map<String, Object> getRequirements() { return requirements; }
    public void setRequirements(Map<String, Object> requirements) { this.requirements = requirements; }
}
