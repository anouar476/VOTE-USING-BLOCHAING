// ResultsTab Component
const { useContext, useState } = React;

function ResultsTab() {
    const { electionData, fetchElectionResults } = useContext(AppContext);
    const [realtimeUpdates, setRealtimeUpdates] = useState(true);
    
    // Generate mock vote history data
    const generateVoteHistory = () => {
        const mockHistory = [];
        const now = new Date();
        
        for (let i = 0; i < 10; i++) {
            const pastTime = new Date(now.getTime() - i * 5 * 60000);
            const randomCandidate = electionData.candidates[Math.floor(Math.random() * electionData.candidates.length)];
            
            if (randomCandidate) {
                mockHistory.push({
                    time: pastTime,
                    block: Math.floor(Math.random() * 10) + 1,
                    voter: Math.random().toString(36).substring(2, 10),
                    candidate: randomCandidate
                });
            }
        }
        
        return mockHistory;
    };
    
    const voteHistory = generateVoteHistory();
    
    return (
        <div className="tab-pane fade show active fade-in" role="tabpanel">
            <h4 className="card-title"><i className="fas fa-chart-bar me-2"></i>Résultats de l'élection</h4>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <button 
                        id="refresh-results" 
                        className="btn btn-outline-primary"
                        onClick={fetchElectionResults}
                    >
                        <i className="fas fa-sync-alt me-2"></i>Rafraîchir manuellement
                    </button>
                </div>
                <div className="form-check form-switch">
                    <input 
                        className="form-check-input" 
                        type="checkbox" 
                        id="realtime-toggle" 
                        checked={realtimeUpdates}
                        onChange={() => setRealtimeUpdates(!realtimeUpdates)} 
                    />
                    <label className="form-check-label" htmlFor="realtime-toggle">
                        Actualisation en temps réel
                    </label>
                </div>
            </div>
            
            <div className="card mb-3">
                <div className="card-body">
                    <h5 className="card-title"><i className="fas fa-chart-line me-2"></i>Statistiques de la Blockchain</h5>
                    <div className="row text-center">
                        <div className="col-md-3 mb-3">
                            <div className="h2" id="stats-voters">{electionData.registeredVoters}</div>
                            <div>Votants inscrits</div>
                        </div>
                        <div className="col-md-3 mb-3">
                            <div className="h2" id="stats-votes">{electionData.votesCast}</div>
                            <div>Transactions</div>
                        </div>
                        <div className="col-md-3 mb-3">
                            <div className="h2" id="stats-blocks">{electionData.blockchain?.length || 1}</div>
                            <div>Blocs dans la chaîne</div>
                        </div>
                        <div className="col-md-3 mb-3">
                            <div className="h2">PoW</div>
                            <div>Consensus</div>
                        </div>
                    </div>
                    <div className="alert alert-info mt-3">
                        <i className="fas fa-info-circle me-2"></i>La blockchain garantit l'immuabilité et la transparence des votes.
                    </div>
                </div>
            </div>
            
            <div id="results-container" className="mb-3">
                {electionData.results.length > 0 ? (
                    <div className="row">
                        {electionData.results.map((result, index) => {
                            const totalVotes = electionData.results.reduce((sum, r) => sum + r.votes, 0);
                            const percentage = totalVotes > 0 ? Math.round((result.votes / totalVotes) * 100) : 0;
                            
                            return (
                                <div key={index} className="col-md-4 mb-4">
                                    <div className="card h-100">
                                        <div className="card-body text-center">
                                            <div className="candidate-photo mx-auto mb-3">
                                                <i className="fas fa-user"></i>
                                            </div>
                                            <h5 className="card-title">{result.name}</h5>
                                            <div className="party-tag mb-3">
                                                {result.party}
                                            </div>
                                            <div className="vote-count">{result.votes}</div>
                                            <div className="text-muted">votes</div>
                                            <div className="progress">
                                                <div 
                                                    className="progress-bar" 
                                                    role="progressbar" 
                                                    style={{ width: `${percentage}%` }} 
                                                    aria-valuenow={percentage} 
                                                    aria-valuemin="0" 
                                                    aria-valuemax="100"
                                                >
                                                    {percentage}%
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="text-center py-5">
                        <div className="spinner-border text-primary" role="status">
                            <span className="visually-hidden">Chargement...</span>
                        </div>
                        <p className="mt-2">Chargement des résultats...</p>
                    </div>
                )}
            </div>
            
            <div className="card">
                <div className="card-header">
                    <h5 className="mb-0">Historique des votes</h5>
                </div>
                <div className="card-body p-0">
                    <div className="table-responsive">
                        <table className="table table-hover mb-0">
                            <thead>
                                <tr>
                                    <th>Heure</th>
                                    <th>Bloc #</th>
                                    <th>ID Votant (hashé)</th>
                                    <th>Candidat</th>
                                </tr>
                            </thead>
                            <tbody id="votes-history">
                                {voteHistory.map((vote, index) => (
                                    <tr key={index}>
                                        <td>{vote.time.toLocaleTimeString()}</td>
                                        <td>{vote.block}</td>
                                        <td>{vote.voter}</td>
                                        <td>{vote.candidate.name}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
