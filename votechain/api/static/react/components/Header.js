// Header Component
const { useContext } = React;

function Header() {
    const { electionData } = useContext(AppContext);
    
    return (
        <div className="header fade-in">
            <h1><i className="fas fa-link me-2"></i>VoteChain</h1>
            <p className="lead">Système de Vote Électronique Sécurisé avec la Blockchain</p>
            <div className="blockchain-info">
                <div className="row text-center mt-3">
                    <div className="col-md-4">
                        <div className="stat-item">
                            <i className="fas fa-users me-2"></i>
                            <span id="voter-count">{electionData.registeredVoters}</span> Votants
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="stat-item">
                            <i className="fas fa-vote-yea me-2"></i>
                            <span id="vote-count">{electionData.votesCast}</span> Votes
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="stat-item">
                            <i className="fas fa-cubes me-2"></i>
                            <span id="block-count">{electionData.blockchain?.length || 1}</span> Blocs
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
