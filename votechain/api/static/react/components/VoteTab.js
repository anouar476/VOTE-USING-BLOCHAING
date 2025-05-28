// VoteTab Component
const { useContext } = React;

function VoteTab() {
    const { 
        electionData, 
        selectedCandidate, 
        setSelectedCandidate, 
        voterData, 
        setVoterData,
        handleVote 
    } = useContext(AppContext);
    
    return (
        <div className="tab-pane fade show active fade-in" role="tabpanel">
            <h4 className="card-title"><i className="fas fa-vote-yea me-2"></i>Voter pour un candidat</h4>
            
            <form onSubmit={handleVote}>
                <div className="mb-3">
                    <label htmlFor="voter-id" className="form-label">ID Votant</label>
                    <input 
                        type="text" 
                        className="form-control" 
                        id="voter-id" 
                        value={voterData.voterId}
                        onChange={(e) => setVoterData({...voterData, voterId: e.target.value})}
                        required 
                    />
                </div>
                <div className="mb-3">
                    <label htmlFor="private-key" className="form-label">Clé Privée</label>
                    <textarea 
                        className="form-control" 
                        id="private-key" 
                        rows="3" 
                        value={voterData.privateKey}
                        onChange={(e) => setVoterData({...voterData, privateKey: e.target.value})}
                        required
                    ></textarea>
                </div>
                <h5>Sélectionnez un candidat</h5>
                <div id="candidates-list" className="row mb-3">
                    {electionData.candidates.map(candidate => (
                        <div key={candidate.id} className="col-md-4 mb-3">
                            <CandidateCard 
                                candidate={candidate}
                                isSelected={selectedCandidate === candidate.id}
                                onClick={() => setSelectedCandidate(candidate.id)}
                            />
                        </div>
                    ))}
                </div>
                <button type="submit" className="btn btn-primary" id="vote-button">
                    <i className="fas fa-paper-plane me-2"></i>
                    Voter
                </button>
            </form>
        </div>
    );
}
