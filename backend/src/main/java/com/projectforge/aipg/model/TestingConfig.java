package com.projectforge.aipg.model;

import java.util.List;
import java.util.Map;

/**
 * Testing configuration
 */
public class TestingConfig {
    private List<String> types;
    private String framework;
    private List<String> testCases;
    private Map<String, Object> coverage;
    
    public TestingConfig() {}
    
    public List<String> getTypes() { return types; }
    public void setTypes(List<String> types) { this.types = types; }
    
    public String getFramework() { return framework; }
    public void setFramework(String framework) { this.framework = framework; }
    
    public List<String> getTestCases() { return testCases; }
    public void setTestCases(List<String> testCases) { this.testCases = testCases; }
    
    public Map<String, Object> getCoverage() { return coverage; }
    public void setCoverage(Map<String, Object> coverage) { this.coverage = coverage; }
}
