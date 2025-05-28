// BlockchainBlock Component
function BlockchainBlock({ block, isGenesis }) {
    return (
        <div className={`block ${isGenesis ? 'genesis-block' : ''} scale-in`}>
            <div className="block-header">
                <div>
                    <i className={`fas ${isGenesis ? 'fa-seedling' : 'fa-cube'} me-2`}></i>
                    Bloc #{block.index} {isGenesis && '(Genesis)'}
                </div>
                <div>
                    <i className="far fa-clock me-1"></i>
                    {new Date(block.timestamp * 1000).toLocaleString()}
                </div>
            </div>
            <div className="block-body">
                <div className="row mb-3">
                    <div className="col-md-6">
                        <div className="mb-2">
                            <strong><i className="fas fa-fingerprint me-1"></i> Hash:</strong>
                            <div className="hash-highlight">{block.hash}</div>
                        </div>
                    </div>
                    <div className="col-md-6">
                        <div className="mb-2">
                            <strong><i className="fas fa-link me-1"></i> Hash précédent:</strong>
                            <div className="hash-highlight">{block.previous_hash}</div>
                        </div>
                    </div>
                </div>
                
                <div className="mb-3">
                    <strong><i className="fas fa-check-circle me-1"></i> Preuve:</strong>
                    <span className="proof-highlight ms-2">{block.proof}</span>
                </div>
                
                <div>
                    <strong>
                        <i className="fas fa-exchange-alt me-1"></i> 
                        Transactions ({block.transactions.length})
                    </strong>
                    {block.transactions.length > 0 ? (
                        <div className="mt-2">
                            {block.transactions.map((tx, idx) => (
                                <div key={idx} className="transaction">
                                    <div className="d-flex justify-content-between">
                                        <span><strong>Votant:</strong> {tx.voter_id}</span>
                                        <span className="text-muted">
                                            {new Date(tx.timestamp * 1000).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <div>
                                        <strong>Candidat:</strong> {tx.candidate_id}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-muted mt-2">Aucune transaction dans ce bloc</p>
                    )}
                </div>
            </div>
        </div>
    );
}
