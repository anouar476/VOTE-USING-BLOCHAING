// Main App Component
const { useState, useEffect } = React;

// Global state for the application
const AppContext = React.createContext();

function App() {
    // State for the active tab
    const [activeTab, setActiveTab] = useState('vote');
    
    // State for blockchain data
    const [blockchain, setBlockchain] = useState({ chain: [], length: 0 });
    
    // State for election data
    const [electionData, setElectionData] = useState({
        registeredVoters: 0,
        registeredCandidates: 0,
        votesCast: 0,
        candidates: [],
        results: []
    });
    
    // State for alerts
    const [alert, setAlert] = useState({ show: false, type: '', message: '' });
    
    // State for selected candidate (in vote tab)
    const [selectedCandidate, setSelectedCandidate] = useState(null);
    
    // State for voter data (in vote tab)
    const [voterData, setVoterData] = useState({
        voterId: '',
        privateKey: ''
    });
    
    // State for registration data
    const [registrationData, setRegistrationData] = useState({
        name: '',
        surname: '',
        idNumber: '',
        birthdate: '',
        email: ''
    });

    // Function to show alerts
    const showAlert = (type, message, duration = 5000) => {
        setAlert({ show: true, type, message });
        setTimeout(() => {
            setAlert({ show: false, type: '', message: '' });
        }, duration);
    };

    // Function to fetch blockchain data
    const fetchBlockchain = async () => {
        try {
            const response = await fetch('/chain');
            const data = await response.json();
            setBlockchain({
                chain: data.chain,
                length: data.length
            });
        } catch (error) {
            console.error('Error fetching blockchain:', error);
            showAlert('danger', 'Erreur lors de la récupération de la blockchain');
        }
    };

    // Function to fetch election status
    const fetchElectionStatus = async () => {
        try {
            const response = await fetch('/election/status');
            const data = await response.json();
            setElectionData(prevData => ({
                ...prevData,
                registeredVoters: data.registered_voters,
                registeredCandidates: data.registered_candidates,
                votesCast: data.votes_cast
            }));
        } catch (error) {
            console.error('Error fetching election status:', error);
        }
    };

    // Function to fetch election results
    const fetchElectionResults = async () => {
        try {
            const response = await fetch('/election/results');
            const data = await response.json();
            setElectionData(prevData => ({
                ...prevData,
                results: data.results || []
            }));
        } catch (error) {
            console.error('Error fetching election results:', error);
        }
    };

    // Fetch candidates for voting
    const fetchCandidates = async () => {
        try {
            // In a real scenario, there would be an API for this
            // For now, we'll use mock data
            const mockCandidates = [
                { id: 'candidate1', name: 'Marie Dupont', party: 'Parti Progressiste' },
                { id: 'candidate2', name: 'Jean Martin', party: 'Alliance Nationale' },
                { id: 'candidate3', name: 'Sophie Lefebvre', party: 'Union Démocratique' }
            ];
            setElectionData(prevData => ({
                ...prevData,
                candidates: mockCandidates
            }));
        } catch (error) {
            console.error('Error fetching candidates:', error);
        }
    };

    // Handle vote submission
    const handleVote = async (e) => {
        e.preventDefault();
        
        if (!selectedCandidate) {
            showAlert('warning', 'Veuillez sélectionner un candidat');
            return;
        }
        
        if (!voterData.voterId.trim() || !voterData.privateKey.trim()) {
            showAlert('warning', 'Veuillez entrer votre ID et votre clé privée');
            return;
        }
        
        try {
            // Mock public key generation from private key
            const publicKey = btoa(voterData.privateKey).substring(0, 20);
            
            // Create a simple signature
            const message = `${voterData.voterId}-${selectedCandidate}`;
            const signature = btoa(message + voterData.privateKey).substring(0, 30);
            
            const response = await fetch('/transactions/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    voter_id: voterData.voterId,
                    candidate_id: selectedCandidate,
                    signature: signature,
                    public_key: publicKey
                })
            });
            
            if (response.status === 201) {
                showAlert('success', 'Vote enregistré avec succès!');
                setSelectedCandidate(null);
                setVoterData({ voterId: '', privateKey: '' });
                fetchElectionStatus();
                fetchElectionResults();
            } else if (response.status === 403) {
                showAlert('danger', 'Vous avez déjà voté ou votre identité est invalide');
            } else {
                showAlert('danger', 'Erreur lors de l\'enregistrement du vote');
            }
        } catch (error) {
            console.error('Error submitting vote:', error);
            showAlert('danger', 'Erreur de connexion au serveur');
        }
    };

    // Handle voter registration
    const handleRegistration = async (e) => {
        e.preventDefault();
        
        // Validate fields
        const { name, surname, idNumber, email } = registrationData;
        if (!name || !surname || !idNumber || !email) {
            showAlert('warning', 'Veuillez remplir tous les champs obligatoires');
            return;
        }
        
        // In a real app, we would send this to the server
        // For demo purposes, we'll just generate a voter ID and keys
        const voterId = idNumber + '-' + Math.random().toString(36).substring(2, 10);
        const privateKey = Array.from({ length: 64 }, () => 
            "0123456789abcdef"[Math.floor(Math.random() * 16)]
        ).join('');
        
        // Show success message with generated credentials
        showAlert('success', 'Inscription réussie!');
        
        // Display registration result
        const registrationResult = document.getElementById('registration-result');
        if (registrationResult) {
            document.getElementById('confirmed-name').textContent = name;
            document.getElementById('confirmed-surname').textContent = surname;
            document.getElementById('hashed-voter-id').textContent = voterId;
            document.getElementById('generated-private-key').value = privateKey;
            registrationResult.style.display = 'block';
        }
        
        // Update voter count
        fetchElectionStatus();
    };

    // Mine new block (admin function)
    const mineBlock = async () => {
        try {
            const response = await fetch('/mine');
            if (response.ok) {
                showAlert('success', 'Nouveau bloc miné avec succès!');
                fetchBlockchain();
                fetchElectionStatus();
                fetchElectionResults();
            } else {
                showAlert('danger', 'Erreur lors du minage du bloc');
            }
        } catch (error) {
            console.error('Error mining block:', error);
            showAlert('danger', 'Erreur de connexion au serveur');
        }
    };

    // Load initial data
    useEffect(() => {
        fetchBlockchain();
        fetchElectionStatus();
        fetchElectionResults();
        fetchCandidates();
        
        // Set up polling for real-time updates
        const interval = setInterval(() => {
            fetchElectionStatus();
            fetchElectionResults();
        }, 10000); // Every 10 seconds
        
        return () => clearInterval(interval);
    }, []);

    return (
        <AppContext.Provider value={{ 
            blockchain, 
            electionData, 
            selectedCandidate, 
            setSelectedCandidate,
            voterData,
            setVoterData,
            registrationData,
            setRegistrationData,
            handleVote,
            handleRegistration,
            mineBlock,
            fetchBlockchain,
            fetchElectionResults
        }}>
            <div className="container">
                <Header />
                
                {alert.show && (
                    <Alert type={alert.type} message={alert.message} />
                )}
                
                <div className="card">
                    <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
                    
                    <div className="card-body">
                        <div className="tab-content">
                            {activeTab === 'vote' && <VoteTab />}
                            {activeTab === 'register' && <RegisterTab />}
                            {activeTab === 'results' && <ResultsTab />}
                            {activeTab === 'blockchain' && <BlockchainTab />}
                        </div>
                    </div>
                </div>
            </div>
        </AppContext.Provider>
    );
}

// Render the App
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
