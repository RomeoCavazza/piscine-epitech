<?php
require_once __DIR__ . '/config.php';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $stmt = $mysqli->prepare("SELECT a.*, e.nom as entreprise_nom FROM Annonce a LEFT JOIN Entreprises e ON a.id_entreprise = e.id_entreprise ORDER BY a.id_annonce DESC");
    $stmt->execute();
    echo json_encode($stmt->get_result()->fetch_all(MYSQLI_ASSOC));
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $user = requireAuth();
    $data = json_decode(file_get_contents('php://input'), true);
    $stmt = $mysqli->prepare("SELECT id_entreprise FROM Entreprises WHERE id_recruteur = ?");
    $stmt->bind_param("i", $user['id']);
    $stmt->execute();
    $entreprise = $stmt->get_result()->fetch_assoc();
    if (!$entreprise) {http_response_code(403); exit(json_encode(['error' => 'Company']));}
    $stmt = $mysqli->prepare("INSERT INTO Annonce (titre, description, lieu, id_entreprise, id_recruteur) VALUES (?, ?, ?, ?, ?)");
    $stmt->bind_param("sssii", $data['titre'], $data['description'], $data['lieu'], $entreprise['id_entreprise'], $user['id']);
    echo json_encode(['success' => $stmt->execute(), 'id' => $mysqli->insert_id]);
}

$mysqli->close();