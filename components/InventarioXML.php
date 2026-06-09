<?php
class InventarioXML {
    private PDO $pdo;

    public function __construct(PDO $pdo) {
        $this->pdo = $pdo;
    }

    public function obtenerPeliculas(): string {
        // Consulta SIEMPRE desde la vista, nunca desde la tabla directa
        $stmt = $this->pdo->query("SELECT * FROM v_inventario");
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // Construir XML intermedio
        $xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE peliculas SYSTEM "../components/inventario.dtd">
            <peliculas/>',
            LIBXML_NOERROR
        );

        foreach ($rows as $row) {
            $pelicula = $xml->addChild('pelicula');
            $pelicula->addChild('id',          $row['id']);
            $pelicula->addChild('titulo',       htmlspecialchars($row['title']));
            $pelicula->addChild('anio',         $row['year']);
            $pelicula->addChild('popularidad',  $row['popularity_log']);
            $pelicula->addChild('calificacion', $row['vote_average']);
            $pelicula->addChild('genero',       $row['genre_main']);
            $pelicula->addChild('pais',         $row['country_main']);
            $pelicula->addChild('ganancias',    $row['revenue']);
        }

        return $xml->asXML();
    }

    public function xmlAJson(string $xmlStr): array {
        // Parsear XML y convertir a array para responder JSON al frontend
        $xml  = simplexml_load_string($xmlStr);
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

        return $data;
    }
}
?>
