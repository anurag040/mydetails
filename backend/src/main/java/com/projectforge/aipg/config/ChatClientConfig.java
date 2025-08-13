package com.projectforge.aipg.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration class for Spring AI ChatClient.
 * Provides a ChatClient bean for dependency injection across the application.
 */
@Configuration
public class ChatClientConfig {

    /**
     * Creates a ChatClient bean from the auto-configured ChatModel.
     * 
     * @param chatModel The auto-configured ChatModel (e.g., OpenAI, Ollama, etc.)
     * @return ChatClient instance for use in agents and services
     */
    @Bean
    public ChatClient chatClient(ChatModel chatModel) {
        return ChatClient.create(chatModel);
    }
}
