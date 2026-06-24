<?php
$host     = 'mysql.railway.internal';
$port     = '3306';
$dbname   = 'railway';
$user     = 'root';
$password = 'XeqtRfCJkZgjAHTiYoCUKRKfuGGBpUTN';

try {
    $pdo = new PDO(
        "mysql:host=$host;port=$port;dbname=$dbname;charset=utf8mb4",
        $user,
        $password
    );
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
    exit;
}
?>
