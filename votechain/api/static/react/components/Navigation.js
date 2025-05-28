// Navigation Component
function Navigation({ activeTab, setActiveTab }) {
    return (
        <div className="card-header">
            <ul className="nav nav-tabs card-header-tabs" role="tablist">
                <li className="nav-item" role="presentation">
                    <button 
                        className={`nav-link ${activeTab === 'vote' ? 'active' : ''}`}
                        onClick={() => setActiveTab('vote')}
                    >
                        <i className="fas fa-vote-yea me-2"></i>Voter
                    </button>
                </li>
                <li className="nav-item" role="presentation">
                    <button 
                        className={`nav-link ${activeTab === 'register' ? 'active' : ''}`}
                        onClick={() => setActiveTab('register')}
                    >
                        <i className="fas fa-user-plus me-2"></i>S'inscrire
                    </button>
                </li>
                <li className="nav-item" role="presentation">
                    <button 
                        className={`nav-link ${activeTab === 'results' ? 'active' : ''}`}
                        onClick={() => setActiveTab('results')}
                    >
                        <i className="fas fa-chart-bar me-2"></i>Résultats
                    </button>
                </li>
                <li className="nav-item" role="presentation">
                    <button 
                        className={`nav-link ${activeTab === 'blockchain' ? 'active' : ''}`}
                        onClick={() => setActiveTab('blockchain')}
                    >
                        <i className="fas fa-cubes me-2"></i>Blockchain
                    </button>
                </li>
            </ul>
        </div>
    );
}
