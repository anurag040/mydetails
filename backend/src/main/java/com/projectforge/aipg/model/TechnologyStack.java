package com.projectforge.aipg.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * Technology stack configuration
 */
public class TechnologyStack {
    private Frontend frontend;
    private Backend backend;
    private Database database;
    private String buildTool;
    
    public TechnologyStack() {}
    
    public Frontend getFrontend() { return frontend; }
    public void setFrontend(Frontend frontend) { this.frontend = frontend; }
    
    public Backend getBackend() { return backend; }
    public void setBackend(Backend backend) { this.backend = backend; }
    
    public Database getDatabase() { return database; }
    public void setDatabase(Database database) { this.database = database; }
    
    public String getBuildTool() { return buildTool; }
    public void setBuildTool(String buildTool) { this.buildTool = buildTool; }
    
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Frontend {
        private String framework;
        private String version;
        private List<String> uiLibraries;
        
        public Frontend() {}
        
        public String getFramework() { return framework; }
        public void setFramework(String framework) { this.framework = framework; }
        
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        
        public List<String> getUiLibraries() { return uiLibraries; }
        public void setUiLibraries(List<String> uiLibraries) { this.uiLibraries = uiLibraries; }
    }
    
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Backend {
        private String framework;
        private String version;
        private String language;
        private String runtime;
        
        public Backend() {}
        
        public String getFramework() { return framework; }
        public void setFramework(String framework) { this.framework = framework; }
        
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        
        public String getLanguage() { return language; }
        public void setLanguage(String language) { this.language = language; }
        
        public String getRuntime() { return runtime; }
        public void setRuntime(String runtime) { this.runtime = runtime; }
    }
    
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Database {
        private String type;
        private String version;
        private List<String> additional;
        
        public Database() {}
        
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        
        public List<String> getAdditional() { return additional; }
        public void setAdditional(List<String> additional) { this.additional = additional; }
    }
}
