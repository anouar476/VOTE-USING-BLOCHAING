import hashlib
import json
import time
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from urllib.parse import urlparse
import requests
import uuid


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100, block_type='genesis')
    
    def register_node(self, address):
        """
        Add a new node to the list of nodes
        
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        
        :param chain: A blockchain
        :return: True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1
        
        while current_index < len(chain):
            block = chain[current_index]
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1
        
        return True
    
    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        
        :return: True if our chain was replaced, False if not
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
                chain = response.json()['chain']
                
                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        
        return False
    
    def new_block(self, proof, previous_hash=None, block_type='transaction'):
        """
        Create a new Block in the Blockchain
        
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :param block_type: Type of block ('genesis', 'registration', 'vote')
        :return: New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
            'type': block_type
        }
        
        # Reset the current list of transactions
        self.current_transactions = []
        
        self.chain.append(block)
        return block
    
    def register_voter(self, cin_hash, public_key):
        """
        Register a new voter in the blockchain
        
        :param cin_hash: Hash of voter's CIN (National Identity Card)
        :param public_key: Public key of the voter
        :return: The index of the Block that will hold this registration
        """
        registration = {
            'type': 'registration',
            'cin_hash': cin_hash,
            'public_key': public_key,
            'timestamp': time.time(),
            'id': str(uuid.uuid4())
        }
        
        self.current_transactions.append(registration)
        
        # Mine a new registration block
        last_block = self.last_block
        proof = self.proof_of_work(last_block['proof'])
        self.new_block(proof, block_type='registration')
        
        return self.last_block['index']
    
    def new_vote(self, cin_hash, candidate, signature, public_key):
        """
        Creates a new vote to go into the next mined Block
        
        :param cin_hash: Hash of voter's CIN
        :param candidate: Candidate chosen by voter
        :param signature: Signature of the vote
        :param public_key: Public key of the voter
        :return: The index of the Block that will hold this vote
        """
        # First verify this voter is registered and hasn't voted yet
        if not self.is_voter_registered(cin_hash):
            raise ValueError("Voter not registered")
        
        if self.has_voter_voted(cin_hash):
            raise ValueError("Voter has already voted")
        
        # Verify the public key matches the one registered
        registered_key = self.get_voter_public_key(cin_hash)
        if registered_key != public_key:
            raise ValueError("Public key does not match the registered one")
        
        # Verify the signature
        message = f"{cin_hash}{candidate}".encode()
        if not self.verify_signature(message, signature, public_key):
            raise ValueError("Invalid vote signature")
        
        vote = {
            'type': 'vote',
            'cin_hash': cin_hash,
            'candidate': candidate,
            'timestamp': time.time(),
            'signature': signature,
            'public_key': public_key,
            'id': str(uuid.uuid4())
        }
        
        self.current_transactions.append(vote)
        
        return self.last_block['index'] + 1
    
    def is_voter_registered(self, cin_hash):
        """
        Check if a voter is registered in the blockchain
        
        :param cin_hash: Hash of voter's CIN
        :return: True if registered, False otherwise
        """
        for block in self.chain:
            if block['type'] == 'registration':
                for transaction in block['transactions']:
                    if transaction['type'] == 'registration' and transaction['cin_hash'] == cin_hash:
                        return True
        return False
    
    def has_voter_voted(self, cin_hash):
        """
        Check if a voter has already voted
        
        :param cin_hash: Hash of voter's CIN
        :return: True if already voted, False otherwise
        """
        for block in self.chain:
            if block['type'] == 'vote':
                for transaction in block['transactions']:
                    if transaction['type'] == 'vote' and transaction['cin_hash'] == cin_hash:
                        return True
        return False
    
    def get_voter_public_key(self, cin_hash):
        """
        Get the public key of a registered voter
        
        :param cin_hash: Hash of voter's CIN
        :return: Public key of the voter or None if not found
        """
        for block in self.chain:
            if block['type'] == 'registration':
                for transaction in block['transactions']:
                    if transaction['type'] == 'registration' and transaction['cin_hash'] == cin_hash:
                        return transaction['public_key']
        return None
    
    def verify_signature(self, message, signature, public_key):
        """
        Verify a digital signature
        
        :param message: The message that was signed
        :param signature: The signature to verify
        :param public_key: The public key to use for verification
        :return: True if signature is valid, False otherwise
        """
        try:
            key = RSA.import_key(public_key)
            h = SHA256.new(message)
            pkcs1_15.new(key).verify(h, bytes.fromhex(signature))
            return True
        except (ValueError, TypeError):
            return False
    
    @property
    def last_block(self):
        """
        Returns the last Block in the chain
        """
        return self.chain[-1]
    
    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        
        :param block: Block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains 4 leading zeroes
        - p is the previous proof, p' is the new proof
        
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof
        
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


def generate_keys():
    """
    Generate a new pair of private and public keys
    
    :return: private key, public key
    """
    key = RSA.generate(2048)
    private_key = key.export_key().decode('utf-8')
    public_key = key.publickey().export_key().decode('utf-8')
    
    return private_key, public_key


def hash_cin(cin):
    """
    Create a SHA-256 hash of a CIN
    
    :param cin: National Identity Card number
    :return: Hex string of the hash
    """
    return hashlib.sha256(cin.encode()).hexdigest()

def sign_vote(private_key, cin_hash, candidate):
    """
    Sign a vote with the private key
    
    :param private_key: Private key
    :param cin_hash: Hash of voter's CIN
    :param candidate: Candidate chosen by voter
    :return: Signature
    """
    key = RSA.import_key(private_key)
    message = f"{cin_hash}{candidate}".encode()
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    return signature.hex()
