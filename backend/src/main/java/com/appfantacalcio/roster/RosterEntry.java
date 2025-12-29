@Entity
@Getter @Setter
public class RosterEntry extends BaseEntity {

    @ManyToOne
    private Team team;

    @ManyToOne
    private Player player;

    private int acquiredFor;
}
