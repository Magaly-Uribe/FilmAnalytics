<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

require_once '../config/db.php';
require_once '../components/InventarioXML.php';

// Recibir parámetros de filtro
$titulo  = $_GET['titulo']  ?? '';
$genero  = $_GET['genero']  ?? '';
$pais    = $_GET['pais']    ?? '';
$anio    = $_GET['anio']    ?? '';
$cal_min = $_GET['cal_min'] ?? 0;
$gan_min = $_GET['gan_min'] ?? 0;

try {
    // Construir query dinámico con filtros
    $sql    = "SELECT * FROM v_inventario WHERE 1=1";
    $params = [];

    if ($titulo) {
        $sql .= " AND title LIKE :titulo";
        $params[':titulo'] = '%' . $titulo . '%';
    }
    if ($genero) {
        $sql .= " AND genre_main = :genero";
        $params[':genero'] = $genero;
    }
    if ($pais) {
        $sql .= " AND country_main = :pais";
        $params[':pais'] = $pais;
    }
    if ($anio) {
        $sql .= " AND year = :anio";
        $params[':anio'] = (int)$anio;
    }
    if ($cal_min > 0) {
        $sql .= " AND vote_average >= :cal_min";
        $params[':cal_min'] = (float)$cal_min;
    }
    if ($gan_min > 0) {
        $sql .= " AND revenue >= :gan_min";
        $params[':gan_min'] = (int)$gan_min;
    }

    $sql .= " LIMIT 200";

    $stmt = $pdo->prepare($sql);
    $stmt->execute($params);
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // XML intermedio
    $xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?><peliculas/>', LIBXML_NOERROR);
    foreach ($rows as $row) {
        $p = $xml->addChild('pelicula');
        $p->addChild('id',           $row['id']);
        $p->addChild('titulo',       htmlspecialchars($row['title']));
        $p->addChild('anio',         $row['year']);
        $p->addChild('popularidad',  $row['popularity_log']);
        $p->addChild('calificacion', $row['vote_average']);
        $p->addChild('genero',       $row['genre_main']);
        $p->addChild('pais',         $row['country_main']);
        $p->addChild('ganancias',    $row['revenue']);
    }

    // Convertir XML a JSON
    $data = [];
    foreach ($xml->pelicula as $p) {
        $data[] = [
            'id'          => (int)    $p->id,
            'titulo'      => (string) $p->titulo,
            'anio'        => (int)    $p->anio,
            'popularidad' => (float)  $p->popularidad,
            'calificacion'=> (float)  $p->calificacion,
            'genero'      => (string) $p->genero,
            'pais'        => (string) $p->pais,
            'ganancias'   => (int)    $p->ganancias,
        ];
    }

    echo json_encode($data);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>
