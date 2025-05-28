// CandidateCard Component
function CandidateCard({ candidate, isSelected, onClick }) {
    return (
        <div 
            className={`candidate-card text-center ${isSelected ? 'selected' : ''}`} 
            onClick={onClick}
        >
            <div className="candidate-photo">
                <i className="fas fa-user"></i>
            </div>
            <h5>{candidate.name}</h5>
            <div className="party-tag">
                <i className="fas fa-flag me-1"></i> {candidate.party}
            </div>
            {isSelected && (
                <div className="selected-badge">
                    <i className="fas fa-check-circle text-primary"></i>
                </div>
            )}
        </div>
    );
}
