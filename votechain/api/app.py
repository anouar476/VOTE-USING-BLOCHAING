from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
import os
import json
from uuid import uuid4
from typing import Dict, List, Any
import datetime
import atexit

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.blockchain import Blockchain
from utils.crypto import verify_signature, hash_identity

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Définir les chemins de fichiers pour le stockage persistant
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

VOTERS_FILE = os.path.join(DATA_DIR, 'registered_voters.json')
CANDIDATES_FILE = os.path.join(DATA_DIR, 'registered_candidates.json')
VOTES_CAST_FILE = os.path.join(DATA_DIR, 'votes_cast.json')
BLOCKCHAIN_FILE = os.path.join(DATA_DIR, 'blockchain.json')

# Charger les données existantes ou initialiser
def load_data():
    global registered_voters, registered_candidates, votes_cast, blockchain
    
    # Initialiser les valeurs par défaut
    registered_voters = {}
    registered_candidates = {}
    votes_cast = set()
    blockchain = Blockchain()
    
    try:
        # Charger les électeurs enregistrés
        if os.path.exists(VOTERS_FILE) and os.path.getsize(VOTERS_FILE) > 0:
            try:
                with open(VOTERS_FILE, 'r') as f:
                    registered_voters = json.load(f)
                print(f"Chargé {len(registered_voters)} électeurs enregistrés")
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON dans {VOTERS_FILE}, utilisation des valeurs par défaut")
        
        # Charger les candidats enregistrés
        if os.path.exists(CANDIDATES_FILE) and os.path.getsize(CANDIDATES_FILE) > 0:
            try:
                with open(CANDIDATES_FILE, 'r') as f:
                    registered_candidates = json.load(f)
                print(f"Chargé {len(registered_candidates)} candidats")
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON dans {CANDIDATES_FILE}, utilisation des valeurs par défaut")
        
        # Charger les votes déjà exprimés
        if os.path.exists(VOTES_CAST_FILE) and os.path.getsize(VOTES_CAST_FILE) > 0:
            try:
                with open(VOTES_CAST_FILE, 'r') as f:
                    votes_cast = set(json.load(f))
                print(f"Chargé {len(votes_cast)} votes exprimés")
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON dans {VOTES_CAST_FILE}, utilisation des valeurs par défaut")
        
        # Charger la blockchain
        if os.path.exists(BLOCKCHAIN_FILE) and os.path.getsize(BLOCKCHAIN_FILE) > 0:
            try:
                with open(BLOCKCHAIN_FILE, 'r') as f:
                    blockchain_data = json.load(f)
                
                # Vérification de la structure du fichier blockchain
                if isinstance(blockchain_data, dict) and 'chain' in blockchain_data:
                    # Restaurer la blockchain avec le constructeur from_json
                    if hasattr(Blockchain, 'from_json'):
                        blockchain = Blockchain.from_json(blockchain_data)
                        print(f"Blockchain restaurée avec {len(blockchain.chain)} blocs")
                    else:
                        # Reconstruction manuelle
                        try:
                            for block_data in blockchain_data['chain'][1:]:  # Skip genesis block
                                proof = block_data['proof']
                                previous_hash = block_data['previous_hash']
                                transactions = block_data['transactions']
                                blockchain.current_transactions = transactions
                                blockchain.create_block(proof, previous_hash)
                            print(f"Blockchain reconstruite manuellement avec {len(blockchain.chain)} blocs")
                        except (KeyError, TypeError) as e:
                            print(f"Erreur lors de la reconstruction manuelle de la blockchain: {e}")
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON dans {BLOCKCHAIN_FILE}, initialisation d'une nouvelle blockchain")
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        print("Initialisation avec des valeurs par défaut")

# Variable pour suivre si des données ont été modifiées
data_modified = {
    'voters': False,
    'candidates': False,
    'votes': False,
    'blockchain': False
}

