package com.projectforge.aipg.agent;

/**
 * Result from agent processing
 */
public class AgentResult {
    private final String agentName;
    private final boolean success;
    private final String message;
    private final Object result;
    private final long processingTimeMs;
    
    public AgentResult(String agentName, boolean success, String message, Object result, long processingTimeMs) {
        this.agentName = agentName;
        this.success = success;
        this.message = message;
        this.result = result;
        this.processingTimeMs = processingTimeMs;
    }
    
    // Getters
    public String getAgentName() { return agentName; }
    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
    public Object getResult() { return result; }
    public long getProcessingTimeMs() { return processingTimeMs; }
    
    // Alias for getResult() for backward compatibility
    public Object getOutput() { return result; }
    
    // Static factory methods
    public static AgentResult success(String agentName, String message, Object result, long processingTimeMs) {
        return new AgentResult(agentName, true, message, result, processingTimeMs);
    }
    
    public static AgentResult failure(String agentName, String message, long processingTimeMs) {
        return new AgentResult(agentName, false, message, null, processingTimeMs);
    }
}
