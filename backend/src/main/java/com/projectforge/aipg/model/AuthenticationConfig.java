package com.projectforge.aipg.model;

import java.util.List;
import java.util.Map;

/**
 * Authentication configuration
 */
public class AuthenticationConfig {
    private String type;
    private String provider;
    private Map<String, String> settings;
    private List<String> roles;
    private List<String> permissions;
    
    public AuthenticationConfig() {}
    
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    
    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }
    
    public Map<String, String> getSettings() { return settings; }
    public void setSettings(Map<String, String> settings) { this.settings = settings; }
    
    public List<String> getRoles() { return roles; }
    public void setRoles(List<String> roles) { this.roles = roles; }
    
    public List<String> getPermissions() { return permissions; }
    public void setPermissions(List<String> permissions) { this.permissions = permissions; }
}
