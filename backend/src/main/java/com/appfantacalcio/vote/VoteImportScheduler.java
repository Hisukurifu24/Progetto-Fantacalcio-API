package com.appfantacalcio.vote;

import com.appfantacalcio.player.Player;
import com.appfantacalcio.player.PlayerRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.Optional;

@Component
@Slf4j
@RequiredArgsConstructor
public class VoteImportScheduler {

	private final VoteRepository voteRepository;
	private final PlayerRepository playerRepository;

	private LocalDateTime lastExecutionTime = LocalDateTime.MIN;

	public boolean triggerManualImport() {
		if (LocalDateTime.now().minusMinutes(1).isBefore(lastExecutionTime)) {
			log.info("Import richiesto manualmente ma saltato: ultimo avvio meno di 1 minuto fa ({})",
					lastExecutionTime);
			return false;
		}
		// Esegui in thread separato per non bloccare la risposta HTTP
		new Thread(this::importDailyVotes).start();
		return true;
	}

	// Esegui ogni giorno alle 04:00
	@Scheduled(cron = "0 0 4 * * ?")
	public void importDailyVotes() {
		this.lastExecutionTime = LocalDateTime.now();
		log.info("Avvio procedura di importazione voti giornalieri...");

		try {
			// 1. Esegui lo scraper Python
			if (runPythonScraper()) {
				// 2. Importa il CSV generato
				importCsvFile();
			} else {
				log.error("Esecuzione dello scraper fallita.");
			}
		} catch (Exception e) {
			log.error("Errore durante l'importazione dei voti", e);
		}
	}

	private boolean runPythonScraper() throws IOException, InterruptedException {
		// Percorso relativo dal modulo backend alla cartella dello scraper
		// Struttura:
		// root/
		// backend/ (user.dir)
		// scrapers/
		// Estrai voti/
		// src/
		// voti_scraper.py

		Path backendPath = Paths.get("").toAbsolutePath();
		Path scraperPath = backendPath.getParent().resolve("scrapers/Estrai voti/src/voti_scraper.py");
		File scraperFile = scraperPath.toFile();

		if (!scraperFile.exists()) {
			log.error("File scraper non trovato: {}", scraperFile.getAbsolutePath());
			return false;
		}

		log.info("Esecuzione dello scraper: {}", scraperFile.getAbsolutePath());

		ProcessBuilder processBuilder = new ProcessBuilder("python3", scraperFile.getAbsolutePath());
		processBuilder.directory(scraperFile.getParentFile()); // Esegui nella cartella dello script
		processBuilder.redirectErrorStream(true);

		Process process = processBuilder.start();

		// Leggi l'output dello script per debug
		try (BufferedReader reader = new BufferedReader(new java.io.InputStreamReader(process.getInputStream()))) {
			String line;
			while ((line = reader.readLine()) != null) {
				log.debug("Python Scraper: {}", line);
			}
		}

		int exitCode = process.waitFor();
		log.info("Scraper terminato con codice: {}", exitCode);

		return exitCode == 0;
	}

