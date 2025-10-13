<?php
require_once __DIR__ . '/config.php';

$method = $_SERVER['REQUEST_METHOD'];
$data = json_decode(file_get_contents('php://input'), true);

if ($method === 'POST' && isset($data['email'])) {
    $check = $mysqli->prepare("SELECT id_user FROM Users WHERE email = ?");
    $check->bind_param("s", $data['email']);
    $check->execute();
    if ($check->get_result()->num_rows > 0) {http_response_code(409); exit(json_encode(['error' => 'Exists']));}

    $hash = password_hash($data['mot_de_passe'], PASSWORD_DEFAULT);
    $prenom = $data['prenom'] ?? 'À compléter';
    $nom = $data['nom'] ?? 'À compléter';
    $roles = $data['roles'] ?? 'candidat';
    $date_naissance = $data['date_naissance'] ?? null;
    $adresse = $data['adresse'] ?? '';
    $etudes = $data['etudes'] ?? '';
    $telephone = $data['telephone'] ?? '';
    
    $stmt = $mysqli->prepare("INSERT INTO Users (roles, prenom, nom, email, mot_de_passe, date_naissance, adresse, etudes, telephone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("sssssssss", $roles, $prenom, $nom, $data['email'], $hash, $date_naissance, $adresse, $etudes, $telephone);

    if ($stmt->execute()) {
        $_SESSION['id_user'] = $mysqli->insert_id;
        $_SESSION['user_role'] = $roles;
        $_SESSION['user_name'] = "$prenom $nom";
        echo json_encode(['success' => true, 'user' => ['id' => $mysqli->insert_id, 'name' => "$prenom $nom", 'role' => $roles]]);
    } else {http_response_code(500); echo json_encode(['error' => 'Error']);}
} elseif ($method === 'GET') {
    $user = requireAuth();
    $stmt = $mysqli->prepare("SELECT * FROM Users WHERE id_user = ?");
    $stmt->bind_param("i", $user['id']);
    $stmt->execute();
    $user_data = $stmt->get_result()->fetch_assoc();
    $response = ['success' => true, 'user' => $user_data];

    if ($user['role'] === 'recruteur') {
        $stmt = $mysqli->prepare("SELECT * FROM Entreprises WHERE id_recruteur = ?");
        $stmt->bind_param("i", $user['id']);
        $stmt->execute();
        $response['company'] = $stmt->get_result()->fetch_assoc();
    }
    echo json_encode($response);
} elseif ($method === 'POST' && !isset($data['email'])) {
    $user = requireAuth();

    if (isset($data['nom_entreprise'])) {
        $stmt = $mysqli->prepare("SELECT id_entreprise FROM Entreprises WHERE id_recruteur = ?");
        $stmt->bind_param("i", $user['id']);
        $stmt->execute();
        $existing = $stmt->get_result()->fetch_assoc();

        $nom = $data['nom_entreprise'];
        $secteur = $data['secteur'] ?? '';
        $adresse = $data['adresse_entreprise'] ?? '';
        $email = $data['email_entreprise'] ?? '';

        if ($existing) {
            $stmt = $mysqli->prepare("UPDATE Entreprises SET nom = ?, secteur = ?, adresse = ?, email = ? WHERE id_entreprise = ?");
            $stmt->bind_param("ssssi", $nom, $secteur, $adresse, $email, $existing['id_entreprise']);
        } else {
            $stmt = $mysqli->prepare("INSERT INTO Entreprises (nom, secteur, adresse, email, id_recruteur) VALUES (?, ?, ?, ?, ?)");
            $stmt->bind_param("ssssi", $nom, $secteur, $adresse, $email, $user['id']);
        }
        echo json_encode(['success' => $stmt->execute()]);
    } else {
        $prenom = $data['prenom'] ?? '';
        $nom = $data['nom'] ?? '';
        $adresse = $data['adresse'] ?? '';
        $etudes = $data['etudes'] ?? '';
        $telephone = $data['telephone'] ?? '';
        $stmt = $mysqli->prepare("UPDATE Users SET prenom = ?, nom = ?, adresse = ?, etudes = ?, telephone = ? WHERE id_user = ?");
        $stmt->bind_param("sssssi", $prenom, $nom, $adresse, $etudes, $telephone, $user['id']);
        echo json_encode(['success' => $stmt->execute()]);
    }
}

$mysqli->close();