@Entity
@Getter @Setter
public class Player {

    @Id
    private UUID id; // same id scraper-side

    private String name;
    private String role;
    private String realTeam;

    private int quotazioneClassico;
    private int quotazioneMantra;
}