# Sauvegarder les données (optimisé pour sauvegarder uniquement ce qui a changé)
def save_data(all_data=False, voters=False, candidates=False, votes=False, save_blockchain=False):
    global data_modified
    
    try:
        # Si all_data est True, tout sauvegarder
        if all_data:
            voters = candidates = votes = save_blockchain = True
        
        # Mettre à jour les drapeaux de modification
        if voters:
            data_modified['voters'] = True
        if candidates:
            data_modified['candidates'] = True
        if votes:
            data_modified['votes'] = True
        if save_blockchain:
            data_modified['blockchain'] = True
        
        # Sauvegarder les électeurs enregistrés si modifiés
        if data_modified['voters']:
            with open(VOTERS_FILE, 'w') as f:
                json.dump(registered_voters, f)
            data_modified['voters'] = False
        
        # Sauvegarder les candidats enregistrés si modifiés
        if data_modified['candidates']:
            with open(CANDIDATES_FILE, 'w') as f:
                json.dump(registered_candidates, f)
            data_modified['candidates'] = False
        
        # Sauvegarder les votes déjà exprimés si modifiés
        if data_modified['votes']:
            with open(VOTES_CAST_FILE, 'w') as f:
                json.dump(list(votes_cast), f)
            data_modified['votes'] = False
        
        # Sauvegarder la blockchain si modifiée
        if data_modified['blockchain']:
            # Vérification de sécurité pour s'assurer que blockchain est valide
            global blockchain
            if isinstance(blockchain, Blockchain) and hasattr(blockchain, 'chain'):
                with open(BLOCKCHAIN_FILE, 'w') as f:
                    # Convertir la blockchain en JSON
                    blockchain_data = {
                        'chain': [block.to_dict() for block in blockchain.chain],
                        'current_transactions': blockchain.current_transactions,
                        'nodes': list(blockchain.nodes)
                    }
                    json.dump(blockchain_data, f)
            else:
                print(f"ERREUR: blockchain n'est pas un objet Blockchain valide: {type(blockchain)}")
            data_modified['blockchain'] = False
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données: {e}")

# S'assurer que les données sont sauvegardées à la fermeture de l'application
def save_data_on_exit():
    try:
        print(f"Sauvegarde des données à {datetime.datetime.now()}")
        save_data(all_data=True)
        print("Sauvegarde terminée avec succès")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde finale: {e}")

# Charger les données au démarrage
load_data()

# Enregistrer la fonction pour sauvegarder les données à la fermeture
atexit.register(save_data_on_exit)


@app.route('/')
def index():
    """Serve the main page of the application."""
    return send_from_directory('static', 'index.html')

