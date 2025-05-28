#!/usr/bin/env python3
import os
import sys
import argparse
from api.app import app
import config

def main():
    """
    Main entry point for the VoteChain application.
    Parses command line arguments and starts the Flask server.
    """
    parser = argparse.ArgumentParser(description='VoteChain - Blockchain Electronic Voting System')
    parser.add_argument('-p', '--port', type=int, default=config.FLASK_PORT,
                        help=f'Port to run the server on (default: {config.FLASK_PORT})')
    parser.add_argument('-H', '--host', type=str, default=config.FLASK_HOST,
                        help=f'Host to run the server on (default: {config.FLASK_HOST})')
    parser.add_argument('-d', '--debug', action='store_true', default=config.FLASK_DEBUG,
                        help='Run the server in debug mode')
    
    args = parser.parse_args()
    
    # Ensure the data directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    print(f"Starting VoteChain server on {args.host}:{args.port}")
    print(f"Access the web interface at http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
    
    # Run the Flask app
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
