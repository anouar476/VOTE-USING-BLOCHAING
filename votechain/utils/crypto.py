from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import hashlib
import json
from typing import Tuple, Dict, Any, Optional


def generate_key_pair() -> Tuple[str, str]:
    """
    Generate a new RSA key pair for a voter.
    
    Returns:
        Tuple containing (private_key, public_key) in PEM format
    """
    key = RSA.generate(2048)
    private_key = key.export_key().decode('utf-8')
    public_key = key.publickey().export_key().decode('utf-8')
    
    return private_key, public_key


def sign_vote(vote_data: Dict[str, Any], private_key_pem: str) -> str:
    """
    Sign vote data with voter's private key.
    
    Args:
        vote_data: Dictionary containing vote information
        private_key_pem: Private key in PEM format
        
    Returns:
        Base64 encoded signature
    """
    # Create a deterministic representation of the vote data
    vote_string = json.dumps(vote_data, sort_keys=True)
    
    # Hash the vote data
    h = SHA256.new(vote_string.encode('utf-8'))
    
    # Load the private key and create the signature
    private_key = RSA.import_key(private_key_pem)
    signature = pkcs1_15.new(private_key).sign(h)
    
    # Return base64 encoded signature
    return base64.b64encode(signature).decode('utf-8')


def verify_signature(vote_data: Dict[str, Any], signature: str, public_key_pem: str) -> bool:
    """
    Verify that the vote was signed by the owner of the private key.
    
    Args:
        vote_data: Dictionary containing vote information
        signature: Base64 encoded signature
        public_key_pem: Public key in PEM format
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Create a deterministic representation of the vote data
        vote_string = json.dumps(vote_data, sort_keys=True)
        
        # Hash the vote data
        h = SHA256.new(vote_string.encode('utf-8'))
        
        # Load the public key and verify the signature
        public_key = RSA.import_key(public_key_pem)
        signature_bytes = base64.b64decode(signature)
        pkcs1_15.new(public_key).verify(h, signature_bytes)
        
        return True
    except (ValueError, TypeError):
        return False


def hash_identity(identity_string: str, salt: Optional[str] = None) -> str:
    """
    Create a one-way hash of a voter's identity to maintain anonymity while preventing double-voting.
    
    Args:
        identity_string: Unique identifier for the voter (e.g., ID number, email)
        salt: Optional salt to add security
        
    Returns:
        Hashed identity
    """
    if salt:
        identity_string = f"{identity_string}{salt}"
    
    return hashlib.sha256(identity_string.encode('utf-8')).hexdigest()
