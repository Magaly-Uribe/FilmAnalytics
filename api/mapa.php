<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once '../config/db.php';

try {
    $stmt = $pdo->query("SELECT * FROM v_graficas_pais LIMIT 50");
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

    $data = [];
    foreach ($rows as $row) {
        $data[] = [
            'pais'          => $row['country_main'],
            'total'         => (int)   $row['total'],
            'avg_rating'    => (float) $row['avg_rating'],
            'revenue_total' => (float) $row['revenue_total'],
        ];
    }

    echo json_encode($data);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>
