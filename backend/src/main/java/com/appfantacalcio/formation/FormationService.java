package com.appfantacalcio.formation;

import com.appfantacalcio.formation.dto.FormationDTO;
import com.appfantacalcio.formation.dto.FormationResponseDTO;
import com.appfantacalcio.player.Player;
import com.appfantacalcio.player.PlayerRepository;
import com.appfantacalcio.player.dto.PlayerResponse;
import com.appfantacalcio.team.Team;
import com.appfantacalcio.team.TeamRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FormationService {

	private final FormationRepository formationRepository;
	private final TeamRepository teamRepository;
	private final PlayerRepository playerRepository;

	@Transactional
	public FormationResponseDTO saveFormation(FormationDTO dto) {
		Team team = teamRepository.findById(dto.getTeamId())
				.orElseThrow(() -> new RuntimeException("Team not found"));

		Formation formation = formationRepository.findByTeamAndMatchDay(team, dto.getMatchDay())
				.orElse(new Formation());

		formation.setTeam(team);
		formation.setMatchDay(dto.getMatchDay());
		formation.setModule(dto.getModule());

		if (dto.getGoalkeeperId() != null) {
			formation.setGoalkeeper(playerRepository.findById(dto.getGoalkeeperId()).orElse(null));
		}

		formation.setDefenders(getPlayers(dto.getDefenderIds()));
		formation.setMidfielders(getPlayers(dto.getMidfielderIds()));
		formation.setForwards(getPlayers(dto.getForwardIds()));
		formation.setBench(getPlayers(dto.getBenchIds()));

		Formation savedFormation = formationRepository.save(formation);
		return toFormationResponseDTO(savedFormation);
	}

	private FormationResponseDTO toFormationResponseDTO(Formation formation) {
		FormationResponseDTO response = new FormationResponseDTO();
		response.setModule(formation.getModule());
		response.setMatchDay(formation.getMatchDay());
		String teamName = formation.getTeam().getName();
		response.setGoalkeeper(toPlayerResponse(formation.getGoalkeeper(), teamName));
		response.setDefenders(
				formation.getDefenders().stream().map(p -> toPlayerResponse(p, teamName)).collect(Collectors.toList()));
		response.setMidfielders(formation.getMidfielders().stream().map(p -> toPlayerResponse(p, teamName))
				.collect(Collectors.toList()));
		response.setForwards(
				formation.getForwards().stream().map(p -> toPlayerResponse(p, teamName)).collect(Collectors.toList()));
		response.setBench(
				formation.getBench().stream().map(p -> toPlayerResponse(p, teamName)).collect(Collectors.toList()));
		return response;
	}

	private List<Player> getPlayers(List<UUID> ids) {
		if (ids == null || ids.isEmpty())
			return List.of();
		List<UUID> nonNullIds = ids.stream().filter(Objects::nonNull).collect(Collectors.toList());
		if (nonNullIds.isEmpty())
			return List.of();

		java.util.Map<UUID, Player> playerMap = playerRepository.findAllById(nonNullIds).stream()
				.collect(Collectors.toMap(Player::getId, p -> p));

		return nonNullIds.stream()
				.map(playerMap::get)
				.filter(Objects::nonNull)
				.collect(Collectors.toList());
	}

	@Transactional(readOnly = true)
	public FormationResponseDTO getFormation(UUID teamId, Integer matchDay) {
		Team team = teamRepository.findById(teamId)
				.orElseThrow(() -> new RuntimeException("Team not found"));

		Formation formation = formationRepository.findByTeamAndMatchDay(team, matchDay)
				.orElseThrow(() -> new RuntimeException("Formation not found"));

		return toFormationResponseDTO(formation);
	}

	private PlayerResponse toPlayerResponse(Player player, String teamName) {
		if (player == null)
			return null;
		return new PlayerResponse(
				player.getId(),
				player.getName(),
				player.getRole(),
				player.getRealTeam(),
				player.getQuotazioneInizialeClassico(),
				player.getQuotazioneAttualeClassico(),
				player.getQuotazioneInizialeMantra(),
				player.getQuotazioneAttualeMantra(),
				player.getFvmClassico(),
				player.getFvmMantra(),
				teamName);
	}
}
