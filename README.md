# FilmAnalytics

![Python](https://img.shields.io/badge/Python-3-3776AB) ![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9-F7931E) ![PHP](https://img.shields.io/badge/PHP-8.2-777BB4) ![MariaDB](https://img.shields.io/badge/MariaDB-10.4-003545) ![estado](https://img.shields.io/badge/estado-app_completa_(local)-brightgreen)

Plataforma web que predice si una película será un **éxito comercial antes de su estreno**, a partir de su año, presupuesto, género, país, idioma y compañía productora. El modelo se entrenó con **7,046 películas** obtenidas de un dataset de TMDB de casi un millón de registros.

Proyecto escolar — ESCOM / IPN.
1. Desarrollo de Aplicaciones para Análisis de Datos. Profesora: Sandra Luz Morales Guitrón
2. Desarrollo de Aplicaciones WEB. Profesor: Manuel Alejandro Soto Ramos

---

## Resultados en breve

| | |
|---|---|
| **Modelo** | Regresión logística (scikit-learn `Pipeline` con `OneHotEncoder`) |
| **AUC** | **≈ 0.83** en validación cruzada de 5 partes (0.85 en el conjunto de prueba) |
| **Variable más importante** | Presupuesto: por sí solo explica casi todo el poder predictivo |
| **Hallazgo** | A igual presupuesto, el terror y los documentales rinden más de lo esperado |

El análisis completo, con la comparación entre la versión original y la mejorada, está en [`notebooks/02_modelo.ipynb`](notebooks/02_modelo.ipynb).

---

## Arquitectura

```
Navegador (HTML / CSS / JS + Chart.js + Leaflet)
        │  fetch()
        ▼
API en PHP (api/*.php)
   ├── MariaDB (tabla peliculas + vistas)      ← inventario, gráficas, mapa
   └── Python: ml/predict.py + ml/modelo.pkl   ← predicciones

Scraper (Python) → data/peliculas.json        ← Top 10 de la página de inicio
```

---

## Datos

- **Fuente:** dataset completo de películas de TMDB (994,914 registros).
- **Limpieza** ([`notebooks/01_limpieza.ipynb`](notebooks/01_limpieza.ipynb)):

| Paso | Películas |
|---|---|
| Dataset original | 994,914 |
| Al menos 100 votos | 18,191 |
| Año válido (≥ 1900) | 18,177 |
| Ingreso y presupuesto > 0 | 7,070 |
| Sin TV Movie ni país nulo | 7,063 |
| Sin montos sospechosos (< $1,000) | **7,046** |

- **Variable objetivo:** éxito = ingreso mayor a la mediana (≈ $30.2 M USD). Clases balanceadas 50/50.
- **Sin data leakage:** solo se usan variables conocidas antes del estreno (se excluyen votos y popularidad).

---

## Modelo

| Modelo | Accuracy | Precision | Recall | F1 | AUC (prueba) | AUC (validación cruzada) |
|---|---|---|---|---|---|---|
| Solo presupuesto (referencia) | — | — | — | — | — | 0.822 |
| Original (`LabelEncoder`) | 0.767 | 0.796 | 0.694 | 0.741 | 0.851 | 0.827 |
| **Final (`OneHotEncoder` + Pipeline)** | 0.765 | 0.778 | 0.716 | 0.745 | 0.846 | **0.830** |

**Qué se aprendió:**
- El AUC de la primera versión se calculaba con predicciones 0/1 en lugar de probabilidades; corregido, pasó de 0.764 a 0.851 en los mismos datos.
- Cambiar a `OneHotEncoder` es lo correcto para variables sin orden, pero casi no cambió las métricas: el límite del modelo está en las variables disponibles, no en la codificación.
- El modelo final vive en un solo `Pipeline`, que incluye el preprocesamiento y maneja categorías nuevas sin errores.

---

## Requisitos

- **Python 3**
- **XAMPP** (Apache + MariaDB + PHP 8)
- Una API key gratuita de [TMDB](https://www.themoviedb.org/settings/api), solo si vas a correr el scraper

---

## Cómo correrlo

1. **Clona el repositorio** dentro de la carpeta `htdocs` de XAMPP:
   ```
   cd C:\xampp\htdocs
   git clone https://github.com/Magaly-Uribe/FilmAnalytics.git
   cd FilmAnalytics
   ```
2. **Instala las dependencias de Python:**
   ```
   pip install -r requirements.txt
   ```
3. **Crea la base de datos:** enciende Apache y MySQL en XAMPP, abre `http://localhost/phpmyadmin`, crea una base llamada `filmin` e importa `database/filmin.sql`.
4. **Configura la conexión:** copia `config/db.example.php` como `config/db.php` y ajusta usuario y contraseña si no usas los de XAMPP por defecto.
5. **Abre la página:** `http://localhost/FilmAnalytics/index.html`

---

## Qué hace cada página

- **Inicio** (`index.html`): Top 10 de las películas más taquilleras, con pósters de TMDB.
- **Inventario** (`inventario.html`): las 7,046 películas con búsqueda y filtros.
- **Gráficas** (`graficas.html`): ingresos por año y relación entre calificación e ingreso.
- **Mapa** (`mapa.html`): países con más películas exitosas.
- **Predicciones** (`predicciones.html`): ingresas los datos de una película y el modelo calcula la probabilidad de éxito.

---

## Comandos útiles

```
python ml/predict.py                                                  # prueba el modelo con un ejemplo
python ml/predict.py 2024 Documentary 2000000 Independiente Mexico es  # año, género, presupuesto, compañía, país, idioma
python scraper/scraper.py                                             # actualiza el Top 10 (requiere .env)
```

Para reentrenar el modelo, corre `notebooks/02_modelo.ipynb` de principio a fin; la última celda guarda `ml/modelo.pkl`.

---

## Solución de problemas

- **La página no carga datos al abrirla con doble clic:** necesita un servidor. Ábrela desde `http://localhost/...` con Apache encendido.
- **"No se pudo conectar a la base de datos":** revisa que MySQL esté encendido en XAMPP y que `config/db.php` exista y tenga los datos correctos.
- **La predicción tarda unos segundos:** es normal la primera vez; Python carga pandas y scikit-learn en cada predicción.
- **La predicción no funciona:** corre `python ml/predict.py` en la terminal para ver el error. En Windows el comando es `python` y en Linux, `python3`; `api/predecir.php` lo detecta solo.
- **"Falta TMDB_API_KEY":** crea el archivo `.env` (ver abajo).

---

## Estructura

```
api/            Endpoints PHP que consulta la página
components/     Clases PHP que arman las respuestas (con DTD de validación)
config/         Conexión a la base de datos (db.example.php como plantilla)
css/, assets/   Estilos e imágenes
data/           movies_clean.csv y JSON que usa la página
database/       filmin.sql: tabla, vistas y datos de MariaDB
ml/             modelo.pkl y predict.py
notebooks/      01_limpieza.ipynb y 02_modelo.ipynb
scraper/        Scraper del Top 10 + pósters de TMDB
```

---

## Configuración y secretos

Estos archivos **no se suben** a GitHub (están en `.gitignore`):

| Archivo | Cómo crearlo |
|---|---|
| `config/db.php` | Copia `config/db.example.php` y ajusta usuario y contraseña |
| `.env` | Copia `.env.example` y pon tu `TMDB_API_KEY` |
| `data/raw/` | Descarga el dataset original de TMDB aquí si quieres correr `01_limpieza.ipynb` |

---

## Estado y próximos pasos

**Funciona:** página completa en local, base de datos, scraper y predicciones con el modelo final.

**Próximos pasos:**
- Ajustar los ingresos por inflación y probar definir el éxito como retorno sobre inversión.
- Agregar variables como mes de estreno, director, reparto o si es secuela.
- Probar modelos no lineales (por ejemplo, Random Forest) con validación cruzada.
- Mostrar un mensaje de "Calculando…" mientras se genera la predicción.

---

## Equipo
- **Alexa Joaquin**: scraper, diseño de la página web y colaboración en la integración del backend.
- **Magaly Uribe**: limpieza de datos, modelo de machine learning e integración con la página.
