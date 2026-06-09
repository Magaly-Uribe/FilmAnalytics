<?php
class PrediccionesXML {
    private PDO $pdo;

    public function __construct(PDO $pdo) {
        $this->pdo = $pdo;
    }

    public function obtenerPredicciones(): string {
        // Consulta desde la vista v_predicciones
        $stmt = $this->pdo->query("SELECT * FROM v_predicciones");
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // Construir XML intermedio
        $xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE predicciones SYSTEM "../components/predicciones.dtd">
            <predicciones/>',
            LIBXML_NOERROR
        );

        foreach ($rows as $row) {
            $p = $xml->addChild('pelicula');
            $p->addChild('titulo',       htmlspecialchars($row['title']));
            $p->addChild('anio',         $row['year']);
            $p->addChild('genero',       $row['genre_main']);
            $p->addChild('probabilidad', $row['probabilidad']);
            $p->addChild('etiqueta',     $row['etiqueta']);
        }

        return $xml->asXML();
    }

    public function xmlAJson(string $xmlStr): array {
        $xml  = simplexml_load_string($xmlStr);
        $data = [];

        foreach ($xml->pelicula as $p) {
            $data[] = [
                'titulo'       => (string) $p->titulo,
                'anio'         => (int)    $p->anio,
                'genero'       => (string) $p->genero,
                'probabilidad' => (float)  $p->probabilidad,
                'etiqueta'     => (string) $p->etiqueta,
            ];
        }

        // Si no hay predicciones aún devuelve estructura vacía compatible
        return [
            'proyeccion' => [],
            'tabla'      => $data
        ];
    }
}
?>
