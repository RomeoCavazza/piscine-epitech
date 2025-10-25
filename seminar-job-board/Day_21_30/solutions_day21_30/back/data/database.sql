CREATE DATABASE IF NOT EXISTS jobboard;
USE jobboard;

CREATE TABLE Users (
    id_user INT PRIMARY KEY AUTO_INCREMENT,
    prenom VARCHAR(255) NOT NULL,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    role ENUM('candidat', 'recruteur', 'admin') DEFAULT 'candidat',
    date_naissance DATE,
    adresse VARCHAR(255),
    localisation VARCHAR(255),
    etudes VARCHAR(255),
    formation VARCHAR(500),
    telephone VARCHAR(50),
    experiences TEXT,
    competences TEXT,
    photo_profil VARCHAR(500),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actif BOOLEAN DEFAULT TRUE
);

CREATE TABLE Entreprises (
    id_entreprise INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255) NOT NULL,
    secteur VARCHAR(255),
    adresse TEXT,
    email VARCHAR(255),
    id_recruteur INT,
    FOREIGN KEY (id_recruteur) REFERENCES Users(id_user)
);

CREATE TABLE Annonce (
    id_annonce INT PRIMARY KEY AUTO_INCREMENT,
    titre VARCHAR(150) NOT NULL,
    description TEXT,
    lieu VARCHAR(100),
    type_contrat ENUM('CDI', 'CDD', 'ALTERNANCE', 'STAGE'),
    id_entreprise INT,
    id_recruteur INT,
    salaire DECIMAL(10,2),
    competence TEXT,
    statut ENUM('En cours', 'En attente', 'Clôturée') DEFAULT 'En cours',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_entreprise) REFERENCES Entreprises(id_entreprise),
    FOREIGN KEY (id_recruteur) REFERENCES Users(id_user)
);

CREATE TABLE Candidature (
    id_candidature INT PRIMARY KEY AUTO_INCREMENT,
    date_candidature DATE NOT NULL,
    id_candidat INT,
    id_entreprise INT,
    id_annonce INT,
    statut ENUM('En attente', 'Acceptée', 'Refusée') DEFAULT 'En attente',
    message TEXT,
    FOREIGN KEY (id_candidat) REFERENCES Users(id_user),
    FOREIGN KEY (id_entreprise) REFERENCES Entreprises(id_entreprise),
    FOREIGN KEY (id_annonce) REFERENCES Annonce(id_annonce)
);

CREATE VIEW vue_candidatures_detaillees AS
SELECT
    c.id_candidature,
    c.date_candidature,
    u.nom AS nom_candidat,
    e.nom AS nom_entreprise,
    a.titre AS titre_annonce,
    c.statut,
    c.message
FROM Candidature c
JOIN Users u ON c.id_candidat = u.id_user
JOIN Entreprises e ON c.id_entreprise = e.id_entreprise
JOIN Annonce a ON c.id_annonce = a.id_annonce; 

CREATE OR REPLACE VIEW vue_entreprises_recruteurs AS
    SELECT
        e.id_entreprise,
        e.nom AS nom_entreprise,
        e.secteur,
        e.adresse,
        e.email AS email_entreprise,
        CONCAT(u.prenom, ' ', u.nom) AS nom_recruteur
FROM Entreprises e
LEFT JOIN Users u ON e.id_recruteur = u.id_user;