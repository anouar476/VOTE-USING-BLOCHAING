import sys
import os
import unittest
import json
from time import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.blockchain import Blockchain, Block
from utils.crypto import generate_key_pair, sign_vote, verify_signature, hash_identity


class TestBlockchain(unittest.TestCase):
    def setUp(self):
        """Set up a new blockchain for each test."""
        self.blockchain = Blockchain()
        self.private_key, self.public_key = generate_key_pair()
    
    def test_create_block(self):
        """Test block creation functionality."""
        # Get the initial chain length
        initial_length = len(self.blockchain.chain)
        
        # Add a new block
        proof = self.blockchain.proof_of_work(self.blockchain.last_block.proof)
        new_block = self.blockchain.create_block(proof)
        
        # Verify the chain has increased by one
        self.assertEqual(len(self.blockchain.chain), initial_length + 1)
        
        # Verify the new block is the last one in the chain
        self.assertEqual(self.blockchain.chain[-1], new_block)
        
        # Verify the block's properties
        self.assertEqual(new_block.index, initial_length + 1)
        self.assertEqual(new_block.previous_hash, self.blockchain.chain[-2].hash)
        self.assertEqual(new_block.proof, proof)
    
    def test_add_transaction(self):
        """Test adding a vote transaction to the blockchain."""
        # Create a vote transaction
        voter_id = hash_identity("test_voter")
        candidate_id = "test_candidate"
        
        # Create vote data and sign it
        vote_data = {
            'voter_id': voter_id,
            'candidate_id': candidate_id
        }
        signature = sign_vote(vote_data, self.private_key)
        
        # Add the transaction
        index = self.blockchain.add_transaction(
            voter_id=voter_id,
            candidate_id=candidate_id,
            signature=signature,
            public_key=self.public_key
        )
        
        # Verify the transaction is in the current_transactions list
        self.assertEqual(len(self.blockchain.current_transactions), 1)
        self.assertEqual(self.blockchain.current_transactions[0]['voter_id'], voter_id)
        self.assertEqual(self.blockchain.current_transactions[0]['candidate_id'], candidate_id)
        self.assertEqual(self.blockchain.current_transactions[0]['signature'], signature)
        self.assertEqual(self.blockchain.current_transactions[0]['public_key'], self.public_key)
        
        # Verify the transaction index is correct
        self.assertEqual(index, len(self.blockchain.chain) + 1)
    
    def test_proof_of_work(self):
        """Test the proof of work algorithm."""
        last_proof = self.blockchain.last_block.proof
        proof = self.blockchain.proof_of_work(last_proof)
        
        # Verify the proof is valid
        self.assertTrue(self.blockchain.valid_proof(last_proof, proof))
        
        # Verify an invalid proof is rejected
        self.assertFalse(self.blockchain.valid_proof(last_proof, proof + 1))
    
    def test_valid_chain(self):
        """Test chain validation."""
        # The initial chain should be valid
        self.assertTrue(self.blockchain.valid_chain(self.blockchain.chain))
        
        # Create a tampered chain
        tampered_chain = self.blockchain.chain.copy()
        tampered_block = tampered_chain[1]  # Skip genesis block
        
        # Tamper with a transaction
        if tampered_block.transactions:
            tampered_block.transactions[0]['candidate_id'] = "tampered_candidate"
        else:
            # Add a fake transaction if none exists
            tampered_block.transactions.append({
                'voter_id': "fake_voter",
                'candidate_id': "fake_candidate",
                'signature': "fake_signature",
                'public_key': "fake_public_key",
                'timestamp': time()
            })
        
        # Recalculate the hash
        tampered_block.hash = tampered_block.calculate_hash()
        
        # The tampered chain should be invalid
        self.assertFalse(self.blockchain.valid_chain(tampered_chain))
    
    def test_block_hash(self):
        """Test that block hash calculation works correctly."""
        block = self.blockchain.last_block
        original_hash = block.hash
        
        # Change a property and verify the hash changes
        block.timestamp = time()
        new_hash = block.calculate_hash()
        
        self.assertNotEqual(original_hash, new_hash)


class TestCryptography(unittest.TestCase):
    def test_key_generation(self):
        """Test key pair generation."""
        private_key, public_key = generate_key_pair()
        
        # Verify keys are not empty
        self.assertTrue(private_key)
        self.assertTrue(public_key)
        
        # Verify keys are different
        self.assertNotEqual(private_key, public_key)
    
    def test_signature_verification(self):
        """Test signature creation and verification."""
        # Generate a key pair
        private_key, public_key = generate_key_pair()
        
        # Create vote data
        vote_data = {
            'voter_id': 'test_voter',
            'candidate_id': 'test_candidate'
        }
        
        # Sign the vote
        signature = sign_vote(vote_data, private_key)
        
        # Verify the signature
        self.assertTrue(verify_signature(vote_data, signature, public_key))
        
        # Verify tampering is detected
        tampered_data = vote_data.copy()
        tampered_data['candidate_id'] = 'tampered_candidate'
        self.assertFalse(verify_signature(tampered_data, signature, public_key))
    
    def test_identity_hashing(self):
        """Test identity hashing for voter anonymity."""
        identity = "voter@example.com"
        
        # Hash the identity
        hashed_identity = hash_identity(identity)
        
        # Verify the hash is not the original identity
        self.assertNotEqual(identity, hashed_identity)
        
        # Verify hashing is deterministic
        self.assertEqual(hashed_identity, hash_identity(identity))
        
        # Verify different identities produce different hashes
        other_identity = "other@example.com"
        self.assertNotEqual(hash_identity(identity), hash_identity(other_identity))
        
        # Test with salt
        salt = "random_salt"
        salted_hash = hash_identity(identity, salt)
        
        # Verify salt changes the hash
        self.assertNotEqual(hashed_identity, salted_hash)
        
        # Verify salted hashing is still deterministic
        self.assertEqual(salted_hash, hash_identity(identity, salt))


if __name__ == '__main__':
    unittest.main()
