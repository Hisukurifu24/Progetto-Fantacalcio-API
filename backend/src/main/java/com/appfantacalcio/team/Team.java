@Entity
@Getter @Setter
public class Team extends BaseEntity {

    private String name;

    @ManyToOne
    private User owner;

    @ManyToOne
    private League league;
}
