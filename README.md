---

## Requisitos

- Python 3.x
- Navegador moderno (Chrome, Firefox, Edge)

---

## Cómo ejecutarlo

**1. Instalar dependencias del scraper:**
```
pip install requests beautifulsoup4
```

**2. Correr el scraper** *(componente DAAD — genera peliculas.json)*:
```
cd filmin/
python scraper/scraper.py
```

**3. Levantar servidor local:**
```
python -m http.server 8080
```

Abrir en el navegador: `http://localhost:8080`

> Los archivos HTML no funcionan abriéndolos directamente desde el explorador de archivos — necesitan un servidor local porque usan `fetch()` para cargar los JSON.

---

## Nota sobre las proyecciones

Los datos de predicciones (`data/predicciones.json`) son ilustrativos para esta primera entrega. En entregas posteriores se conectarán con la base de datos.