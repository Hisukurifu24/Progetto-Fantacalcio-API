package com.appfantacalcio.config;

import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Component
@RequiredArgsConstructor
@Slf4j
public class DatabaseFixer implements CommandLineRunner {

	private final JdbcTemplate jdbcTemplate;

	@Override
	public void run(String... args) throws Exception {
		try {
			log.info("Attempting to drop outdated constraint competition_type_check...");
			jdbcTemplate.execute("ALTER TABLE competition DROP CONSTRAINT IF EXISTS competition_type_check");
			log.info("Constraint dropped successfully (if it existed).");
		} catch (Exception e) {
			log.warn("Failed to drop constraint: " + e.getMessage());
		}
	}
}
