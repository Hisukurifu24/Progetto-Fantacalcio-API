@RestController
@RequestMapping("/api/leagues")
@RequiredArgsConstructor
public class LeagueController {

    private final LeagueService leagueService;

    @PostMapping
    public League create(@RequestBody CreateLeagueRequest req) {
        return leagueService.create(req);
    }

    @GetMapping
    public List<League> myLeagues() {
        return leagueService.findMine();
    }

    @GetMapping("/public")
    public List<League> publicLeagues() {
        return leagueService.findPublic();
    }

    @GetMapping("/{id}")
    public League get(@PathVariable UUID id) {
        return leagueService.get(id);
    }
}
