package com.projectforge.aipg.agent;

/**
 * Information about a registered agent
 */
public class AgentInfo {
    private final String name;
    private final String description;
    private final int priority;
    
    public AgentInfo(String name, String description, int priority) {
        this.name = name;
        this.description = description;
        this.priority = priority;
    }
    
    public String getName() { return name; }
    public String getDescription() { return description; }
    public int getPriority() { return priority; }
}
