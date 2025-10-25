<?php
ini_set('session.cookie_httponly', 1);
ini_set('session.use_only_cookies', 1);
ini_set('session.cookie_secure', 0);
ini_set('session.cookie_samesite', 'Lax');
session_start();

header('Content-Type: application/json');
header('Access-Control-Allow-Credentials: true');
require 'config.php';

// Utiliser la connexion existante de config.php
if ($mysqli->connect_errno) {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Erreur de connexion à la base de données']);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $email = $data['email'] ?? '';
    $password = $data['mot_de_passe'] ?? '';

    $stmt = $mysqli->prepare("SELECT id_user, prenom, nom, email, adresse, etudes, formation, telephone, experiences, competences, mot_de_passe, role FROM Users WHERE email = ?");
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $user = $stmt->get_result()->fetch_assoc();
    $stmt->close();

    if ($user && password_verify($password, $user['mot_de_passe'])) {
        $_SESSION['id_user'] = $user['id_user'];
        $_SESSION['user_role'] = $user['role'];
        $_SESSION['user_name'] = $user['prenom'] . ' ' . $user['nom'];
        $_SESSION['user_email'] = $user['email'];

        // Si recruteur, on récupère l'id_entreprise liée
        if ($user['role'] === 'recruteur') {
            $stmt = $mysqli->prepare("SELECT id_entreprise FROM Entreprises WHERE id_recruteur = ?");
            $stmt->bind_param("i", $user['id_user']);
            $stmt->execute();
            $result = $stmt->get_result()->fetch_assoc();
            $_SESSION['id_entreprise'] = $result['id_entreprise'] ?? null;
            $stmt->close();
        }

        // Définir la redirection selon le rôle
        $redirect = '/front/index.html';  // par défaut, page normale

        if ($user['role'] === 'recruteur') {
            $redirect = '/front/recruteur.html';  // page avec formulaire pour recruteur
        } elseif ($user['role'] === 'candidat') {
            $redirect = '/front/candidat.html';  // page candidat si besoin
        } elseif ($user['role'] === 'admin') {
            $redirect = '/front/admin.html';  // page admin
        }

        echo json_encode([
            'status' => 'ok',
            'user' => [
                'id' => $user['id_user'],
                'prenom' => $user['prenom'],
                'nom' => $user['nom'],
                'email' => $user['email'],
                'adresse' => $user['adresse'],
                'etudes' => $user['etudes'],
                'formation' => $user['formation'],
                'telephone' => $user['telephone'],
                'experiences' => $user['experiences'],
                'competences' => $user['competences'],
                'role' => $user['role'],
                'entreprise' => $_SESSION['id_entreprise'] ?? null
            ],
            'redirect' => $redirect
        ]);
    } else {
        http_response_code(401);
        echo json_encode(['status' => 'error', 'message' => "Email ou mot de passe incorrect."]);
    }
}

elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (isset($_SESSION['id_user'])) {
        $stmt = $mysqli->prepare("SELECT adresse, etudes, formation, telephone, experiences, competences, photo_profil FROM Users WHERE id_user = ?");
        $stmt->bind_param("i", $_SESSION['id_user']);
        $stmt->execute();
        $details = $stmt->get_result()->fetch_assoc();
        
        echo json_encode([
            'logged_in' => true,
            'user' => [
                'id' => $_SESSION['id_user'],
                'name' => $_SESSION['user_name'],
                'role' => $_SESSION['user_role'],
                'email' => $_SESSION['user_email'],
                'adresse' => $details['adresse'] ?? null,
                'etudes' => $details['etudes'] ?? null,
                'formation' => $details['formation'] ?? null,
                'telephone' => $details['telephone'] ?? null,
                'experiences' => $details['experiences'] ?? null,
                'competences' => $details['competences'] ?? null,
                'photo_profil' => $details['photo_profil'] ?? null
            ]
        ]);
    } else {
        echo json_encode(['logged_in' => false, 'user' => null]);
    }
}

elseif ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    if (!isset($_SESSION['id_user'])) {
        http_response_code(403);
        echo json_encode(['success' => false, 'message' => 'Non connecté']);
        exit();
    }

    $data = json_decode(file_get_contents('php://input'), true);
    $prenom = $data['prenom'] ?? '';
    $nom = $data['nom'] ?? '';
    $email = $data['email'] ?? '';
    $adresse = $data['adresse'] ?? '';
    $etudes = $data['etudes'] ?? '';
    $formation = $data['formation'] ?? '';
    $telephone = $data['telephone'] ?? '';
    $experiences = $data['experiences'] ?? '';
    $competences = $data['competences'] ?? '';
    $photo_profil = $data['photo_profil'] ?? '';
    $mot_de_passe = $data['mot_de_passe'] ?? '';

    if ($mot_de_passe) {
        $mot_de_passe_hash = password_hash($mot_de_passe, PASSWORD_DEFAULT);
        $stmt = $mysqli->prepare("UPDATE Users SET prenom = ?, nom = ?, email = ?, adresse = ?, etudes = ?, formation = ?, telephone = ?, experiences = ?, competences = ?, photo_profil = ?, mot_de_passe = ? WHERE id_user = ?");
        $stmt->bind_param("sssssssssssi", $prenom, $nom, $email, $adresse, $etudes, $formation, $telephone, $experiences, $competences, $photo_profil, $mot_de_passe_hash, $_SESSION['id_user']);
    } else {
        $stmt = $mysqli->prepare("UPDATE Users SET prenom = ?, nom = ?, email = ?, adresse = ?, etudes = ?, formation = ?, telephone = ?, experiences = ?, competences = ?, photo_profil = ? WHERE id_user = ?");
        $stmt->bind_param("ssssssssssi", $prenom, $nom, $email, $adresse, $etudes, $formation, $telephone, $experiences, $competences, $photo_profil, $_SESSION['id_user']);
    }

    if ($stmt->execute()) {
        echo json_encode(['success' => true]);
    } else {
        echo json_encode(['success' => false, 'message' => 'Erreur lors de la mise à jour']);
    }
    $stmt->close();
}

elseif ($_SERVER['REQUEST_METHOD'] === 'DELETE') {
    session_destroy();
    echo json_encode(['success' => true]);
}

$mysqli->close();
exit();
?>
