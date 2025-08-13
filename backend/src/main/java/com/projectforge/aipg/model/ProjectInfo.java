package com.projectforge.aipg.model;

import java.util.Map;

/**
 * Basic project information
 */
public class ProjectInfo {
    private String name;
    private String description;
    private String version;
    private String packageName;
    private Map<String, String> metadata;
    
    // Constructors, getters and setters
    public ProjectInfo() {}
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }
    
    public String getPackageName() { return packageName; }
    public void setPackageName(String packageName) { this.packageName = packageName; }
    
    public Map<String, String> getMetadata() { return metadata; }
    public void setMetadata(Map<String, String> metadata) { this.metadata = metadata; }
}
