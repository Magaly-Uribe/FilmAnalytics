<?php
class PeliculasXML {
    private PDO $pdo;

    public function __construct(PDO $pdo) {
        $this->pdo = $pdo;
    }

    public function obtenerTop10(): string {
        // Consulta las 10 películas con mayor revenue desde la vista
        $stmt = $this->pdo->query(
            "SELECT id, title, revenue FROM v_peliculas
             ORDER BY revenue DESC LIMIT 10"
        );
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // Construir XML intermedio
        $xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE peliculas SYSTEM "../components/peliculas.dtd">
            <peliculas/>',
            LIBXML_NOERROR
        );

        $rank = 1;
        foreach ($rows as $row) {
            $p = $xml->addChild('pelicula');
            $p->addChild('rank',        $rank++);
            $p->addChild('titulo',      htmlspecialchars($row['title']));
            $p->addChild('recaudacion', '$' . number_format($row['revenue'] / 1e9, 2) . 'B');
        }

        return $xml->asXML();
    }

    public function xmlAJson(string $xmlStr): array {
        $xml  = simplexml_load_string($xmlStr);
        $data = [];

        foreach ($xml->pelicula as $p) {
            $data[] = [
                'rank'        => (int)    $p->rank,
                'titulo'      => (string) $p->titulo,
                'recaudacion' => (string) $p->recaudacion,
                'imagen'      => null,
            ];
        }

        return $data;
    }
}
?>
