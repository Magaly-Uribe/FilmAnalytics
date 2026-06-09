<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

require_once '../config/db.php';

$input   = json_decode(file_get_contents('php://input'), true);
$titulo  = $input['titulo']  ?? '';
$anio    = (int)($input['anio']   ?? 2024);
$genero  = $input['genero']  ?? 'Drama';
$budget  = (int)($input['budget'] ?? 0);
$company = $input['company'] ?? 'Independiente';

try {
    $cmd    = "python3 '/var/www/html/webapp/Proyecto filmin/ml/predict.py'" .
              " '$anio' '$genero' '$budget' '$company' 2>&1";
    $output = shell_exec($cmd);
    $lines  = array_values(array_filter(explode("\n", trim($output))));

    $etiqueta  = 'no exitosa';
    $confianza = 0;
    foreach ($lines as $line) {
        if (str_contains($line, 'Etiqueta:'))  $etiqueta  = trim(str_replace('Etiqueta:', '', $line));
        if (str_contains($line, 'Confianza:')) $confianza = (float) filter_var($line, FILTER_SANITIZE_NUMBER_FLOAT, FILTER_FLAG_ALLOW_FRACTION);
    }

    $stmt = $pdo->prepare("SELECT AVG(revenue) as avg_revenue FROM peliculas WHERE genre_main = :genero");
    $stmt->execute([':genero' => $genero]);
    $avg = $stmt->fetchColumn() ?? 50000000;

    $factores = [0.35, 0.20, 0.12, 0.08, 0.06, 0.05, 0.04, 0.03, 0.03, 0.02, 0.01, 0.01];
    $curva    = [];
    $avgM     = round($avg / 1e6, 2);
    $modeloM  = round(($avg * ($confianza / 100)) / 1e6, 2);

    for ($i = 0; $i < 12; $i++) {
        $curva[] = [
            'semana'    => 'S' . ($i + 1),
            'historico' => round($avgM   * $factores[$i], 2),
            'modelo'    => round($modeloM * $factores[$i], 2),
        ];
    }

    echo json_encode([
        'titulo'    => $titulo,
        'anio'      => $anio,
        'genero'    => $genero,
        'etiqueta'  => trim($etiqueta),
        'confianza' => $confianza,
        'curva'     => $curva
    ]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>
