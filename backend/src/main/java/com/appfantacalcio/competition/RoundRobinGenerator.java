package com.appfantacalcio.competition;

import java.util.ArrayList;
import java.util.List;

import com.appfantacalcio.match.Match;
import com.appfantacalcio.team.Team;

public class RoundRobinGenerator {

	public static List<Match> generate(
			List<Team> teams,
			Competition competition) {
		List<Match> result = new ArrayList<>();

		List<Team> list = new ArrayList<>(teams);
		if (list.size() % 2 != 0)
			list.add(null); // bye

		int n = list.size();
		int days = n - 1;
		int matchDay = competition.getStartDay();

		for (int day = 0; day < days; day++) {
			for (int i = 0; i < n / 2; i++) {
				Team home = list.get(i);
				Team away = list.get(n - 1 - i);

				if (home != null && away != null) {
					Match m = new Match();
					m.setCompetition(competition);
					m.setHomeTeam(home);
					m.setAwayTeam(away);
					m.setMatchDay(matchDay);
					result.add(m);
				}
			}

			// rotate (keep first fixed)
			Team fixed = list.remove(1);
			list.add(fixed);
			matchDay++;
		}

		return result;
	}
}
