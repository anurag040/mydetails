package com.projectforge.aipg.agent;

import com.projectforge.aipg.model.ProjectBlueprint;
import java.util.concurrent.CompletableFuture;

/**
 * Base interface for all AI agents in the system
 */
public interface ProjectAgent {
    
    /**
     * Get the agent name for identification
     */
    String getAgentName();
    
    /**
     * Get the agent description
     */
    String getDescription();
    
    /**
     * Check if this agent can handle the given blueprint section
     */
    boolean canProcess(ProjectBlueprint blueprint);
    
    /**
     * Execute the agent's processing asynchronously
     * @param blueprint The project blueprint
     * @return CompletableFuture with the processing result
     */
    CompletableFuture<AgentResult> processAsync(ProjectBlueprint blueprint);
    
    /**
     * Get the agent's priority (lower number = higher priority)
     */
    default int getPriority() {
        return 100;
    }
}
