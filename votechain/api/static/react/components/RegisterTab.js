// RegisterTab Component
const { useContext } = React;

function RegisterTab() {
    const { registrationData, setRegistrationData, handleRegistration } = useContext(AppContext);
    
    const handleChange = (e) => {
        const { id, value } = e.target;
        let field = id.replace('voter-', '');
        if (field === 'surname') field = 'surname';
        else if (field === 'name') field = 'name';
        else if (field === 'id-number') field = 'idNumber';
        else if (field === 'birthdate') field = 'birthdate';
        else if (field === 'email') field = 'email';
        
        setRegistrationData({
            ...registrationData,
            [field]: value
        });
    };
    
    return (
        <div className="tab-pane fade show active fade-in" role="tabpanel">
            <h4 className="card-title"><i className="fas fa-user-plus me-2"></i>S'inscrire comme votant</h4>
            
            <div className="id-card mb-4">
                <div className="id-card-header">
                    <h5><i className="fas fa-id-card me-2"></i>Carte d'Identité Électronique</h5>
                    <div className="id-photo">
                        <i className="fas fa-user"></i>
                    </div>
                </div>
                <p className="mb-1">Utilisez votre identité électronique pour participer au vote en toute sécurité.</p>
            </div>
            
            <form id="register-form" onSubmit={handleRegistration}>
                <div className="row">
                    <div className="col-md-6 mb-3">
                        <label htmlFor="voter-name" className="form-label">Nom</label>
                        <input 
                            type="text" 
                            className="form-control" 
                            id="voter-name" 
                            value={registrationData.name}
                            onChange={handleChange}
                            required 
                        />
                    </div>
                    <div className="col-md-6 mb-3">
                        <label htmlFor="voter-surname" className="form-label">Prénom</label>
                        <input 
                            type="text" 
                            className="form-control" 
                            id="voter-surname" 
                            value={registrationData.surname}
                            onChange={handleChange}
                            required 
                        />
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-6 mb-3">
                        <label htmlFor="voter-id-number" className="form-label">Numéro de Carte d'Identité</label>
                        <input 
                            type="text" 
                            className="form-control" 
                            id="voter-id-number" 
                            value={registrationData.idNumber}
                            onChange={handleChange}
                            required 
                        />
                    </div>
                    <div className="col-md-6 mb-3">
                        <label htmlFor="voter-birthdate" className="form-label">Date de Naissance</label>
                        <input 
                            type="date" 
                            className="form-control" 
                            id="voter-birthdate" 
                            value={registrationData.birthdate}
                            onChange={handleChange}
                            required 
                        />
                    </div>
                </div>
                <div className="mb-3">
                    <label htmlFor="voter-email" className="form-label">Email</label>
                    <input 
                        type="email" 
                        className="form-control" 
                        id="voter-email" 
                        value={registrationData.email}
                        onChange={handleChange}
                        required 
                    />
                    <div className="form-text">Un code de vérification sera envoyé à cette adresse.</div>
                </div>
                <button type="submit" className="btn btn-primary" id="register-button">
                    <i className="fas fa-user-check me-2"></i>Vérifier et s'inscrire
                </button>
            </form>
            
            {/* Registration Result */}
            <div className="mt-4" id="registration-result" style={{ display: 'none' }}>
                <div className="alert alert-info">
                    <h5><i className="fas fa-check-circle me-2"></i>Identité vérifiée - Informations d'inscription</h5>
                    <p><strong>Nom:</strong> <span id="confirmed-name"></span></p>
                    <p><strong>Prénom:</strong> <span id="confirmed-surname"></span></p>
                    <p><strong>ID Votant (Hashé):</strong> <span id="hashed-voter-id"></span></p>
                    <div className="mb-3">
                        <label htmlFor="generated-private-key" className="form-label"><strong>Clé Privée:</strong></label>
                        <textarea className="form-control" id="generated-private-key" rows="5" readOnly></textarea>
                    </div>
                    <div className="d-grid gap-2">
                        <button className="btn btn-outline-primary" type="button" id="download-credentials">
                            <i className="fas fa-download me-2"></i>Télécharger mes informations d'identification
                        </button>
                    </div>
                    <div className="alert alert-warning mt-3">
                        <i className="fas fa-exclamation-triangle me-2"></i>
                        <strong>IMPORTANT:</strong> Sauvegardez votre clé privée en lieu sûr. Elle sera nécessaire pour voter.
                    </div>
                </div>
            </div>
        </div>
    );
}
