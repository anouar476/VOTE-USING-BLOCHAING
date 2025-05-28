# Documentation Technique - VoteChain

## Architecture du Système

VoteChain est une application blockchain conçue pour le vote électronique, avec une architecture modulaire composée de plusieurs composants clés:

### 1. Couche Blockchain (Core)

Le cœur du système est une implémentation blockchain personnalisée pour le vote électronique:

- **Block**: Unité fondamentale de la blockchain, contenant:
  - Index
  - Horodatage
  - Transactions (votes)
  - Hash du bloc précédent
  - Preuve de travail
  - Hash du bloc actuel

- **Blockchain**: Gère la chaîne de blocs et implémente:
  - Création de blocs
  - Ajout de transactions (votes)
  - Algorithme de preuve de travail
  - Mécanisme de consensus (résolution des conflits)
  - Validation de la chaîne

### 2. Couche Cryptographique

Module gérant toutes les opérations cryptographiques essentielles:

- Génération de paires de clés RSA (publique/privée)
- Signature des votes avec la clé privée du votant
- Vérification des signatures avec la clé publique
- Hachage des identités des votants pour l'anonymisation

### 3. Couche API

Interface RESTful construite avec Flask pour interagir avec la blockchain:

- Endpoints pour l'enregistrement des votants
- Endpoints pour l'enregistrement des candidats
- Endpoints pour soumettre des votes
- Endpoints pour consulter les résultats de l'élection
- Endpoints pour le minage de blocs et la maintenance du réseau

### 4. Interface Utilisateur

- Interface web simple pour les votants
- Interface CLI pour l'administration et les tests

## Flux de Données

### Processus d'Enregistrement d'un Votant

1. Le votant soumet son identifiant unique
2. Le système génère une paire de clés (publique/privée)
3. L'identifiant est haché pour protéger l'anonymat
4. Le votant reçoit son ID haché et sa clé privée
5. La clé publique et l'ID haché sont enregistrés dans le système

### Processus de Vote

1. Le votant s'authentifie avec son ID haché et sa clé privée
2. Le votant sélectionne un candidat
3. Le vote est signé avec la clé privée du votant
4. Le système vérifie la signature avec la clé publique enregistrée
5. Le vote est ajouté comme transaction en attente
6. Un mineur crée un bloc contenant la transaction
7. Le bloc est ajouté à la blockchain

## Implémentation Technique

### Structure de Données des Blocs

```python
{
    "index": 1,
    "timestamp": 1622547854.2548828,
    "transactions": [
        {
            "voter_id": "8a7b9e3f4c2d1e0f6a5b8c2d3e7f9a1b",
            "candidate_id": "candidate1",
            "signature": "base64_encoded_signature",
            "public_key": "public_key_pem_format",
            "timestamp": 1622547853.1234567
        }
    ],
    "previous_hash": "0",
    "proof": 12345,
    "hash": "current_block_hash"
}
```

### Structure de Données des Votants

```python
{
    "8a7b9e3f4c2d1e0f6a5b8c2d3e7f9a1b": "public_key_pem_format"
}
```

### Structure de Données des Candidats

```python
{
    "candidate1": {
        "name": "Marie Dupont",
        "party": "Parti A"
    }
}
```

## Algorithmes Clés

### Preuve de Travail

La preuve de travail est un algorithme qui exige qu'un certain travail soit effectué avant de créer un nouveau bloc. Dans notre implémentation:

1. On cherche un nombre (preuve) tel que le hachage de la concaténation de la preuve précédente et de la nouvelle preuve contient N zéros en tête.
2. La difficulté (nombre de zéros) est configurée dans les paramètres.

```python
def proof_of_work(last_proof):
    proof = 0
    while valid_proof(last_proof, proof) is False:
        proof += 1
    return proof

def valid_proof(last_proof, proof):
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:DIFFICULTY] == "0" * DIFFICULTY
```

### Signature et Vérification

1. Pour signer un vote, nous créons un hash SHA-256 des données du vote, puis signons ce hash avec la clé privée RSA du votant.
2. Pour vérifier, nous recalculons le hash et vérifions la signature avec la clé publique.

```python
def sign_vote(vote_data, private_key_pem):
    # Create a deterministic representation of the vote data
    vote_string = json.dumps(vote_data, sort_keys=True)
    
    # Hash the vote data
    h = SHA256.new(vote_string.encode('utf-8'))
    
    # Load the private key and create the signature
    private_key = RSA.import_key(private_key_pem)
    signature = pkcs1_15.new(private_key).sign(h)
    
    # Return base64 encoded signature
    return base64.b64encode(signature).decode('utf-8')
```

## Sécurité

### Prévention du Double Vote

- Chaque votant n'est autorisé à voter qu'une seule fois
- Les tentatives de double vote sont détectées et rejetées
- Un ensemble de "votes_cast" maintient la liste des votants ayant déjà voté

### Protection de l'Anonymat

- Les identités des votants sont protégées par hachage
- Aucune information personnelle n'est stockée dans la blockchain
- Le lien entre l'identité réelle et l'identité hachée est uniquement connu du votant

### Intégrité des Votes

- Chaque vote est signé cryptographiquement
- La blockchain garantit l'immuabilité des votes
- Le consensus distribué empêche la falsification

## Extensions Possibles

### Améliorations de Sécurité

- Implémentation d'un protocole de connaissance zéro pour prouver l'éligibilité sans révéler l'identité
- Utilisation de l'aveuglage cryptographique pour renforcer l'anonymat
- Ajout d'un système multi-signature pour l'authentification

### Améliorations de Performance

- Remplacement de la preuve de travail par un consensus plus efficace (PoS, DPoS, PBFT)
- Optimisation de la structure de données pour des performances accrues
- Implémentation de sharding pour la scalabilité

### Fonctionnalités Additionnelles

- Support pour différents types de votes (oui/non, classement, votes pondérés)
- Intégration avec des systèmes d'identité numérique nationaux
- Ajout d'un système de délégation de vote (vote par procuration)

## Limites Connues

- Dépendance à la disponibilité des nœuds pour la propagation des transactions
- Coût computationnel de la preuve de travail
- Nécessité pour les votants de conserver leur clé privée en sécurité

## Références Techniques

- [Documentation de Flask](https://flask.palletsprojects.com/)
- [Documentation de PyCryptodome](https://pycryptodome.readthedocs.io/)
- [Livre blanc Bitcoin](https://bitcoin.org/bitcoin.pdf)
- [Protocoles de vote électronique sécurisé](https://www.nist.gov/publications/security-considerations-remote-electronic-voting)
