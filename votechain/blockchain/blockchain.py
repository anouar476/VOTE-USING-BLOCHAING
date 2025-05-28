import hashlib
import json
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import requests


class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Dict],
                 previous_hash: str, proof: int = 0) -> None:
        """
        Initialize a new Block in the VoteChain.
        
        Args:
            index: Unique index of the block
            timestamp: Time of block creation
            transactions: List of vote transactions
            previous_hash: Hash of the previous block
            proof: Proof of work value
        """
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.proof = proof
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "proof": self.proof
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "proof": self.proof,
            "hash": self.hash
        }


class Blockchain:
    def __init__(self) -> None:
        """Initialize a new Blockchain for electronic voting."""
        self.chain: List[Block] = []
        self.current_transactions: List[Dict] = []
        self.nodes: set = set()
        
        # Create the genesis block
        self.create_block(proof=1, previous_hash="0")
    
    def create_block(self, proof: int, previous_hash: Optional[str] = None) -> Block:
        """
        Create a new Block in the Blockchain.
        
        Args:
            proof: The proof of work value
            previous_hash: Hash of previous Block (optional)
            
        Returns:
            The new Block
        """
        if not previous_hash and self.chain:
            previous_hash = self.chain[-1].hash
            
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=self.current_transactions,
            previous_hash=previous_hash,
            proof=proof
        )
        
        # Reset the current list of transactions
        self.current_transactions = []
        
        self.chain.append(block)
        return block
    
    def add_transaction(self, voter_id: str, candidate_id: str, 
                        signature: str, public_key: str) -> int:
        """
        Add a new vote transaction to the list of transactions.
        
        Args:
            voter_id: ID of the voter (anonymized)
            candidate_id: ID of the candidate being voted for
            signature: Digital signature of the vote
            public_key: Voter's public key
            
        Returns:
            The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'voter_id': voter_id,
            'candidate_id': candidate_id,
            'signature': signature,
            'public_key': public_key,
            'timestamp': time.time()
        })
        
        return self.last_block.index + 1
    
    def proof_of_work(self, last_proof: int) -> int:
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains 4 leading zeroes, where p is the previous p'
        - p is the previous proof, and p' is the new proof
        
        Args:
            last_proof: Previous proof
            
        Returns:
            New proof that solves the algorithm
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
            
        return proof
    
    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validate the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        
        Args:
            last_proof: Previous Proof
            proof: Current Proof
            
        Returns:
            True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes.
        
        Args:
            address: URL of node. e.g. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def valid_chain(self, chain: List[Block]) -> bool:
        """
        Determine if a given blockchain is valid.
        
        Args:
            chain: A blockchain
            
        Returns:
            True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1
        
        while current_index < len(chain):
            block = chain[current_index]
            
            # Check that the hash of the block is correct
            if block.previous_hash != last_block.hash:
                return False
                
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block.proof, block.proof):
                return False
                
            last_block = block
            current_index += 1
            
        return True
    
    def resolve_conflicts(self) -> bool:
        """
        Consensus Algorithm: resolves conflicts by replacing our chain with
        the longest one in the network.
        
        Returns:
            True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None
        
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            
            if response.status_code == 200:
                length = response.json()['length']
                chain_data = response.json()['chain']
                
                # Convert the JSON chain data back to Block objects
                chain = []
                for block_data in chain_data:
                    block = Block(
                        index=block_data['index'],
                        timestamp=block_data['timestamp'],
                        transactions=block_data['transactions'],
                        previous_hash=block_data['previous_hash'],
                        proof=block_data['proof']
                    )
                    chain.append(block)
                
                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
            
        return False
    
    @property
    def last_block(self) -> Block:
        """Returns the last Block in the chain."""
        return self.chain[-1]
        
    @classmethod
    def from_json(cls, data: Dict) -> 'Blockchain':
        """
        Reconstruit une instance de Blockchain à partir de données JSON sauvegardées.
        
        Args:
            data: Dictionnaire contenant les données de la blockchain
            
        Returns:
            Une nouvelle instance de Blockchain avec les données restaurées
        """
        blockchain = cls()  # Crée une nouvelle instance avec un bloc genesis
        blockchain.chain = []  # Efface le bloc genesis par défaut
        
        # Reconstruire la chaîne de blocs
        for block_data in data['chain']:
            block = Block(
                index=block_data['index'],
                timestamp=block_data['timestamp'],
                transactions=block_data['transactions'],
                previous_hash=block_data['previous_hash'],
                proof=block_data['proof']
            )
            # Assurez-vous que le hash est correctement défini
            block.hash = block_data.get('hash', block.calculate_hash())
            blockchain.chain.append(block)
        
        # Restaurer les transactions en cours
        blockchain.current_transactions = data.get('current_transactions', [])
        
        # Restaurer les nœuds du réseau
        blockchain.nodes = set(data.get('nodes', []))
        
        return blockchain
