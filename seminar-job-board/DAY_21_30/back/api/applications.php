<?php
require_once __DIR__ . '/config.php';

$user = requireAuth();

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $sql = $user['role'] === 'candidat' 
        ? "SELECT c.*, a.titre, e.nom AS entreprise_nom FROM Candidature c JOIN Annonce a ON c.id_annonce = a.id_annonce JOIN Entreprises e ON c.id_entreprise = e.id_entreprise WHERE c.id_candidat = ?"
        : "SELECT c.*, a.titre, u.prenom, u.nom FROM Candidature c JOIN Annonce a ON c.id_annonce = a.id_annonce JOIN Users u ON c.id_candidat = u.id_user WHERE a.id_recruteur = ?";
    $stmt = $mysqli->prepare($sql);
    $stmt->bind_param("i", $user['id']);
    $stmt->execute();
    echo json_encode($stmt->get_result()->fetch_all(MYSQLI_ASSOC));
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST' && $user['role'] === 'candidat') {
    $data = json_decode(file_get_contents('php://input'), true);
    $stmt = $mysqli->prepare("SELECT id_entreprise FROM Annonce WHERE id_annonce = ?");
    $stmt->bind_param("i", $data['id_annonce']);
    $stmt->execute();
    $annonce = $stmt->get_result()->fetch_assoc();
    if (!$annonce) {http_response_code(404); exit(json_encode(['error' => 'Not found']));}
    $stmt = $mysqli->prepare("INSERT INTO Candidature (date_candidature, id_candidat, id_entreprise, id_annonce, statut) VALUES (CURDATE(), ?, ?, ?, 'En attente')");
    $stmt->bind_param("iii", $user['id'], $annonce['id_entreprise'], $data['id_annonce']);
    echo json_encode(['success' => $stmt->execute(), 'id' => $mysqli->insert_id]);
}

$mysqli->close();