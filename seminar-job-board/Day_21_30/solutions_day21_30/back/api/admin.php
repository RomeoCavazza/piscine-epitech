<?php
session_start();
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
require 'config.php';

$db = new mysqli($host, $user, $pass, $dbname, $port);
if ($db->connect_error) {
    echo json_encode(['error' => 'Erreur de connexion à la base de données']);
    exit;
}
$tables = ['Users', 'Entreprises', 'Annonce', 'Candidature'];

if ($_GET['table']) {
    $table = $_GET['table'];
    if (!in_array($table, $tables)) {
        echo '{"error":"Table non autorisée"}';
        exit;
    }
    
    $data = $db->query("SELECT * FROM $table ORDER BY 1 DESC")->fetch_all(MYSQLI_ASSOC);
    echo json_encode(['data' => $data]);
}

else {
    $data = json_decode(file_get_contents('php://input'), true);
    $table = $data['table'];
    
    if (!in_array($table, $tables)) {
        echo '{"error":"Table non autorisée"}';
        exit;
    }
    
    if ($_POST || $_SERVER['REQUEST_METHOD'] === 'POST') {
        if ($table === 'Users' && $data['mot_de_passe']) {
            $data['mot_de_passe'] = password_hash($data['mot_de_passe'], PASSWORD_DEFAULT);
        }
        $cols = implode(',', array_keys($data));
        $vals = array_values($data);
        $place = str_repeat('?,', count($vals)-1) . '?';
        $stmt = $db->prepare("INSERT INTO $table ($cols) VALUES ($place)");
        $stmt->bind_param(str_repeat('s', count($vals)), ...$vals);
        echo json_encode(['success' => $stmt->execute(), 'id' => $db->insert_id]);
    }
    
    elseif ($_SERVER['REQUEST_METHOD'] === 'PUT') {
        $id = $data['id'];
        unset($data['id'], $data['table']);
        if ($table === 'Users' && $data['mot_de_passe']) {
            $data['mot_de_passe'] = password_hash($data['mot_de_passe'], PASSWORD_DEFAULT);
        }
        $set = implode('=?,', array_keys($data)) . '=?';
        $vals = array_merge(array_values($data), [$id]);
        $pk = ['Users'=>'id_user','Entreprises'=>'id_entreprise','Annonce'=>'id_annonce','Candidature'=>'id_candidature'][$table];
        $stmt = $db->prepare("UPDATE $table SET $set WHERE $pk = ?");
        $stmt->bind_param(str_repeat('s', count($vals)), ...$vals);
        echo json_encode(['success' => $stmt->execute()]);
    }
    
    elseif ($_SERVER['REQUEST_METHOD'] === 'DELETE') {
        $id = $data['id'];
        $pk = ['Users'=>'id_user','Entreprises'=>'id_entreprise','Annonce'=>'id_annonce','Candidature'=>'id_candidature'][$table];
        $stmt = $db->prepare("DELETE FROM $table WHERE $pk = ?");
        $stmt->bind_param("i", $id);
        echo json_encode(['success' => $stmt->execute()]);
    }
}

$db->close();
?>