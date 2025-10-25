<?php 
session_start();
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
require 'config.php';

// Utiliser la connexion existante de config.php
if ($mysqli->connect_errno) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Erreur de connexion à la base de données']);
    exit();
}

// GET : toutes les annonces ou seulement celles du recruteur connecté
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (isset($_SESSION['id_user']) && $_SESSION['user_role'] === 'recruteur') {
        // Recruteur connecté : récupérer ses annonces
        $stmt = $mysqli->prepare("
            SELECT a.*, e.nom as entreprise_nom 
            FROM Annonce a 
            LEFT JOIN Entreprises e ON a.id_entreprise = e.id_entreprise 
            WHERE a.id_recruteur = ?
            ORDER BY a.id_annonce DESC
        ");
        $stmt->bind_param("i", $_SESSION['id_user']);
    } else {
        // Visiteur ou candidat : voir toutes les annonces
        $stmt = $mysqli->prepare("
            SELECT a.*, e.nom as entreprise_nom 
            FROM Annonce a 
            LEFT JOIN Entreprises e ON a.id_entreprise = e.id_entreprise 
            ORDER BY a.id_annonce DESC
        ");
    }

    $stmt->execute();
    $result = $stmt->get_result()->fetch_all(MYSQLI_ASSOC);
    echo json_encode($result);

    $stmt->close();
    $mysqli->close();
    exit();
}

// POST : création d'une nouvelle annonce par un recruteur
elseif ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_SESSION['id_user']) && $_SESSION['user_role'] === 'recruteur') {
    $data = json_decode(file_get_contents('php://input'), true);

    $required = ['titre', 'description', 'lieu', 'type_contrat', 'adresse'];
    foreach ($required as $field) {
        if (empty($data[$field])) {
            echo json_encode(['success' => false, 'message' => "Le champ '$field' est requis."]);
            exit();
        }
    }

    // Récupération de l'entreprise liée au recruteur
    $stmt = $mysqli->prepare("SELECT id_entreprise FROM Entreprises WHERE id_recruteur = ?");
    $stmt->bind_param("i", $_SESSION['id_user']);
    $stmt->execute();
    $entreprise = $stmt->get_result()->fetch_assoc();
    $stmt->close();

    if (!$entreprise) {
        echo json_encode(['success' => false, 'message' => 'Aucune entreprise liée à ce recruteur.']);
        exit();
    }

    // Données à insérer
    $titre = $data['titre'];
    $description = $data['description'];
    $lieu = $data['lieu'];
    $salaire = isset($data['salaire']) && is_numeric($data['salaire']) ? $data['salaire'] : null;
    $type_contrat = $data['type_contrat'];
    $adresse = $data['adresse'];
    $id_entreprise = $entreprise['id_entreprise'];
    $id_recruteur = $_SESSION['id_user'];

    // Insertion
    $stmt = $mysqli->prepare("
        INSERT INTO Annonce (titre, description, lieu, salaire, type_contrat, adresse, id_entreprise, id_recruteur) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ");
    $stmt->bind_param("sssdsiis", $titre, $description, $lieu, $salaire, $type_contrat, $adresse, $id_entreprise, $id_recruteur);

    if ($stmt->execute()) {
        echo json_encode(['success' => true, 'id' => $stmt->insert_id, 'message' => 'Annonce créée avec succès']);
    } else {
        echo json_encode(['success' => false, 'message' => 'Erreur lors de la création : ' . $stmt->error]);
    }

    $stmt->close();
    $mysqli->close();
    exit();
}

// PUT : modification d'une annonce
elseif ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $data = json_decode(file_get_contents('php://input'), true);
    $stmt = $mysqli->prepare("UPDATE Annonce SET titre=?, description=? WHERE id_annonce=? AND id_recruteur=?");
    $stmt->bind_param("ssii", $data['titre'], $data['description'], $data['id'], $_SESSION['id_user']);
    echo json_encode(['success' => $stmt->execute()]);
}

// DELETE : suppression d'une annonce (recruteur uniquement)
elseif ($_SERVER['REQUEST_METHOD'] === 'DELETE' && isset($_SESSION['id_user']) && $_SESSION['user_role'] === 'recruteur') {
    parse_str(file_get_contents("php://input"), $deleteData);
    $id_annonce = $deleteData['id'] ?? null;

    if (!$id_annonce) {
        echo json_encode(['success' => false, 'message' => 'ID de l\'annonce manquant.']);
        exit();
    }

    // Vérification que l'annonce appartient au recruteur connecté
    $stmt = $mysqli->prepare("SELECT id_recruteur FROM Annonce WHERE id_annonce = ?");
    $stmt->bind_param("i", $id_annonce);
    $stmt->execute();
    $result = $stmt->get_result()->fetch_assoc();
    $stmt->close();

    if (!$result || $result['id_recruteur'] != $_SESSION['id_user']) {
        echo json_encode(['success' => false, 'message' => 'Vous ne pouvez pas supprimer cette annonce.']);
        exit();
    }

    // Suppression
    $stmt = $mysqli->prepare("DELETE FROM Annonce WHERE id_annonce = ?");
    $stmt->bind_param("i", $id_annonce);

    if ($stmt->execute()) {
        echo json_encode(['success' => true, 'message' => 'Annonce supprimée avec succès.']);
    } else {
        echo json_encode(['success' => false, 'message' => 'Erreur lors de la suppression : ' . $stmt->error]);
    }

    $stmt->close();
    $mysqli->close();
    exit();
}

// Méthode non autorisée
else {
    echo json_encode(['success' => false, 'message' => 'Méthode non autorisée ou utilisateur non connecté.']);
    $mysqli->close();
    exit();
}
