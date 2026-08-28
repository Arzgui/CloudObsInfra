# CloudObsInfra

Projet portfolio — infrastructure observée et sécurisée en Cloud.

## Objectif

Assembler dans un seul projet une application déployée sur une infrastructure
provisionnée par code (Terraform), avec pipeline CI/CD, logs centralisés
(OpenSearch) et détection d'anomalies (brute force sur l'authentification).

## Architecture

GitHub (push) → GitHub Actions (build + push image) → GHCR
↓
Serveur Hetzner (Terraform)
↓
Nginx (reverse proxy :80) → App FastAPI (:8000)
↓
Logs Docker (stdout, JSON)
↓
Fluent Bit (tail + parse JSON imbriqué)
↓
OpenSearch (index)
↓
Monitor (requête + trigger, seuil > 3
échecs de login / 5 min) → Alerte


## Stack

- **Backend** : Python / FastAPI
- **Infra** : Terraform (provider Hetzner Cloud)
- **Conteneurisation** : Docker
- **Reverse proxy** : Nginx
- **CI/CD** : GitHub Actions (build, push registry, déploiement SSH)
- **Registry** : GitHub Container Registry (ghcr.io)
- **Logs & supervision** : Fluent Bit → OpenSearch
- **Détection** : Monitor OpenSearch (requête + trigger par seuil)
- **Scan de vulnérabilités** : Trivy

## Choix techniques et justifications

- **Terraform / Hetzner** : provider choisi pour la simplicité de mise en
  place ; les concepts (provider, resource, state, variables) sont
  directement transférables à AWS/Azure/GCP — seuls les noms de ressources
  changent (ex. `hcloud_server` ↔ `aws_instance`, `hcloud_firewall` ↔
  `aws_security_group`).
- **Nginx en reverse proxy** : le firewall n'autorise que les ports
  22/80/443 (principe de moindre privilège) ; l'application écoute en
  interne sur le port 8000, jamais exposé directement à Internet.
- **Fluent Bit en mode `tail` plutôt que `forward`** : la première approche
  (Docker poussant activement les logs vers Fluent Bit) a échoué sous
  Docker Desktop/Windows (`dial tcp: i/o timeout`). Le mode `tail` (Fluent
  Bit lit directement les fichiers de logs Docker) est plus robuste et
  correspond de toute façon à la méthode la plus répandue pour lire des
  logs de conteneurs.
- **Monitor OpenSearch versionné via API** (`monitor_bruteforce.json`)
  plutôt que créé uniquement dans l'interface graphique : reproductible
  par quiconque clone le repo, cohérent avec la logique "infra as code"
  du reste du projet.

## Détection d'anomalie — mapping MITRE ATT&CK

L'application logue chaque tentative de connexion (succès/échec) en JSON
structuré. Un monitor OpenSearch surveille le nombre d'échecs sur une
fenêtre glissante de 5 minutes ; au-delà de 3 échecs, une alerte est
déclenchée.

- **Technique détectée** : Brute Force / Credential Stuffing
- **Référence MITRE ATT&CK** : [T1110](https://attack.mitre.org/techniques/T1110/)

## Scan de vulnérabilités (Trivy)

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image ghcr.io/arzgui/cloudobsinfra:latest
```

Résultat : 1 vulnérabilité CRITICAL (`perl-base`, CVE-2026-13221) et 1 HIGH
(`openssl-provider-legacy`, CVE-2026-14456), toutes deux héritées de
l'image de base système (Debian slim), pas du code applicatif. Piste de
remédiation : migrer vers une image de base plus minimaliste (ex.
`python:3.12-alpine`) pour réduire la surface de paquets système.

## Reproduire le projet

```bash
git clone https://github.com/Arzgui/CloudObsInfra.git
cd CloudObsInfra
docker compose up -d opensearch fluent-bit
sleep 15
docker compose up -d app
curl -X POST http://localhost:9200/_plugins/_alerting/monitors \
  -H "Content-Type: application/json" -d @monitor_bruteforce.json
```

Infra cloud (optionnelle) :
```bash
cd infra
export TF_VAR_hcloud_token="votre_token"
terraform init
terraform apply
```

## État d'avancement

- [x] Route `/login` fonctionnelle (succès + échec)
- [x] Dockerisation
- [x] Provisioning infra via Terraform
- [x] Déploiement automatique (GitHub Actions)
- [x] Logs structurés vers OpenSearch (Fluent Bit)
- [x] Détection d'anomalies (monitor/trigger, versionné)
- [x] Scan de vulnérabilités (Trivy)

## Limitations connues (assumées, projet portfolio)

- Sécurité OpenSearch désactivée (`DISABLE_SECURITY_PLUGIN=true`) —
  acceptable en local/démo, à ne jamais faire en production réelle
- Pas de HTTPS (pas de certificat SSL configuré sur Nginx)
- Seuil de détection (3 échecs / 5 min) arbitraire, à calibrer selon le
  trafic réel dans un vrai contexte de production