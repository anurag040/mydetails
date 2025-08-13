package com.projectforge.aipg.agent;

import com.projectforge.aipg.model.ProjectBlueprint;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

/**
 * Orchestrates the execution of multiple AI agents
 */
@Service
public class AgentOrchestrator {
    
    private static final Logger logger = LoggerFactory.getLogger(AgentOrchestrator.class);
    
    private final List<ProjectAgent> agents;
    private final ExecutorService executorService;
    
    @Autowired
    public AgentOrchestrator(List<ProjectAgent> agents) {
        this.agents = agents.stream()
                .sorted((a, b) -> Integer.compare(a.getPriority(), b.getPriority()))
                .collect(Collectors.toList());
        this.executorService = Executors.newFixedThreadPool(4);
        
        logger.info("Initialized AgentOrchestrator with {} agents", agents.size());
        agents.forEach(agent -> logger.info("Registered agent: {} - {}", 
            agent.getAgentName(), agent.getDescription()));
    }
    
    /**
     * Execute all applicable agents on the blueprint
     */
    public CompletableFuture<OrchestrationResult> executeAgents(ProjectBlueprint blueprint) {
        logger.info("Starting agent orchestration for project: {}", 
            blueprint.getProjectInfo() != null ? blueprint.getProjectInfo().getName() : "Unknown");
        
        long startTime = System.currentTimeMillis();
        
        // Filter agents that can process this blueprint
        List<ProjectAgent> applicableAgents = agents.stream()
                .filter(agent -> agent.canProcess(blueprint))
                .collect(Collectors.toList());
        
        logger.info("Found {} applicable agents", applicableAgents.size());
        
        // Execute agents
        List<CompletableFuture<AgentResult>> futures = applicableAgents.stream()
                .map(agent -> agent.processAsync(blueprint))
                .collect(Collectors.toList());
        
        // Combine all results
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .thenApply(v -> {
                    List<AgentResult> results = futures.stream()
                            .map(CompletableFuture::join)
                            .collect(Collectors.toList());
                    
                    long totalTime = System.currentTimeMillis() - startTime;
                    
                    boolean allSuccess = results.stream().allMatch(AgentResult::isSuccess);
                    
                    logger.info("Agent orchestration completed in {}ms. Success: {}", 
                        totalTime, allSuccess);
                    
                    return new OrchestrationResult(results, allSuccess, totalTime);
                })
                .exceptionally(throwable -> {
                    logger.error("Agent orchestration failed", throwable);
                    long totalTime = System.currentTimeMillis() - startTime;
                    return new OrchestrationResult(List.of(), false, totalTime);
                });
    }
    
    /**
     * Synchronous version of executeAgents for simpler service integration
     */
    public List<AgentResult> orchestrateProject(ProjectBlueprint blueprint) {
        try {
            OrchestrationResult result = executeAgents(blueprint).get();
            return result.getAgentResults();
        } catch (Exception e) {
            logger.error("Failed to orchestrate project", e);
            return List.of();
        }
    }
    
    /**
     * Get information about all registered agents
     */
    public List<AgentInfo> getAgentInfo() {
        return agents.stream()
                .map(agent -> new AgentInfo(
                    agent.getAgentName(),
                    agent.getDescription(),
                    agent.getPriority()
                ))
                .collect(Collectors.toList());
    }
}
