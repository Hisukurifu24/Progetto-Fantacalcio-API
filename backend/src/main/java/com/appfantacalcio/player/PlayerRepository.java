package com.appfantacalcio.player;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface PlayerRepository extends JpaRepository<Player, UUID> {

	Optional<Player> findByName(String name);

	Optional<Player> findByNameAndRealTeam(String name, String realTeam);

	@Query("SELECT p FROM Player p WHERE " +
			"(:role IS NULL OR p.role = :role) AND " +
			"(:search IS NULL OR LOWER(CAST(p.name AS string)) LIKE LOWER(CONCAT('%', CAST(:search AS string), '%'))) AND "
			+
			"(:team IS NULL OR p.realTeam = :team) AND " +
			"(:minQuotazione IS NULL OR p.quotazioneAttualeClassico >= :minQuotazione) AND " +
			"(:maxQuotazione IS NULL OR p.quotazioneAttualeClassico <= :maxQuotazione) AND " +
			"(:minFvm IS NULL OR p.fvmClassico >= :minFvm) AND " +
			"(:maxFvm IS NULL OR p.fvmClassico <= :maxFvm)")
	List<Player> findByFilters(
			@Param("role") String role,
			@Param("search") String search,
			@Param("team") String team,
			@Param("minQuotazione") Integer minQuotazione,
			@Param("maxQuotazione") Integer maxQuotazione,
			@Param("minFvm") Integer minFvm,
			@Param("maxFvm") Integer maxFvm);
}
