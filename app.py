from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
import json
import os
import time
from uuid import uuid4
from blockchain import Blockchain, generate_keys, sign_vote, hash_cin

# Instantiate the Node
app = Flask(__name__)
# Use a fixed secret key for development to maintain sessions between restarts
app.secret_key = 'development_secret_key_for_blockchain_app'

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# In a production environment, this would be a secure database
# For demonstration purposes, we'll keep a cache of registered voters to avoid
# scanning the blockchain for every operation
voter_cache = {}  # {cin_hash: {'cin': cin, 'has_registered': bool, 'has_voted': bool}}

# Store candidates
candidates = ["Candidate A", "Candidate B", "Candidate C"]


@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new voter"""
    if request.method == 'POST':
        cin = request.form.get('cin')
        
        if not cin or len(cin) < 4:
            flash('Veuillez entrer un numéro CIN valide', 'danger')
            return redirect(url_for('register'))
        
        # Hash the CIN for privacy
        cin_hash = hash_cin(cin)
        
        # Check if voter is already in cache
        if cin_hash in voter_cache and voter_cache[cin_hash]['has_registered']:
            flash('Ce numéro CIN est déjà enregistré!', 'danger')
            return redirect(url_for('register'))
        
        # Check in blockchain if not in cache
        if blockchain.is_voter_registered(cin_hash):
            voter_cache[cin_hash] = {
                'cin': cin,
                'has_registered': True,
                'has_voted': blockchain.has_voter_voted(cin_hash)
            }
            flash('Ce numéro CIN est déjà enregistré!', 'danger')
            return redirect(url_for('register'))
        
        # Generate a new key pair for the voter
        private_key, public_key = generate_keys()
        
        # Ne plus enregistrer dans la blockchain, seulement dans le cache
        # Stocker directement dans le cache
        voter_cache[cin_hash] = {
            'cin': cin,
            'public_key': public_key, # Stocker la clé publique ici
            'has_registered': True,
            'has_voted': False
        }
        
        # Store keys in session
        session['cin'] = cin
        session['cin_hash'] = cin_hash
        session['private_key'] = private_key
        session['public_key'] = public_key
        
        flash('Inscription réussie! Vos clés cryptographiques ont été générées.', 'success')
        return redirect(url_for('vote'))
    
    return render_template('register.html')


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    """Cast a vote"""
    if 'cin' not in session or 'cin_hash' not in session:
        flash('Veuillez vous inscrire d\'abord!', 'warning')
        return redirect(url_for('register'))
    
    cin = session['cin']
    cin_hash = session['cin_hash']
    
    # Vérifier uniquement dans le cache, plus dans la blockchain
    if cin_hash not in voter_cache:
        flash('Votre inscription n\'est pas valide. Veuillez vous inscrire à nouveau.', 'warning')
        return redirect(url_for('register'))
    
    # Vérifier si l'électeur a déjà voté (uniquement dans le cache)
    if voter_cache[cin_hash]['has_voted']:
        flash('Vous avez déjà voté!', 'warning')
        return redirect(url_for('results'))
    
    if request.method == 'POST':
        candidate = request.form.get('candidate')
        
        if candidate not in candidates:
            flash('Candidat invalide!', 'danger')
            return redirect(url_for('vote'))
        
        try:
            # Vérifier que la clé publique dans la session correspond à celle du cache
            if session['public_key'] != voter_cache[cin_hash]['public_key']:
                flash('Erreur de validation: Clé publique non valide.', 'danger')
                return redirect(url_for('vote'))
                
            # Sign the vote
            signature = sign_vote(session['private_key'], cin_hash, candidate)
            
            # Créer la transaction de vote
            vote = {
                'type': 'vote',
                'cin_hash': cin_hash,
                'candidate': candidate,
                'timestamp': time.time(),
                'signature': signature,
                'public_key': session['public_key'],
                'id': str(uuid4())
            }
            
            # Vider les transactions actuelles pour s'assurer qu'il n'y a qu'un vote par bloc
            blockchain.current_transactions = []
            
            # Ajouter uniquement ce vote comme transaction
            blockchain.current_transactions.append(vote)
            
            # Mine a new block to include the vote
            last_block = blockchain.last_block
            last_proof = last_block['proof']
            proof = blockchain.proof_of_work(last_proof)
            
            # Forge the new block with only this vote
            blockchain.new_block(proof, block_type='vote')
            
            # Update cache
            voter_cache[cin_hash]['has_voted'] = True
            
            flash('Votre vote a été enregistré dans la blockchain!', 'success')
            return redirect(url_for('results'))
        except ValueError as e:
            flash(f'Erreur: {str(e)}', 'danger')
            return redirect(url_for('vote'))
    
    return render_template('vote.html', candidates=candidates)


@app.route('/results')
def results():
    """View election results"""
    # Count votes for each candidate
    vote_counts = {candidate: 0 for candidate in candidates}
    
    # Count votes from all blocks in the chain
    for block in blockchain.chain:
        if block['type'] == 'vote':
            for transaction in block['transactions']:
                if transaction['type'] == 'vote' and transaction['candidate'] in candidates:
                    vote_counts[transaction['candidate']] += 1
    
    total_votes = sum(vote_counts.values())
    
    return render_template('results.html', 
                           vote_counts=vote_counts, 
                           total_votes=total_votes,
                           candidates=candidates)


@app.route('/blockchain')
def view_blockchain():
    """View the entire blockchain"""
    
    # Get some statistics for the dashboard
    total_blocks = len(blockchain.chain)
    registration_blocks = sum(1 for block in blockchain.chain if block['type'] == 'registration')
    vote_blocks = sum(1 for block in blockchain.chain if block['type'] == 'vote')
    
    registered_voters = 0
    for block in blockchain.chain:
        if block['type'] == 'registration':
            registered_voters += sum(1 for tx in block['transactions'] if tx['type'] == 'registration')
    
    votes_cast = 0
    for block in blockchain.chain:
        if block['type'] == 'vote':
            votes_cast += sum(1 for tx in block['transactions'] if tx['type'] == 'vote')
    
    return render_template('blockchain.html', 
                          chain=blockchain.chain,
                          total_blocks=total_blocks,
                          registration_blocks=registration_blocks,
                          vote_blocks=vote_blocks,
                          registered_voters=registered_voters,
                          votes_cast=votes_cast)


# API Endpoints for the blockchain network

@app.route('/chain', methods=['GET'])
def full_chain():
    """Return the full blockchain"""
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """Register a list of new nodes"""
    values = request.get_json()
    
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    
    for node in nodes:
        blockchain.register_node(node)
    
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """Resolve conflicts using consensus algorithm"""
    replaced = blockchain.resolve_conflicts()
    
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
