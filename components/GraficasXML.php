<?php
class GraficasXML {
    private PDO $pdo;

    public function __construct(PDO $pdo) {
        $this->pdo = $pdo;
    }

    public function obtenerGraficas(): string {
        // Consulta vista de dispersión (películas individuales)
        $stmtDisp = $this->pdo->query(
            "SELECT title, vote_average, revenue FROM v_peliculas
             ORDER BY revenue DESC LIMIT 100"
        );
        $dispersion = $stmtDisp->fetchAll(PDO::FETCH_ASSOC);

        // Consulta vista de tendencia por año
        $stmtTend = $this->pdo->query(
            "SELECT year, revenue_total FROM v_graficas_anio"
        );
        $tendencia = $stmtTend->fetchAll(PDO::FETCH_ASSOC);

        // Construir XML intermedio
        $xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE graficas SYSTEM "../components/graficas.dtd">
            <graficas/>',
            LIBXML_NOERROR
        );

        // Sección dispersión
        $dispNode = $xml->addChild('dispersion');
        foreach ($dispersion as $row) {
            $p = $dispNode->addChild('pelicula');
            $p->addChild('titulo',      htmlspecialchars($row['title']));
            $p->addChild('imdb',        $row['vote_average']);
            $p->addChild('recaudacion', round($row['revenue'] / 1e6, 2));
        }

        // Sección tendencia
        $tendNode = $xml->addChild('tendencia');
        foreach ($tendencia as $row) {
            $pt = $tendNode->addChild('punto');
            $pt->addChild('anio',     $row['year']);
            $pt->addChild('ingresos', round($row['revenue_total'] / 1e9, 2));
        }

        return $xml->asXML();
    }

    public function xmlAJson(string $xmlStr): array {
        $xml = simplexml_load_string($xmlStr);

        $dispersion = [];
        foreach ($xml->dispersion->pelicula as $p) {
            $dispersion[] = [
                'titulo'      => (string) $p->titulo,
                'imdb'        => (float)  $p->imdb,
                'recaudacion' => (float)  $p->recaudacion,
            ];
        }

        $tendencia = [];
        foreach ($xml->tendencia->punto as $pt) {
            $tendencia[] = [
                'anio'     => (int)   $pt->anio,
                'ingresos' => (float) $pt->ingresos,
            ];
        }

        return [
            'dispersion' => $dispersion,
            'tendencia'  => $tendencia,
        ];
    }
}
?>
