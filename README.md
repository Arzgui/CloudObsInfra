# CloudObsInfra

Projet portfolio — infrastructure observée et sécurisée en Cloud.

## Objectif

Assembler dans un seul projet : une application déployée sur une infrastructure
provisionnée par code (Terraform), avec pipeline CI/CD, logs centralisés (OpenSearch)
et détection d'anomalies (ex. brute force sur l'authentification).

## Stack

- **Backend** : Python / FastAPI
- **Infra** : Terraform (à venir)
- **Conteneurisation** : Docker (à venir)
- **CI/CD** : GitHub Actions (à venir)
- **Logs & supervision** : Fluent Bit → OpenSearch (à venir)

## État d'avancement

- [x] Route `/login` fonctionnelle (données de test en dur)
- [x] Cas d'échec de connexion
- [x] Dockerisation
- [ ] Provisioning infra via Terraform
- [ ] Déploiement automatique (GitHub Actions)
- [ ] Logs vers OpenSearch
- [ ] Détection d'anomalies (monitor/trigger)