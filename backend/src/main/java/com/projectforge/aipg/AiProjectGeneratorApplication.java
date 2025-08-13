package com.projectforge.aipg;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class AiProjectGeneratorApplication {

	public static void main(String[] args) {
		SpringApplication.run(AiProjectGeneratorApplication.class, args);
	}

}
