<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once '../config/db.php';

try{
        $stmt = $pdo->query(
                "SELECT DISTINCT company_main
                FROM peliculas
                WHERE company_main != 'Independiente'
                ORDER BY company_main ASC"
        );
        $companias = $stmt->fetchAll(PDO::FETCH_COLUMN);

        //Agregar Independiente al final
        $companias[] = 'Independiente';

        echo json_encode($companias);
} catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['error' => $e->getMessage()]);
}
