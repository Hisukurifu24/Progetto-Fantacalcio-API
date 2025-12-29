@Entity
@Getter @Setter
public class League extends BaseEntity {

    private String name;

    private boolean isPublic;

    @Column(unique = true)
    private String inviteCode;

    @ManyToOne(fetch = FetchType.LAZY)
    private User createdBy;
}
