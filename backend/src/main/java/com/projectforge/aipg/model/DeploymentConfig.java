package com.projectforge.aipg.model;

import java.util.List;
import java.util.Map;

/**
 * Deployment configuration
 */
public class DeploymentConfig {
    private String type;
    private Map<String, String> environment;
    private DockerConfig docker;
    private CloudConfig cloud;
    
    public DeploymentConfig() {}
    
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    
    public Map<String, String> getEnvironment() { return environment; }
    public void setEnvironment(Map<String, String> environment) { this.environment = environment; }
    
    public DockerConfig getDocker() { return docker; }
    public void setDocker(DockerConfig docker) { this.docker = docker; }
    
    public CloudConfig getCloud() { return cloud; }
    public void setCloud(CloudConfig cloud) { this.cloud = cloud; }
    
    public static class DockerConfig {
        private String baseImage;
        private List<String> ports;
        private Map<String, String> environment;
        private List<String> volumes;
        
        public DockerConfig() {}
        
        public String getBaseImage() { return baseImage; }
        public void setBaseImage(String baseImage) { this.baseImage = baseImage; }
        
        public List<String> getPorts() { return ports; }
        public void setPorts(List<String> ports) { this.ports = ports; }
        
        public Map<String, String> getEnvironment() { return environment; }
        public void setEnvironment(Map<String, String> environment) { this.environment = environment; }
        
        public List<String> getVolumes() { return volumes; }
        public void setVolumes(List<String> volumes) { this.volumes = volumes; }
    }
    
    public static class CloudConfig {
        private String provider;
        private String region;
        private Map<String, Object> resources;
        
        public CloudConfig() {}
        
        public String getProvider() { return provider; }
        public void setProvider(String provider) { this.provider = provider; }
        
        public String getRegion() { return region; }
        public void setRegion(String region) { this.region = region; }
        
        public Map<String, Object> getResources() { return resources; }
        public void setResources(Map<String, Object> resources) { this.resources = resources; }
    }
}
