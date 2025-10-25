<?php
session_start();
header('Content-Type: application/json');
require 'config.php';

if (!isset($_SESSION['id_user'])) {
    header('HTTP/1.1 401 Unauthorized');
    exit(json_encode(['error' => 'Vous devez être connecté pour accéder à cette page.']));
}

$userId = $_SESSION['id_user'];

$stmt = $mysqli->prepare("SELECT roles FROM Users WHERE id_user = ?");
$stmt->bind_param("i", $userId);
$stmt->execute();
$stmt->bind_result($role);
$stmt->fetch();
$stmt->close();

if ($role !== 'recruteur') {
    header('HTTP/1.1 403 Forbidden');
    exit(json_encode(['error' => 'Accès interdit : réservé aux recruteurs.']));
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $stmt = $mysqli->prepare("SELECT nom, secteur, adresse, email FROM Entreprises WHERE id_recruteur = ?");
    $stmt->bind_param("i", $userId);
    $stmt->execute();
    $result = $stmt->get_result();
    $entreprise = $result->fetch_assoc();
    $stmt->close();

    echo json_encode($entreprise ?: new stdClass());
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);

    $titre = trim($input['titre'] ?? '');
    $description = trim($input['description'] ?? '');
    $salaire = floatval($input['salaire'] ?? 0);
    $type_contrat = $input['type_contrat'] ?? '';
    $lieu = trim($input['lieu'] ?? '');
    $competence = trim($input['competence'] ?? '');

    $nom = trim($input['nom'] ?? '');
    $secteur = trim($input['secteur'] ?? '');
    $adresse = trim($input['adresse'] ?? '');
    $email = trim($input['email'] ?? '');

    if (!$nom || !$titre || !$description || !$salaire || !$type_contrat || !$lieu) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Merci de remplir tous les champs requis, y compris le nom de l\'entreprise.']);
        exit;
    }

    $stmt = $mysqli->prepare("SELECT id_entreprise FROM Entreprises WHERE id_recruteur = ?");
    $stmt->bind_param("i", $userId);
    $stmt->execute();
    $stmt->bind_result($companyId);
    $stmt->fetch();
    $stmt->close();

    if (!$companyId) {
        $stmt = $mysqli->prepare("INSERT INTO Entreprises (nom, secteur, adresse, email, id_recruteur) VALUES (?, ?, ?, ?, ?)");
        $stmt->bind_param("ssssi", $nom, $secteur, $adresse, $email, $userId);
        if (!$stmt->execute()) {
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => "Erreur lors de la création de l'entreprise."]);
            exit;
        }
        $companyId = $stmt->insert_id;
        $stmt->close();
    } else {
        $stmt = $mysqli->prepare("UPDATE Entreprises SET nom = ?, secteur = ?, adresse = ?, email = ? WHERE id_entreprise = ?");
        $stmt->bind_param("ssssi", $nom, $secteur, $adresse, $email, $companyId);
        $stmt->execute();
        $stmt->close();
    }

    $stmt = $mysqli->prepare("INSERT INTO Annonce (titre, description, salaire, type_contrat, lieu, competence, id_recruteur, id_entreprise) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("ssdsssii", $titre, $description, $salaire, $type_contrat, $lieu, $competence, $userId, $companyId);

    if ($stmt->execute()) {
        echo json_encode(['success' => true, 'message' => 'Annonce postée avec succès.']);
    } else {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => "Erreur lors de la création de l’annonce."]);
    }
    $stmt->close();
    exit;
}

http_response_code(405);
echo json_encode(['error' => 'Méthode non autorisée.']);
?>