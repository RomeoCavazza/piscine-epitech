<?php
$envFile = __DIR__ . '/../.env';
if (file_exists($envFile)) {
    $lines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos($line, '=') !== false) {
            list($key, $value) = explode('=', $line, 2);
            $_ENV[trim($key)] = trim($value);
        }
    }
}

// Configuration sécurisée via variables d'environnement
$host = $_ENV['DB_HOST'] ?? 'localhost';
$port = (int)($_ENV['DB_PORT'] ?? 3306);
$dbname = $_ENV['DB_NAME'] ?? 'jobboard';
$user = $_ENV['DB_USER'] ?? 'root';
$pass = $_ENV['DB_PASS'] ?? '';

ini_set('default_socket_timeout', 30);
set_time_limit(30);

$mysqli = new mysqli($host, $user, $pass, $dbname, $port);

if ($mysqli->connect_errno) {
    http_response_code(500);
    exit('DB connection failed');
}

$mysqli->set_charset('utf8mb4');
?>
