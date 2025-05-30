# eVoteChain - Système de Vote Électronique Sécurisé par Blockchain

## Table des matières

1. [Introduction](#introduction)
2. [Fonctionnalités](#fonctionnalités)
3. [Architecture technique](#architecture-technique)
4. [Explication détaillée du code](#explication-détaillée-du-code)
   - [Blockchain](#blockchain)
   - [Système cryptographique](#système-cryptographique)
   - [Processus de vote](#processus-de-vote)
   - [Interface utilisateur](#interface-utilisateur)
5. [Installation](#installation)
6. [Utilisation](#utilisation)
7. [Pour les développeurs](#pour-les-développeurs)
8. [Considérations de sécurité](#considérations-de-sécurité)
9. [Déploiement distribué](#déploiement-sur-un-réseau-distribué)
10. [Limitations et améliorations](#limitations-et-améliorations-futures)
11. [License](#license)

## Introduction

eVoteChain est une application de vote électronique basée sur la technologie blockchain, garantissant la transparence, l'immutabilité et la vérification cryptographique de chaque vote. Ce système permet aux électeurs de s'inscrire avec leur numéro CIN (Carte d'Identité Nationale), de recevoir une paire de clés cryptographiques, et de voter pour leur candidat préféré de manière sécurisée et vérifiable.

Ce projet implémente une blockchain complète avec son propre mécanisme de consensus (preuve de travail), un système de signature cryptographique, et une interface utilisateur moderne et intuitive.

## Fonctionnalités

- **Inscription des électeurs** avec génération de clés cryptographiques
- **Vote sécurisé** avec signature numérique
- **Vérification cryptographique** de chaque vote
- **Résultats en temps réel** visualisés graphiquement
- **Exploration de la blockchain** pour auditer le processus de vote
- **Protection contre la double-vote** grâce à la vérification d'unicité
- **Interface responsive et animée** pour une expérience utilisateur optimale
- **Un bloc par vote** pour une traçabilité maximale

## Architecture technique

- **Frontend** : Interface web responsive avec HTML5, CSS3, JavaScript
- **Librairies frontend** : Bootstrap 5.2, Chart.js, GSAP, Animate.css
- **Backend** : Flask 2.0 et Python 3.11
- **Blockchain** : Implémentation personnalisée en Python
- **Cryptographie** : RSA (2048 bits) et SHA-256 via PyCryptodome
- **Authentification** : Par clé publique/privée (chaque électeur reçoit une paire)
- **Consensus** : Preuve de travail avec difficulté ajustable
- **Stockage des données** : En mémoire avec cache pour les informations d'électeurs

## Explication détaillée du code

### Blockchain

La blockchain est le composant central du système, implémentée dans le fichier `blockchain.py`. Elle gère l'ensemble des opérations liées à la chaîne de blocs, au minage et aux transactions.

#### Structure des blocs

```python
def new_block(self, proof, previous_hash=None, block_type='vote'):
    """
    Create a new Block in the Blockchain
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
```
    
Chaque bloc contient :
- Un index unique
- Un horodatage
- La liste des transactions (un seul vote par bloc)
- Une preuve de travail
- Le hash du bloc précédent
- Un type (vote)

#### Algorithme de consensus

Le système utilise un algorithme de preuve de travail qui consiste à trouver un nombre qui, combiné avec la preuve du bloc précédent, donne un hash avec 4 zéros en préfixe :

```python
def proof_of_work(self, last_proof):
    """
    Simple Proof of Work Algorithm
    """
    proof = 0
    while self.valid_proof(last_proof, proof) is False:
        proof += 1
    return proof

def valid_proof(self, last_proof, proof):
    """
    Validates the Proof
    """
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:4] == "0000"
```

#### Gestion des votes

Chaque vote est stocké dans un bloc unique pour garantir une traçabilité maximale :

```python
def new_vote(self, cin_hash, candidate, signature, public_key):
    """
    Creates a new vote transaction
    """
    # Validate voter using cache
    if cin_hash not in voter_cache:
        return {
            'message': "Cet électeur n'est pas inscrit."
        }
    
    if voter_cache[cin_hash]['has_voted']:
        return {
            'message': "Cet électeur a déjà voté."
        }
        
    # Verify signature
    message = f"{cin_hash}{candidate}".encode()
    if not self.verify_signature(message, signature, public_key):
        return {
            'message': "Signature invalide."
        }
    
    # Create a new vote transaction
    vote = {
        'type': 'vote',
        'cin_hash': cin_hash,
        'candidate': candidate,
        'timestamp': time.time(),
        'signature': signature,
        'public_key': public_key,
        'id': str(uuid4())
    }
    
    self.current_transactions.append(vote)
    
    return {'message': "Vote ajouté aux transactions en attente."}
```

### Système cryptographique

La cryptographie est essentielle pour garantir la sécurité et l'authenticité des votes. Le système utilise des clés asymétriques RSA.

#### Génération des clés

```python
def generate_keys():
    """
    Generate a new pair of private and public keys
    """
    key = RSA.generate(2048)  # Génère une clé RSA de 2048 bits
    private_key = key.export_key().decode('utf-8')
    public_key = key.publickey().export_key().decode('utf-8')
    
    return private_key, public_key
```

#### Signature des votes

```python
def sign_vote(private_key, cin_hash, candidate):
    """
    Sign a vote with the private key
    """
    key = RSA.import_key(private_key)
    message = f"{cin_hash}{candidate}".encode()
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    return signature.hex()
```

Le processus de signature fonctionne ainsi :
1. La clé privée de l'électeur est importée
2. Un message est créé en combinant le hash du CIN et le candidat choisi
3. Ce message est haché avec SHA-256
4. Le hash est signé avec la clé privée en utilisant l'algorithme PKCS#1 v1.5
5. La signature est convertie en format hexadécimal pour le stockage

#### Vérification des signatures

```python
def verify_signature(self, message, signature, public_key):
    """
    Verify a digital signature
    """
    try:
        key = RSA.import_key(public_key)
        h = SHA256.new(message)
        pkcs1_15.new(key).verify(h, bytes.fromhex(signature))
        return True
    except (ValueError, TypeError):
        return False
```

Cette vérification fonctionne ainsi :
1. La clé publique de l'électeur est importée
2. Le même message (hash du CIN + candidat) est haché à nouveau avec SHA-256
3. L'algorithme PKCS#1 v1.5 est utilisé pour vérifier que la signature correspond bien au hash
4. Si la vérification réussit, la fonction renvoie `True` (signature valide)
5. Si une exception est levée (signature invalide), la fonction renvoie `False`

### Processus de vote

Le processus de vote est géré par l'application Flask dans `app.py`. Voici les étapes principales :

#### Inscription des électeurs

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        cin = request.form.get('cin')
        
        # Vérifier si le CIN est valide
        if not cin or len(cin) < 8:
            flash('CIN invalide!', 'danger')
            return redirect(url_for('register'))
        
        # Hasher le CIN
        cin_hash = hashlib.sha256(cin.encode()).hexdigest()
        
        # Vérifier si l'électeur est déjà inscrit
        if cin_hash in voter_cache:
            flash('Cet électeur est déjà inscrit!', 'warning')
            return redirect(url_for('register'))
        
        # Générer les clés
        private_key, public_key = generate_keys()
        
        # Stocker les informations dans le cache
        voter_cache[cin_hash] = {
            'public_key': public_key,
            'has_voted': False
        }
        
        # Stocker les clés dans la session
        session['cin'] = cin
        session['private_key'] = private_key
        session['public_key'] = public_key
        
        flash('Inscription réussie! Vous pouvez maintenant voter.', 'success')
        return redirect(url_for('vote'))
    
    return render_template('register.html')
```

#### Soumission d'un vote

```python
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    # Vérifier si l'électeur est inscrit
    if 'cin' not in session:
        flash('Vous devez vous inscrire avant de voter!', 'warning')
        return redirect(url_for('register'))
    
    cin_hash = hashlib.sha256(session['cin'].encode()).hexdigest()
    
    # Vérifier si l'électeur existe dans le cache
    if cin_hash not in voter_cache:
        flash('Vous devez vous inscrire avant de voter!', 'warning')
        return redirect(url_for('register'))
    
    # Vérifier si l'électeur a déjà voté
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
                
            # Signer le vote
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
            
            # Miner un nouveau bloc pour inclure le vote
            last_block = blockchain.last_block
            last_proof = last_block['proof']
            proof = blockchain.proof_of_work(last_proof)
            
            # Forger le nouveau bloc avec seulement ce vote
            blockchain.new_block(proof, block_type='vote')
            
            # Mettre à jour le cache
            voter_cache[cin_hash]['has_voted'] = True
            
            flash('Votre vote a été enregistré dans la blockchain!', 'success')
            return redirect(url_for('results'))
        except Exception as e:
            flash(f'Erreur lors du vote: {str(e)}', 'danger')
            return redirect(url_for('vote'))
    
    return render_template('vote.html', candidates=candidates)
```

### Interface utilisateur

L'interface utilisateur est développée avec Flask, Bootstrap 5.2, Chart.js, GSAP et Animate.css. Voici quelques éléments clés :

#### Affichage des résultats

```html
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="card shadow-lg border-0 rounded-4 mb-5 animate__animated animate__fadeIn">
                <div class="card-header bg-primary text-white text-center py-3 rounded-top-4">
                    <h2 class="mb-0">Résultats des Élections</h2>
                </div>
                <div class="card-body p-4">
                    <!-- Graphique des votes -->
                    <div class="chart-container position-relative" style="height:50vh;">
                        <canvas id="resultsChart"></canvas>
                    </div>
                    
                    <!-- Liste détaillée des résultats -->
                    <div class="mt-5">
                        <h3 class="text-center mb-4">Détail des votes</h3>
                        <div class="row">
                            {% for candidate in candidates %}
                            <div class="col-md-4 mb-4">
                                <div class="card h-100 border-0 shadow-sm candidate-card">
                                    <div class="card-body text-center">
                                        <h4 class="candidate-name">{{ candidate }}</h4>
                                        <div class="vote-count my-3" id="count-{{ candidate }}">0</div>
                                        <div class="progress rounded-pill" style="height: 10px;">
                                            <div class="progress-bar bg-primary progress-bar-striped progress-bar-animated" 
                                                role="progressbar" id="progress-{{ candidate }}" style="width: 0%;"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

#### Visualisation avec Chart.js

```javascript
const resultsChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: candidatesList,
        datasets: [{
            label: 'Votes',
            data: candidatesList.map(function(candidate) { 
                return getVoteCount(candidate); 
            }),
            backgroundColor: generateGradientColors(candidatesList.length),
            borderWidth: 0,
            borderRadius: 6,
            borderSkipped: false,
            maxBarThickness: 40
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1500,
            easing: 'easeOutQuart'
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0,0,0,0.8)',
                titleFont: {
                    size: 16
                },
                bodyFont: {
                    size: 14
                },
                padding: 12,
                cornerRadius: 8,
                displayColors: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0
                },
                grid: {
                    display: true,
                    color: 'rgba(0,0,0,0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});
```

## Prérequis

- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone <URL_DU_DEPOT>
   cd evotechain
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

1. Démarrez l'application :
   ```bash
   python app.py
   ```

2. Ouvrez votre navigateur à l'adresse `http://localhost:8080`

3. Suivez le processus :
   - Inscrivez-vous en fournissant votre numéro CIN
   - Le système génère automatiquement vos clés cryptographiques
   - Sélectionnez votre candidat et votez
   - Visualisez les résultats en temps réel
   - Explorez la blockchain pour vérifier la transparence du processus

## Pour les développeurs

### Structure du projet

```
/mini projet
├── app.py                 # Application Flask principale
├── blockchain.py          # Implémentation de la blockchain
├── requirements.txt       # Dépendances Python
└── templates/             # Templates HTML
    ├── base.html          # Template de base avec les styles communs
    ├── blockchain.html    # Visualisation de la blockchain
    ├── index.html         # Page d'accueil
    ├── register.html      # Inscription des électeurs
    ├── results.html       # Affichage des résultats
    └── vote.html          # Interface de vote
```

### Fonctionnement du consensus

Le système utilise un algorithme de preuve de travail simplifié où chaque nœud doit trouver un nombre qui, combiné avec la preuve du bloc précédent, donne un hash avec un certain nombre de zéros au début. Cette approche est similaire à celle utilisée par Bitcoin, mais avec une difficulté moindre pour faciliter le minage rapide sur un seul serveur.

### Extensibilité du code

Le code a été conçu pour être modulaire et facilement extensible :

- Ajout de nouveaux candidats : il suffit de mettre à jour la liste `candidates` dans `app.py`
- Modification de la difficulté du consensus : en changeant le nombre de zéros requis dans `valid_proof()`
- Implémentation d'autres algorithmes de consensus : en créant de nouvelles méthodes dans la classe `Blockchain`
- Ajout de nouvelles fonctionnalités à l'interface : grâce à la structure modulaire des templates

## Considérations de sécurité

### Modèle de sécurité

Le système eVoteChain repose sur plusieurs mécanismes de sécurité :

1. **Cryptographie asymétrique** : Utilisation de clés RSA 2048 bits pour la signature des votes

2. **Signatures numériques** : Chaque vote est signé avec la clé privée de l'électeur, garantissant :
   - L'authenticité : seul le détenteur de la clé privée peut voter
   - L'intégrité : toute modification du vote invalidera la signature
   - La non-répudiation : l'électeur ne peut nier avoir voté

3. **Protection contre le double-vote** :
   - Vérification dans le cache `voter_cache` pour s'assurer qu'un électeur ne vote qu'une fois
   - Stockage d'un flag `has_voted` pour chaque électeur

4. **Immutabilité de la blockchain** :
   - Chaque bloc contient le hash du bloc précédent
   - Toute modification d'un bloc invaliderait tous les blocs suivants

5. **Vérification des clés publiques** :
   - La clé publique utilisée pour le vote doit correspondre à celle stockée dans le cache

### Limitations actuelles

1. **Stockage des clés** : Les clés privées sont stockées dans la session utilisateur, ce qui peut être vulnérable aux attaques XSS

2. **Centralisation** : Le système actuel fonctionne sur un seul serveur, ce qui le rend vulnérable aux attaques DDoS

3. **Persistance des données** : Le stockage en mémoire est volatil et ne survit pas aux redémarrages du serveur

## Déploiement sur un réseau distribué

Pour déployer cette application sur un réseau distribué et la rendre véritablement décentralisée :

1. Lancez l'application sur plusieurs nœuds différents :
   ```bash
   python app.py --port=8080 --node=1
   python app.py --port=8081 --node=2
   # etc.
   ```

2. Sur chaque nœud, enregistrez les autres nœuds via l'API `/nodes/register` :
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{
     "nodes": ["http://localhost:8081", "http://localhost:8082"]
   }' "http://localhost:8080/nodes/register"
   ```

3. Le consensus résoudra automatiquement les conflits entre les différentes copies de la blockchain en choisissant la plus longue chaîne valide.

## Limitations et améliorations futures

### Limitations actuelles

1. **Stockage en mémoire** : Les données de la blockchain et le cache des électeurs sont stockés en mémoire, ce qui les rend volatiles.

2. **Scalabilité** : L'implémentation actuelle n'est pas optimisée pour un très grand nombre d'électeurs ou de transactions.

3. **Anonymat partiel** : Bien que nous utilisions le hash du CIN, une corrélation pourrait être faite entre un électeur et son vote dans certaines circonstances.

4. **Interface d'administration limitée** : Pas d'interface dédiée pour gérer les élections ou les candidats.

### Améliorations proposées

1. **Stockage persistant** :
   - Implémenter une base de données (PostgreSQL, MongoDB) pour stocker la blockchain
   - Utiliser Redis pour la gestion du cache des électeurs

2. **Renforcement de la sécurité** :
   - Implémenter un système d'authentification à deux facteurs
   - Utiliser des hardwares sécurisés (HSM) pour la gestion des clés
   - Mettre en place un chiffrement homomorphe pour améliorer la confidentialité

3. **Amélioration de l'expérience utilisateur** :
   - Développer une application mobile pour les électeurs
   - Implémenter une vérification individuelle des votes ("voter verification")
   - Créer un tableau de bord d'administration pour la gestion des élections

4. **Scalabilité et performance** :
   - Optimiser l'algorithme de consensus pour un minage plus efficace
   - Implémenter des techniques de sharding pour la blockchain
   - Utiliser des caches distribués pour améliorer les performances

5. **Interopérabilité** :
   - Développer une API REST complète pour l'intégration avec d'autres systèmes
   - Implémenter des standards de blockchain comme ERC20 ou similar

## License

Ce projet est distribué sous licence MIT.

---

© 2025 eVoteChain. Tous droits réservés.

2. Ouvrez votre navigateur à l'adresse `http://localhost:5000`

3. Suivez le processus :
   - Inscrivez-vous avec un identifiant d'électeur
   - Recevez vos clés cryptographiques
   - Votez pour votre candidat préféré
   - Explorez les résultats et la blockchain

## Pour les développeurs

### Structure du projet

- `app.py` - Application Flask principale
- `blockchain.py` - Implémentation de la blockchain
- `templates/` - Fichiers HTML de l'interface utilisateur
- `requirements.txt` - Dépendances du projet

### Fonctionnement du consensus

Le système utilise un algorithme de preuve de travail simplifié où chaque nœud doit trouver un nombre qui, combiné avec la preuve du bloc précédent, donne un hash avec un certain nombre de zéros au début.

### Sécurité

- Chaque vote est signé avec la clé privée de l'électeur
- Les signatures sont vérifiées avec la clé publique correspondante
- L'immutabilité de la blockchain garantit qu'aucun vote ne peut être modifié

## Déploiement sur un réseau distribué

Pour déployer cette application sur un réseau distribué :

1. Lancez l'application sur plusieurs nœuds différents
2. Sur chaque nœud, enregistrez les autres nœuds via l'API `/nodes/register`
3. Le consensus résoudra automatiquement les conflits pour maintenir une chaîne cohérente

## License

Ce projet est distribué sous licence MIT.
