package com.appfantacalcio.config;

import com.appfantacalcio.league.League;
import com.appfantacalcio.league.LeagueRepository;
import com.appfantacalcio.team.Team;
import com.appfantacalcio.team.TeamRepository;
import com.appfantacalcio.user.User;
import com.appfantacalcio.user.UserRepository;
import com.appfantacalcio.user.UserRole;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Optional;
import java.util.UUID;

@Component
public class DataSeeder implements CommandLineRunner {

	private static final Logger logger = LoggerFactory.getLogger(DataSeeder.class);

	private final LeagueRepository leagueRepository;
	private final TeamRepository teamRepository;
	private final UserRepository userRepository;

	public DataSeeder(LeagueRepository leagueRepository, TeamRepository teamRepository, UserRepository userRepository) {
		this.leagueRepository = leagueRepository;
		this.teamRepository = teamRepository;
		this.userRepository = userRepository;
	}

	@Override
	@Transactional
	public void run(String... args) throws Exception {
		seedLeagueAndTeams();
	}

	private void seedLeagueAndTeams() {
		String leagueName = "FANTAStico";
		Optional<League> leagueOpt = leagueRepository.findByName(leagueName);
		League league;

		User adminUser = userRepository.findByUsername("admin").orElseGet(() -> {
			User newUser = new User();
			newUser.setUsername("admin");
			newUser.setEmail("admin@example.com");
			newUser.setPassword("password"); // Note: In a real scenario, use PasswordEncoder
			newUser.setRole(UserRole.USER);
			return userRepository.save(newUser);
		});

		if (leagueOpt.isPresent()) {
			league = leagueOpt.get();
			logger.info("League '{}' already exists.", leagueName);
		} else {
			league = new League();
			league.setName(leagueName);
			league.setPublic(true);
			league.setInviteCode(UUID.randomUUID().toString().substring(0, 8));
			league.setMaxBudget(500);
			league.setCreatedBy(adminUser);
			league = leagueRepository.save(league);
			logger.info("Created league '{}'.", leagueName);
		}

		for (int i = 1; i <= 8; i++) {
			String teamName = "Squadra " + i;
			if (teamRepository.findByNameAndLeagueId(teamName, league.getId()).isEmpty()) {
				Team team = new Team();
				team.setName(teamName);
				team.setLeague(league);
				team.setOwner(adminUser);
				team.setCoachName("Coach " + i);
				teamRepository.save(team);
				logger.info("Created team '{}' in league '{}'.", teamName, leagueName);
			} else {
				logger.info("Team '{}' already exists in league '{}'.", teamName, leagueName);
			}
		}
	}
}
