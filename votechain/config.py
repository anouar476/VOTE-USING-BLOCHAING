import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Flask configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']

# Blockchain configuration
DIFFICULTY = int(os.getenv('DIFFICULTY', 4))  # Number of leading zeros required for proof of work
MINING_REWARD = os.getenv('MINING_REWARD', '0')  # Reward for mining a block (none for voting)

# Cryptography configuration
KEY_SIZE = int(os.getenv('KEY_SIZE', 2048))  # Size of RSA key in bits
HASH_ALGORITHM = os.getenv('HASH_ALGORITHM', 'sha256')  # Hash algorithm to use

# Election configuration
ELECTION_NAME = os.getenv('ELECTION_NAME', 'Election Générale')
ELECTION_START = os.getenv('ELECTION_START')  # Format: YYYY-MM-DD HH:MM:SS
ELECTION_END = os.getenv('ELECTION_END')  # Format: YYYY-MM-DD HH:MM:SS

# Security configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.urandom(24).hex())
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')  # Change this in production!

# Storage configuration (for persistent data)
DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
CHAIN_FILE = os.path.join(DATA_DIR, 'chain.json')
VOTERS_FILE = os.path.join(DATA_DIR, 'voters.json')
CANDIDATES_FILE = os.path.join(DATA_DIR, 'candidates.json')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)
