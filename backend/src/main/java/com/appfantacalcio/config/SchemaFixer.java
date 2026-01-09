package com.appfantacalcio.config;

import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class SchemaFixer implements CommandLineRunner {

	private static final Logger logger = LoggerFactory.getLogger(SchemaFixer.class);
	private final JdbcTemplate jdbcTemplate;

	public SchemaFixer(JdbcTemplate jdbcTemplate) {
		this.jdbcTemplate = jdbcTemplate;
	}

	@Override
	public void run(String... args) throws Exception {
		logger.info("Checking and fixing database schema...");

		try {
			// Fix matches table to allow null teams (for cup placeholders)
			logger.info("Altering matches table to allow null home_team_id and away_team_id...");
			jdbcTemplate.execute("ALTER TABLE matches ALTER COLUMN home_team_id DROP NOT NULL");
			jdbcTemplate.execute("ALTER TABLE matches ALTER COLUMN away_team_id DROP NOT NULL");

			// Ensure match_number and round_number are nullable
			jdbcTemplate.execute("ALTER TABLE matches ALTER COLUMN match_number DROP NOT NULL");
			jdbcTemplate.execute("ALTER TABLE matches ALTER COLUMN round_number DROP NOT NULL");

			logger.info("Schema fix applied successfully.");
		} catch (Exception e) {
			logger.warn("Schema fix might have failed or was not needed: " + e.getMessage());
		}
	}
}
