<?php
session_start();
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
require 'config.php';

if ($mysqli->connect_errno) {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Erreur de connexion à la base de données']);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);

    $role = $data['role'] ?? '';
    $prenom = $data['prenom'] ?? '';
    $nom = $data['nom'] ?? '';
    $email = $data['email'] ?? '';
    $adresse = $data['adresse'] ?? '';
    $etudes = $data['etudes'] ?? '';
    $telephone = $data['telephone'] ?? '';
    $mot_de_passe = password_hash($data['mot_de_passe'] ?? '', PASSWORD_DEFAULT);
    $nom_entreprise = ($role === 'recruteur') ? ($data['nom_entreprise'] ?? null) : null;
    
    if (empty($role) || empty($prenom) || empty($nom) || empty($email) || empty($data['mot_de_passe'])) {
        echo json_encode(["status" => "error", "message" => "Tous les champs obligatoires doivent être remplis"]);
        exit();
    }

    $check = $mysqli->prepare("SELECT prenom, nom FROM Users WHERE email = ?");
    $check->bind_param("s", $email);
    $check->execute();
    $check->store_result();

    if ($check->num_rows > 0) {
        $check->bind_result($existingPrenom, $existingNom);
        $check->fetch();
        echo json_encode([
            "status" => "exists",
            "message" => "Vous êtes déjà inscrit : $existingPrenom $existingNom"
        ]);
        $check->close();
        $mysqli->close();
        exit();
    }
    $check->close();

    $stmt = $mysqli->prepare("INSERT INTO Users (role, prenom, nom, email, mot_de_passe, adresse, etudes, telephone) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("ssssssss", $role, $prenom, $nom, $email, $mot_de_passe, $adresse, $etudes, $telephone);

    if (!$stmt->execute()) {
        echo json_encode(["status" => "error", "message" => "Erreur lors de l'enregistrement : " . $stmt->error]);
        $stmt->close();
        $mysqli->close();
        exit();
    }

    $user_id = $stmt->insert_id;
    $stmt->close();

    $_SESSION['id_user'] = $user_id;
    $_SESSION['user_role'] = $role;
    $_SESSION['user_name'] = $prenom . ' ' . $nom;
    $_SESSION['user_email'] = $email;

    if ($role === 'recruteur' && $nom_entreprise) {
        $stmt = $mysqli->prepare("INSERT INTO Entreprises (nom, id_recruteur) VALUES (?, ?)");
        $stmt->bind_param("si", $nom_entreprise, $user_id);
        if (!$stmt->execute()) {
            echo json_encode(["status" => "error", "message" => "Erreur lors de l'ajout de l'entreprise : " . $stmt->error]);
            $stmt->close();
            $mysqli->close();
            exit();
        }
        $stmt->close();
    }

    if ($role === 'recruteur') {
        $stmt = $mysqli->prepare("SELECT id_entreprise FROM Entreprises WHERE id_recruteur = ?");
        $stmt->bind_param("i", $user_id);
        $stmt->execute();
        $result = $stmt->get_result()->fetch_assoc();
        $_SESSION['id_entreprise'] = $result['id_entreprise'] ?? null;
        $stmt->close();
    }

    $mysqli->close();

    $redirect = '/front/web/index.html'; 
    if ($role === 'recruteur') {
        $redirect = '/front/web/recruteur.html'; 
    } elseif ($role === 'admin') {
        $redirect = '/front/web/admin.html'; 
    }

    echo json_encode([
        "status" => "ok",
        "message" => "Inscription réussie",
        "redirect" => $redirect
    ]);
    exit();
}

else {
    http_response_code(405);
    echo json_encode(['status' => 'error', 'message' => 'Méthode non autorisée']);
    exit();
}
?>