@app.route('/react')
def react_app():
    """Serve the React version of the application."""
    return send_from_directory('static/react', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


@app.route('/register', methods=['POST'])
def register_voter():
    """
    Register a new voter with their ID and public key.
    """
    values = request.get_json()
    
    # Validate input
    required = ['voter_id', 'public_key']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400
    
    voter_id = values['voter_id']
    public_key = values['public_key']
    
    # Check if voter is already registered
    if voter_id in registered_voters:
        return jsonify({'message': 'Voter already registered'}), 400
    
    # Register the voter
    registered_voters[voter_id] = public_key
    
    # Save voter registration data
    save_data(voters=True)
    
    response = {
        'message': 'Voter registered successfully',
        'voter_id': voter_id
    }
    
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def get_chain():
    """
    Return the full blockchain and its length.
    """
    response = {
        'chain': [block.to_dict() for block in blockchain.chain],
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
    """
    Execute the proof of work algorithm to mine a new block.
    """
    # We run the proof of work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)
    
    # We must receive a reward for finding the proof
    # The sender is "0" to signify that this node has mined a new coin
    blockchain.add_transaction(
        voter_id="0",  # "0" signifies a system transaction
        candidate_id="0",  # Not a real vote
        signature="0",
        public_key="0"
    )
    
    # Create the new Block by adding it to the chain
    previous_hash = last_block.hash
    block = blockchain.create_block(proof, previous_hash)
    
    # Sauvegarder uniquement la blockchain après avoir miné un bloc
    save_data(save_blockchain=True)
    
    response = {
        'message': "New Block Mined",
        'index': block.index,
        'transactions': block.transactions,
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }
    
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Add a new vote transaction to the blockchain.
    """
    values = request.get_json()
    
    # Check that the required fields are in the POST data
    required = ['voter_id', 'candidate_id', 'signature', 'public_key']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400
    
    # Récupérer l'ID de l'électeur
    voter_id = values['voter_id']
    
    # TEMPORAIRE: Auto-enregistrer l'électeur s'il n'est pas déjà enregistré
    if voter_id not in registered_voters:
        # Récupérer la clé publique (ou utiliser celle fournie dans la requête)
        public_key = values['public_key']
        registered_voters[voter_id] = public_key
        save_data(voters=True)
        print(f"Électeur auto-enregistré: {voter_id}")
    
    # Mode démonstration: désactive la vérification stricte
    # if voter_id not in registered_voters:
    #     return jsonify({'message': 'Voter not registered'}), 403
    
    # Vérifier si le candidat existe
    candidate_id = values['candidate_id']
    
    # TEMPORAIRE: Ajouter le candidat automatiquement s'il n'existe pas (pour la démonstration)
    if candidate_id not in registered_candidates:
        print(f"Ajout automatique du candidat {candidate_id} pour la démonstration")
        registered_candidates[candidate_id] = {
            'name': f"Candidat {candidate_id}",
            'party': "Parti de démonstration"
        }
        save_data(candidates=True)
    
    # Mode démonstration: désactive la vérification stricte
    # if candidate_id not in registered_candidates:
    #    return jsonify({'message': 'Invalid candidate'}), 400
        
    # Check for double voting
    if voter_id in votes_cast:
        return jsonify({'message': 'Voter has already cast a vote'}), 403
    
    # Données du vote
    vote_data = {
        'voter_id': voter_id,
        'candidate_id': candidate_id
    }
    
    # TEMPORAIRE: Désactivation de la vérification de signature pour la démonstration
    # if not verify_signature(vote_data, values['signature'], registered_voters[voter_id]):
    #    return jsonify({'message': 'Invalid signature'}), 403
    print(f"Vérification de signature désactivée pour la démonstration")
    
    # Record that this voter has cast a vote
    votes_cast.add(voter_id)
    
    # Create a new transaction
    index = blockchain.add_transaction(
        voter_id=voter_id,
        candidate_id=candidate_id,
        signature=values['signature'],
        public_key=values['public_key']
    )
    
    # Sauvegarder les votes et les transactions en attente
    save_data(votes=True, save_blockchain=True)
    
    response = {'message': f'Vote will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
    Register a list of new nodes in the form of URLs.
    """
    values = request.get_json()
    
    nodes = values.get('nodes')
    if nodes is None:
        return jsonify({'message': 'Error: Please supply a valid list of nodes'}), 400
    
    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    Resolve conflicts between blockchain nodes using the consensus algorithm.
    """
    replaced = blockchain.resolve_conflicts()
    
    if replaced:
        # Si notre chaîne a été remplacée, sauvegarder uniquement la blockchain
        save_data(save_blockchain=True)
        
        response = {
            'message': 'Our chain was replaced',
            'new_chain': [block.to_dict() for block in blockchain.chain]
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': [block.to_dict() for block in blockchain.chain]
        }
    
    return jsonify(response), 200


# Route supprimée pour éviter le conflit avec /register


@app.route('/candidates/register', methods=['POST'])
def register_candidate():
    """
    Register a new candidate for the election.
    """
    values = request.get_json()
    
    required = ['candidate_id', 'name', 'party']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400
    
    candidate_id = values['candidate_id']
    
    # Check if candidate is already registered
    if candidate_id in registered_candidates:
        return jsonify({'message': 'Candidate already registered'}), 400
    
    # Register the candidate
    registered_candidates[candidate_id] = {
        'name': values['name'],
        'party': values['party']
    }
    
    # Sauvegarder uniquement les données des candidats
    save_data(candidates=True)
    
    return jsonify({'message': 'Candidate registered successfully'}), 201


@app.route('/election/results', methods=['GET'])
def get_results():
    """
    Calculate and return the current election results.
    """
    # Count votes for each candidate
    results = {}
    for block in blockchain.chain:
        for transaction in block.transactions:
            # Skip system transactions
            if transaction['voter_id'] == "0":
                continue
                
            candidate_id = transaction['candidate_id']
            if candidate_id in results:
                results[candidate_id] += 1
            else:
                results[candidate_id] = 1
    
    # Add candidate details to results
    formatted_results = []
    for candidate_id, votes in results.items():
        candidate_info = registered_candidates.get(candidate_id, {'name': 'Unknown', 'party': 'Unknown'})
        formatted_results.append({
            'candidate_id': candidate_id,
            'name': candidate_info['name'],
            'party': candidate_info['party'],
            'votes': votes
        })
    
    # Sort by votes (descending)
    formatted_results.sort(key=lambda x: x['votes'], reverse=True)
    
    return jsonify({
        'results': formatted_results,
        'total_votes': sum(results.values())
    }), 200


@app.route('/election/status', methods=['GET'])
def get_election_status():
    """
    Get the current status of the election.
    """
    return jsonify({
        'registered_voters': len(registered_voters),
        'registered_candidates': len(registered_candidates),
        'votes_cast': len(votes_cast),
        'blockchain_length': len(blockchain.chain)
    }), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    app.run(host='0.0.0.0', port=port, debug=True)
