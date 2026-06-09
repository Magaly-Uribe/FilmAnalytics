<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once '../config/db.php';
require_once '../components/PeliculasXML.php';

try {
    $peliculas = new PeliculasXML($pdo);
    $xmlStr    = $peliculas->obtenerTop10();
    $data      = $peliculas->xmlAJson($xmlStr);

    echo json_encode($data);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>