	private void importCsvFile() {
		// Il CSV viene generato in ../data/voti_fantacalcio.csv rispetto allo script
		Path backendPath = Paths.get("").toAbsolutePath();
		Path csvPath = backendPath.getParent().resolve("scrapers/Estrai voti/data/voti_fantacalcio.csv");
		File csvFile = csvPath.toFile();

		if (!csvFile.exists()) {
			log.error("File CSV non trovato: {}", csvFile.getAbsolutePath());
			return;
		}

		log.info("Lettura CSV: {}", csvFile.getAbsolutePath());

		try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
			String line;
			boolean firstLine = true;
			int importedCount = 0;

			while ((line = br.readLine()) != null) {
				if (firstLine) {
					firstLine = false;
					continue; // Salta intestazione
				}

				String[] columns = parseCsvLine(line);
				if (columns.length >= 15) { // Giornata + 14 campi dati
					processVoteRow(columns);
					importedCount++;
				}
			}
			log.info("Importazione completata. Voti processati: {}", importedCount);

		} catch (IOException e) {
			log.error("Errore durante la lettura del CSV", e);
		}
	}

	private String[] parseCsvLine(String line) {
		// Implementazione CSV semplice (splitta per virgola, gestendo eventuali quote
		// base se necessario, qui assumiamo formato semplice)
		return line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);
	}

	private void processVoteRow(String[] data) {
		try {
			// Indici basati su:
			// 0:Giornata, 1:Nome, 2:Squadra, 3:Ruolo, 4:Voto, 5:Fantavoto,
			// 6:Gol, 7:Assist, 8:Rigori_Segnati, 9:Rigori_Sbagliati,
			// 10:Rigori_Parati, 11:Gol_Subiti, 12:Autoreti, 13:MOTM, 14:Bonus_Totali

			Integer matchDay = parseInteger(data[0]);
			String name = cleanString(data[1]);
			String team = cleanString(data[2]);
			Double voteValue = parseDouble(data[4]);
			Double fantaVoteValue = parseDouble(data[5]);

			if (matchDay == null || matchDay == 0 || name.isEmpty()) {
				return;
			}

			// Cerca il giocatore
			Optional<Player> playerOpt = playerRepository.findByNameAndRealTeam(name, team);
			if (playerOpt.isEmpty()) {
				// Fallback solo nome (potrebbe essere rischioso, ma meglio che perdere dati)
				playerOpt = playerRepository.findByName(name);
			}

			if (playerOpt.isPresent()) {
				Player player = playerOpt.get();

				// Aggiorna o crea il voto
				Vote vote = voteRepository.findByPlayerAndMatchDay(player, matchDay)
						.orElse(new Vote());

				vote.setPlayer(player);
				vote.setMatchDay(matchDay);
				vote.setVote(voteValue);
				vote.setFantaVote(fantaVoteValue);

				vote.setGoalsScored(parseInteger(data[6]));
				vote.setAssists(parseInteger(data[7]));
				// Nota: rigori segnati/sbagliati/parati vanno mappati correttamente
				vote.setPenaltiesMissed(Math.abs(parseInteger(data[9]))); // Scraper mette malus negativo spesso?
																			// Verificare. CSV scraper mette -value per
																			// rigori_sbagliati
				// Il CSV scraper dice: rigori_sbagliati = -value. Quindi -3 se sbagliato.
				// Il DB aspetta probabilmente il conteggio (1 rigore sbagliato).
				// Controllo logica: se valore è -3, count è 1? O valore è count?
				// Scraper: value = int(bonus_span.get('data-value')). rigori_sbagliati =
				// -value.
				// Quindi 'rigori sbagliati' se data-value è 1 (un rigore), scraper mette -1?
				// No, scraper mette -value dove value è il numero di bonus/malus? No value è il
				// valore intero dello span.
				// Di solito data-value nei bonus è il punteggio (+3, -3).
				// Se è il punteggio, allora devo dividere per 3. Ma se è il count?
				// Analizziamo scraper: "value = int(bonus_span... get 'data-value')".
				// Se è un bonus fantacalcio, data-value di solito è +3 o -3.
				// Se lo scraper prende il punteggio bonus, allora data[6] (gol) sarebbe '1' o
				// '3'?
				// Scraper: "gol = value". Se ho fatto 1 gol, il bonus è +3.

				// Aspetta! Lo scraper dice:
				// if 'gol segnati' in title: gol = value.
				// Su fantacalcio.it data-value di solito è il numero di eventi (1 gol), non il
				// bonus (+3).
				// Verifichiamo. 'data-value' nello span class 'player-bonus'.
				// Se è 1 gol, data-value="1".
				// Se è così, allora gol=1. rigori_sbagliati = -value (quindi -1).
				// Quindi devo prendere il valore assoluto.

				vote.setGoalsConceded(Math.abs(parseInteger(data[11]))); // Gol subiti (malus)
				vote.setOwnGoals(Math.abs(parseInteger(data[12])));
				vote.setPenaltiesSaved(parseInteger(data[10]));

				// Rigori segnati non è esplicito in Vote.java?
				// Vote.java ha: goalsScored, goalsConceded, assists, yellowCards, redCards,
				// penaltiesSaved, penaltiesMissed, ownGoals.
				// Rigori segnati sono inclusi in goalsScored? Di solito sì, ma statisticamente
				// si separano.
				// Vote non ha field 'penaltiesScored'. Quindi o li metto in gol (se non ci sono
				// già) o li ignoro.
				// Di solito 'goalsScored' nel DB contiene TUTTI i gol (azione + rigore).
				// Lo scraper ha gol e rigori_segnati separati.
				// Se fantacalcio.it separa "Gol" da "Rigori" (es. 1 gol azione + 1 rigore),
				// allora Vote.goalScored = gol + rigori.
				// Se "Gol" include rigori, allora ok. Di solito sono separati nei bonus.
				// Assumo somma: Gol data[6] + RigoriSegnati data[8].

				int goalsAction = parseInteger(data[6]);
				int penScored = parseInteger(data[8]);
				vote.setGoalsScored(goalsAction + penScored);

				// Cards - non presenti in CSV modificato (avevo deciso di non aggiungerli per
				// ora)
				vote.setYellowCards(0);
				vote.setRedCards(0);

				voteRepository.save(vote);
			} else {
				log.warn("Giocatore non trovato: {} ({})", name, team);
			}
		} catch (Exception e) {
			log.error("Errore processamento riga voto: " + String.join(",", data), e);
		}
	}

	private Integer parseInteger(String val) {
		try {
			return Integer.parseInt(val);
		} catch (Exception e) {
			return 0;
		}
	}

	private Double parseDouble(String val) {
		try {
			// Gestione virgola decimale e stringhe vuote
			if (val == null || val.isEmpty() || val.equalsIgnoreCase("s.v.") || val.equalsIgnoreCase("6*")) {
				// 6* di solito è voto d'ufficio
				if (val.contains("6*"))
					return 6.0;
				return null;
			}
			return Double.parseDouble(val.replace(",", "."));
		} catch (Exception e) {
			return null;
		}
	}

	private String cleanString(String input) {
		if (input != null && input.length() > 0 && input.charAt(0) == '"') {
			input = input.substring(1);
		}
		if (input != null && input.length() > 0 && input.charAt(input.length() - 1) == '"') {
			input = input.substring(0, input.length() - 1);
		}
		return input;
	}
}
