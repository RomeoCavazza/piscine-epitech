<?php
header('Content-Type: application/json');
require 'config.php';

if ($mysqli->connect_errno) {
    http_response_code(500);
    echo json_encode(['error' => 'Erreur de connexion à la base de données']);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $required = ['nom', 'prenom', 'email', 'message', 'id_annonce'];
    foreach ($required as $field) {
        if (empty($_POST[$field])) {
            http_response_code(400);
            echo json_encode(['error' => "Le champ $field est obligatoire"]);
            exit;
        }
    }

    $nom = $_POST['nom'];
    $prenom = $_POST['prenom'];
    $email = $_POST['email'];
    $message = $_POST['message'];
    $id_annonce = $_POST['id_annonce'];

    $upload_dir = '../uploads/';
    if (!is_dir($upload_dir)) {
        mkdir($upload_dir);
    }

    $cv_path = '';
    $lettre_path = '';

    if (isset($_FILES['cv']) && $_FILES['cv']['error'] === UPLOAD_ERR_OK) {
        $cv_path = $upload_dir . basename($_FILES['cv']['name']);
        move_uploaded_file($_FILES['cv']['tmp_name'], $cv_path);
    }

    if (isset($_FILES['Lettre-motiv']) && $_FILES['Lettre-motiv']['error'] === UPLOAD_ERR_OK) {
        $lettre_path = $upload_dir . basename($_FILES['Lettre-motiv']['name']);
        move_uploaded_file($_FILES['Lettre-motiv']['tmp_name'], $lettre_path);
    }

    $stmt = $mysqli->prepare("INSERT INTO Candidature (
        date_candidature, nom, prenom, email, message, id_annonce, cv_path, lettre_path
    ) VALUES (
        CURDATE(), ?, ?, ?, ?, ?, ?, ?
    )");

    $stmt->bind_param("ssssiss", $nom, $prenom, $email, $message, $id_annonce, $cv_path, $lettre_path);

    if ($stmt->execute()) {
        echo json_encode([
            'success' => true,
            'id' => $mysqli->insert_id,
            'cv' => $cv_path,
            'lettre' => $lettre_path
        ]);
    } else {
        http_response_code(500);
        echo json_encode([
            'error' => 'Erreur lors de la création de la candidature',
            'details' => $stmt->error
        ]);
    }

    $stmt->close();
}
?>