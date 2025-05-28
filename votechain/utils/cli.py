#!/usr/bin/env python3
import argparse
import json
import requests
import sys
import os
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.crypto import generate_key_pair, sign_vote, hash_identity

BASE_URL = 'http://localhost:5000'


def register_voter(voter_id: str) -> Dict[str, Any]:
    """
    Register a new voter and generate their key pair.
    
    Args:
        voter_id: Unique identifier for the voter
        
    Returns:
        Dict containing registration status and key pair if successful
    """
    # Generate key pair for the voter
    private_key, public_key = generate_key_pair()
    
    # Register voter with the blockchain
    response = requests.post(
        f'{BASE_URL}/voters/register',
        json={
            'voter_id': hash_identity(voter_id),
            'public_key': public_key
        }
    )
    
    if response.status_code == 201:
        return {
            'status': 'success',
            'message': 'Voter registered successfully',
            'private_key': private_key,
            'public_key': public_key,
            'voter_id': hash_identity(voter_id)
        }
    else:
        return {
            'status': 'error',
            'message': response.json().get('message', 'Registration failed')
        }


def register_candidate(candidate_id: str, name: str, party: str) -> Dict[str, Any]:
    """
    Register a new candidate for the election.
    
    Args:
        candidate_id: Unique identifier for the candidate
        name: Candidate's name
        party: Candidate's political party
        
    Returns:
        Dict containing registration status
    """
    response = requests.post(
        f'{BASE_URL}/candidates/register',
        json={
            'candidate_id': candidate_id,
            'name': name,
            'party': party
        }
    )
    
    if response.status_code == 201:
        return {
            'status': 'success',
            'message': 'Candidate registered successfully'
        }
    else:
        return {
            'status': 'error',
            'message': response.json().get('message', 'Registration failed')
        }


def cast_vote(voter_id: str, candidate_id: str, private_key: str) -> Dict[str, Any]:
    """
    Cast a vote for a candidate.
    
    Args:
        voter_id: Voter's unique identifier (hashed)
        candidate_id: Candidate's unique identifier
        private_key: Voter's private key
        
    Returns:
        Dict containing vote status
    """
    # Create vote data to sign
    vote_data = {
        'voter_id': voter_id,
        'candidate_id': candidate_id
    }
    
    # Sign the vote data with voter's private key
    signature = sign_vote(vote_data, private_key)
    
    # Extract public key from private key
    # In a real application, the voter would have their key pair safely stored
    _, public_key = generate_key_pair()
    
    # Send the transaction to the blockchain
    response = requests.post(
        f'{BASE_URL}/transactions/new',
        json={
            'voter_id': voter_id,
            'candidate_id': candidate_id,
            'signature': signature,
            'public_key': public_key
        }
    )
    
    if response.status_code == 201:
        return {
            'status': 'success',
            'message': response.json().get('message', 'Vote cast successfully')
        }
    else:
        return {
            'status': 'error',
            'message': response.json().get('message', 'Vote failed')
        }


def get_election_results() -> Dict[str, Any]:
    """
    Get the current election results.
    
    Returns:
        Dict containing election results
    """
    response = requests.get(f'{BASE_URL}/election/results')
    
    if response.status_code == 200:
        return {
            'status': 'success',
            'results': response.json()
        }
    else:
        return {
            'status': 'error',
            'message': 'Failed to retrieve election results'
        }


def get_election_status() -> Dict[str, Any]:
    """
    Get the current status of the election.
    
    Returns:
        Dict containing election status
    """
    response = requests.get(f'{BASE_URL}/election/status')
    
    if response.status_code == 200:
        return {
            'status': 'success',
            'election_status': response.json()
        }
    else:
        return {
            'status': 'error',
            'message': 'Failed to retrieve election status'
        }


def mine_block() -> Dict[str, Any]:
    """
    Mine a new block to add pending votes to the blockchain.
    
    Returns:
        Dict containing mining status
    """
    response = requests.get(f'{BASE_URL}/mine')
    
    if response.status_code == 200:
        return {
            'status': 'success',
            'block': response.json()
        }
    else:
        return {
            'status': 'error',
            'message': 'Mining failed'
        }


def view_blockchain() -> Dict[str, Any]:
    """
    View the entire blockchain.
    
    Returns:
        Dict containing the blockchain
    """
    response = requests.get(f'{BASE_URL}/chain')
    
    if response.status_code == 200:
        return {
            'status': 'success',
            'chain': response.json()
        }
    else:
        return {
            'status': 'error',
            'message': 'Failed to retrieve blockchain'
        }


def main():
    parser = argparse.ArgumentParser(description='VoteChain CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Register voter command
    register_voter_parser = subparsers.add_parser('register-voter', help='Register a new voter')
    register_voter_parser.add_argument('voter_id', help='Unique identifier for the voter')
    
    # Register candidate command
    register_candidate_parser = subparsers.add_parser('register-candidate', help='Register a new candidate')
    register_candidate_parser.add_argument('candidate_id', help='Unique identifier for the candidate')
    register_candidate_parser.add_argument('name', help='Candidate name')
    register_candidate_parser.add_argument('party', help='Candidate political party')
    
    # Cast vote command
    cast_vote_parser = subparsers.add_parser('cast-vote', help='Cast a vote for a candidate')
    cast_vote_parser.add_argument('voter_id', help='Voter ID (hashed)')
    cast_vote_parser.add_argument('candidate_id', help='Candidate ID')
    cast_vote_parser.add_argument('private_key', help='Voter private key')
    
    # Get election results command
    subparsers.add_parser('results', help='Get election results')
    
    # Get election status command
    subparsers.add_parser('status', help='Get election status')
    
    # Mine block command
    subparsers.add_parser('mine', help='Mine a new block')
    
    # View blockchain command
    subparsers.add_parser('chain', help='View the blockchain')
    
    args = parser.parse_args()
    
    if args.command == 'register-voter':
        result = register_voter(args.voter_id)
        print(json.dumps(result, indent=4))
        if result['status'] == 'success':
            print("\nIMPORTANT: Save your private key safely. You will need it to cast your vote.")
            print(f"Your hashed voter ID is: {result['voter_id']}")
    
    elif args.command == 'register-candidate':
        result = register_candidate(args.candidate_id, args.name, args.party)
        print(json.dumps(result, indent=4))
    
    elif args.command == 'cast-vote':
        result = cast_vote(args.voter_id, args.candidate_id, args.private_key)
        print(json.dumps(result, indent=4))
    
    elif args.command == 'results':
        result = get_election_results()
        print(json.dumps(result, indent=4))
    
    elif args.command == 'status':
        result = get_election_status()
        print(json.dumps(result, indent=4))
    
    elif args.command == 'mine':
        result = mine_block()
        print(json.dumps(result, indent=4))
    
    elif args.command == 'chain':
        result = view_blockchain()
        print(json.dumps(result, indent=4))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
