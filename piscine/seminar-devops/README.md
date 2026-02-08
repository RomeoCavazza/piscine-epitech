# Séminaire DevOps (Days 56–60)

![Linux](https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black)
![Debian](https://img.shields.io/badge/Debian-A81D33?logo=debian&logoColor=white)
![VirtualBox](https://img.shields.io/badge/VirtualBox-183A61?logo=virtualbox&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?logo=gnubash&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?logo=ansible&logoColor=white)
![Apache](https://img.shields.io/badge/Apache-D22128?logo=apache&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)
![PHP](https://img.shields.io/badge/PHP-777BB4?logo=php&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-003545?logo=mariadb&logoColor=white)
![SSH](https://img.shields.io/badge/SSH-000000?logo=ssh&logoColor=white)
![Symfony](https://img.shields.io/badge/Symfony-000000?logo=symfony&logoColor=white)
![Composer](https://img.shields.io/badge/Composer-885630?logo=composer&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?logo=nodedotjs&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)

Administration système, virtualisation, sécurité réseau, déploiement d'applications et automatisation DevOps avec Ansible.

## Contenu
- Day 56 → Sécurité système et configuration VM sécurisée ([README](Day_56/README.md))
  - Installation Debian, gestion utilisateurs/groups, SSH sécurisé, fail2ban, nftables
- Day 57 → Architecture client-gateway et configuration réseau ([README](Day_57/README.md))
  - Machines virtuelles client/gateway, DHCP (kea-dhcp4-server), routage nftables, DNS (bind9)
- Days 58–59 → Configuration serveur et déploiement d'applications ([README](Day_58_59/README.md))
  - Serveur web (Apache2), base de données (MariaDB), déploiement frontend/backend, sécurité, sauvegardes, HTTPS
- Day 60 → Automatisation avec Ansible ([README](Day_60/README.md))
  - Infrastructure as Code, rôles Ansible, automatisation complète d'une stack web (Nginx, PHP, MariaDB)

## Notions
- **Virtualisation** : VirtualBox, machines virtuelles, snapshots, réseaux privés, interfaces multiples
- **Sécurité système** : Gestion utilisateurs/groups (UID/GID), SSH sécurisé, fail2ban, nftables (pare-feu moderne)
- **Réseau** : Architecture client-gateway-serveur, DHCP (kea-dhcp4-server), DNS (bind9), routage, NAT
- **Services web** : Apache2, Nginx, virtualhosts, ports personnalisés, authentification basique
- **Bases de données** : MariaDB/MySQL, création d'utilisateurs, gestion des droits, accessibilité réseau
- **Déploiement** : Applications full-stack (frontend/backend), PHP, modules PHP, dépendances (composer, npm)
- **Automatisation** : Ansible (playbooks, rôles, inventory), Infrastructure as Code, scripts bash, cron
- **DevOps** : Déploiement automatisé, sauvegardes, HTTPS, monitoring, maintenance

## Technologies
- **Système** : Debian 13 "Trixie", Linux administration, partitions, gestion des services
- **Virtualisation** : VirtualBox, machines virtuelles, snapshots, réseaux virtuels
- **Réseau** : kea-dhcp4-server, bind9, nftables, tcpdump, nmap, netstat
- **Sécurité** : SSH, fail2ban, nftables, authentification Apache2, certificats SSL/TLS
- **Web** : Apache2, Nginx, PHP (7.4+), phpMyAdmin
- **Bases de données** : MariaDB, MySQL
- **Automatisation** : Ansible, Bash, cron
- **Outils** : curl, git, htop, sudo, composer, symfony, node

## Ressources

### Images ISO Debian
Les images ISO Debian nécessaires pour créer les machines virtuelles **ne sont pas versionnées dans ce dépôt** (les fichiers `*.iso` sont ignorés par Git).  
Pour suivre le séminaire, téléchargez les ISO Debian officielles puis placez-les localement dans un dossier `isos/` à la racine de `seminar-devops/` :
- **debian-13.2.0-amd64-netinst.iso** : Installation réseau minimale (recommandée pour les VMs)
- **debian-13.2.0-amd64-live-kde.iso** : Live CD avec environnement KDE (pour tests rapides)

Ces ISO sont utilisées pour installer Debian sur les machines virtuelles VirtualBox créées dans les différents jours du séminaire.

## Compétences
- **Administration système Linux** : Installation, configuration, gestion des utilisateurs, services système
- **Virtualisation** : Création et gestion de machines virtuelles, réseaux virtuels, snapshots
- **Sécurité réseau** : Configuration de pare-feu (nftables), protection SSH, fail2ban, authentification
- **Services réseau** : Configuration DHCP, DNS, routage, NAT, résolution de noms
- **Déploiement web** : Configuration de serveurs web (Apache2, Nginx), déploiement d'applications, PHP
- **Bases de données** : Installation et configuration MariaDB/MySQL, gestion d'utilisateurs et droits
- **Automatisation DevOps** : Ansible (Infrastructure as Code), scripts bash, cron, sauvegardes automatiques
- **Gestion d'infrastructure** : Déploiement complet, monitoring, maintenance, bonnes pratiques DevOps
