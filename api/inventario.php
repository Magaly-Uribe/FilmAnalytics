<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once '../config/db.php';
require_once '../components/InventarioXML.php';

try {
    // 1. Crear objeto que consulta la vista y genera XML
    $inventario = new InventarioXML($pdo);

    // 2. Obtener XML intermedio desde la vista v_inventario
    $xmlStr = $inventario->obtenerPeliculas();

    // 3. Convertir XML a array y responder JSON al frontend
    $data = $inventario->xmlAJson($xmlStr);

    echo json_encode($data);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>
