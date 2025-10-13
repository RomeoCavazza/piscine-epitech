<?php
require_once __DIR__ . '/config.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $stmt = $mysqli->prepare("SELECT id_user, prenom, nom, mot_de_passe, roles FROM Users WHERE email = ?");
    $stmt->bind_param("s", $data['email']);
    $stmt->execute();
    $user = $stmt->get_result()->fetch_assoc();

    if ($user && password_verify($data['mot_de_passe'], $user['mot_de_passe'])) {
        $_SESSION['id_user'] = $user['id_user'];
        $_SESSION['user_role'] = $user['roles'];
        $_SESSION['user_name'] = $user['prenom'] . ' ' . $user['nom'];
        echo json_encode(['success' => true, 'user' => ['id' => $user['id_user'], 'name' => $_SESSION['user_name'], 'role' => $user['roles']]]);
    } else {http_response_code(401); echo json_encode(['error' => 'Invalid']);}
} elseif ($method === 'GET') {
    echo json_encode(['logged_in' => isset($_SESSION['id_user']), 'user' => isset($_SESSION['id_user']) ? ['id' => $_SESSION['id_user'], 'name' => $_SESSION['user_name'], 'role' => $_SESSION['user_role']] : null]);
} elseif ($method === 'DELETE') {
    session_destroy(); echo json_encode(['success' => true]);
}

$mysqli->close();