# VoteChain - Solution Blockchain pour le Vote Électronique

## À propos du projet

VoteChain est une application blockchain développée pour sécuriser et décentraliser le processus de vote électronique. Ce projet répond aux exigences d'un système de vote moderne en offrant:

- **Transparence**: Toutes les transactions de vote sont enregistrées dans la blockchain et sont publiquement vérifiables
- **Anonymat**: L'identité des votants est protégée par le hachage cryptographique
- **Sécurité**: Utilisation de la cryptographie à clé publique/privée pour authentifier les votants
- **Immuabilité**: Une fois qu'un vote est enregistré, il ne peut pas être modifié
- **Décentralisation**: Aucun point de contrôle central, réduisant les risques de manipulation

## Justification de l'utilisation de la blockchain

### Problèmes des systèmes de vote traditionnels

1. **Confiance limitée**: Les systèmes centralisés nécessitent une confiance totale envers l'autorité centrale
2. **Manque de transparence**: Les citoyens ne peuvent pas vérifier eux-mêmes le décompte des votes
3. **Vulnérabilité aux manipulations**: Point unique de défaillance et possibilité de falsification des résultats
4. **Difficulté d'audit**: Absence de traçabilité complète et vérifiable du processus

### Avantages de la solution blockchain

1. **Registre immuable**: Les votes ne peuvent pas être modifiés une fois enregistrés
2. **Consensus distribué**: Plusieurs nœuds valident les transactions, éliminant le besoin d'une autorité centrale
3. **Transparence vérifiable**: Tout participant peut vérifier l'intégrité de la chaîne
4. **Cryptographie robuste**: Protection de l'anonymat tout en garantissant l'authenticité des votes
5. **Résistance à la censure**: Système résilient face aux tentatives de perturbation

## Fonctionnalités principales

- Authentification des votants avec cryptographie à clé publique/privée
- Protection de l'identité des votants par hachage
- Preuve cryptographique de l'intégrité des votes
- Interface web simple pour voter et consulter les résultats
- API RESTful pour l'intégration avec d'autres systèmes
- Vérification en temps réel du statut de l'élection

## Architecture technique

L'application est composée de plusieurs modules:

- **Blockchain**: Implémentation du registre distribué et du mécanisme de consensus
- **Cryptographie**: Gestion des clés, signatures et hachage d'identité
- **API**: Interface RESTful pour interagir avec la blockchain
- **Interface Web**: Application frontend pour les utilisateurs
- **CLI**: Utilitaires en ligne de commande pour l'administration

## Améliorations par rapport à une blockchain de base

1. **Système d'authentification avancé**: Utilisation de la cryptographie à clé publique/privée pour sécuriser les votes
2. **Anonymisation des votants**: Hachage des identités pour protéger la vie privée
3. **Interface utilisateur intuitive**: Simplification du processus de vote
4. **Validation spécifique au vote**: Règles métier adaptées au contexte électoral
5. **Mécanismes anti-fraude**: Prévention du double vote et vérification d'éligibilité

## Installation et démarrage

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. Clonez le dépôt:
   ```bash
   git clone https://github.com/votre-username/votechain.git
   cd votechain
   ```

2. Installez les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

3. Configuration (optionnel):
   Créez un fichier `.env` à la racine du projet pour personnaliser les paramètres:
   ```
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000
   FLASK_DEBUG=True
   ELECTION_NAME=Election Présidentielle 2025
   ```

### Exécution du serveur

```bash
python main.py
```

Le serveur démarre par défaut sur http://localhost:5000

### Exécution des tests

```bash
python -m unittest discover tests
```

## Utilisation du système

### Inscription des votants

1. Accédez à l'interface web et cliquez sur l'onglet "S'inscrire"
2. Entrez votre identifiant unique
3. Le système génère une paire de clés et affiche votre ID de votant hashé
4. **Important**: Conservez votre clé privée en lieu sûr, elle sera nécessaire pour voter

### Vote

1. Accédez à l'interface web et restez sur l'onglet "Voter"
2. Entrez votre ID de votant hashé et votre clé privée
3. Sélectionnez un candidat
4. Cliquez sur "Voter"
5. Le système vérifie votre identité et enregistre votre vote dans la blockchain

### Consultation des résultats

1. Accédez à l'interface web et cliquez sur l'onglet "Résultats"
2. Les résultats actuels de l'élection sont affichés
3. Cliquez sur "Rafraîchir les résultats" pour obtenir les dernières données

## Limites et perspectives d'amélioration

### Limites actuelles

- Implémentation simplifiée du consensus (preuve de travail basique)
- Absence de mécanisme de récupération en cas de perte de clé privée
- Interface administrateur limitée pour la gestion des élections

### Améliorations futures

- Implémentation d'un consensus plus efficace (Preuve d'enjeu ou DPoS)
- Ajout d'un système d'autorité de certification pour la vérification d'identité
- Développement d'une interface d'administration complète
- Intégration avec des systèmes d'identité numérique nationaux
- Support multi-élection et votes parallèles

## Licence

Ce projet est sous licence MIT.

## Auteurs

[Votre nom et celui de vos coéquipiers]
