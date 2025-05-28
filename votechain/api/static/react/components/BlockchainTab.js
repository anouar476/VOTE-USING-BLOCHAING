// BlockchainTab Component
const { useContext } = React;

function BlockchainTab() {
    const { blockchain, fetchBlockchain, mineBlock } = useContext(AppContext);
    
    return (
        <div className="tab-pane fade show active fade-in" role="tabpanel">
            <h4 className="card-title"><i className="fas fa-cubes me-2"></i>Explorer la Blockchain</h4>
            
            <div className="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <button 
                        className="btn btn-primary me-2" 
                        onClick={fetchBlockchain}
                    >
                        <i className="fas fa-sync-alt me-2"></i>Rafraîchir la blockchain
                    </button>
                    <button 
                        className="btn btn-outline-primary" 
                        onClick={mineBlock}
                    >
                        <i className="fas fa-hammer me-2"></i>Miner un bloc
                    </button>
                </div>
                <div>
                    <span className="badge bg-primary">
                        <i className="fas fa-cube me-1"></i>
                        Nombre de blocs: <span id="blockchain-length">{blockchain.chain?.length || 0}</span>
                    </span>
                </div>
            </div>
            
            <div className="blockchain-visualization">
                {blockchain.chain && blockchain.chain.map((block, index) => (
                    <BlockchainBlock 
                        key={index}
                        block={block} 
                        isGenesis={index === 0}
                    />
                ))}
                
                {(!blockchain.chain || blockchain.chain.length === 0) && (
                    <div className="text-center py-5">
                        <div className="spinner-border text-primary" role="status">
                            <span className="visually-hidden">Chargement...</span>
                        </div>
                        <p className="mt-2">Chargement de la blockchain...</p>
                    </div>
                )}
            </div>
        </div>
    );
}
