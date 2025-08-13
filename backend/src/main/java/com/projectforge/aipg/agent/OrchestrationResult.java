package com.projectforge.aipg.agent;

import java.util.List;

/**
 * Result of the entire orchestration process
 */
public class OrchestrationResult {
    private final List<AgentResult> agentResults;
    private final boolean success;
    private final long totalProcessingTimeMs;
    
    public OrchestrationResult(List<AgentResult> agentResults, boolean success, long totalProcessingTimeMs) {
        this.agentResults = agentResults;
        this.success = success;
        this.totalProcessingTimeMs = totalProcessingTimeMs;
    }
    
    public List<AgentResult> getAgentResults() { return agentResults; }
    public boolean isSuccess() { return success; }
    public long getTotalProcessingTimeMs() { return totalProcessingTimeMs; }
}
