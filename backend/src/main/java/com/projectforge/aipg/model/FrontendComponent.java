package com.projectforge.aipg.model;

import java.util.List;
import java.util.Map;

/**
 * Frontend component definition
 */
public class FrontendComponent {
    private String name;
    private String type;
    private String path;
    private String template;
    private List<String> dependencies;
    private Map<String, Object> properties;
    private List<String> methods;
    private List<String> routes;
    
    public FrontendComponent() {}
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    
    public String getPath() { return path; }
    public void setPath(String path) { this.path = path; }
    
    public String getTemplate() { return template; }
    public void setTemplate(String template) { this.template = template; }
    
    public List<String> getDependencies() { return dependencies; }
    public void setDependencies(List<String> dependencies) { this.dependencies = dependencies; }
    
    public Map<String, Object> getProperties() { return properties; }
    public void setProperties(Map<String, Object> properties) { this.properties = properties; }
    
    public List<String> getMethods() { return methods; }
    public void setMethods(List<String> methods) { this.methods = methods; }
    
    public List<String> getRoutes() { return routes; }
    public void setRoutes(List<String> routes) { this.routes = routes; }
}
