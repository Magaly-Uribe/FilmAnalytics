import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup


URL_FUENTE = "https://www.septima-ars.com/las-10-peliculas-mas-vendidas-de-la-historia-cine/"

SELECTORES = {
    "heading_tags":    ["h2", "h3", "h4", "h5"],
    "revenue_keywords":["$", "millon", "billion", "recauda", "taquill", "dólares", "usd"],
    "img_attrs":       ["src", "data-src", "data-lazy-src", "data-original", "data-srcset"],
}

TOP_N            = 10
MAX_REINTENTOS   = 3
ESPERA_REINTENTOS= 2

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language":           "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding":           "gzip, deflate, br",
    "Referer":                   "https://www.google.com/search?q=peliculas+mas+taquilleras+historia",
    "DNT":                       "1",
    "Connection":                "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

BASE_DIR     = os.path.dirname(__file__)
OUTPUT_PATH  = os.path.join(BASE_DIR, "..", "data", "peliculas.json")
POSTERS_DIR  = os.path.join(BASE_DIR, "..", "assets", "images", "posters")


def obtener_html(url: str) -> BeautifulSoup:
    session = requests.Session()
    session.headers.update(HEADERS)

    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            print(f"  [→] Intento {intento}/{MAX_REINTENTOS} — conectando…")
            resp = session.get(url, timeout=20)

            if resp.status_code == 403:
                raise PermissionError(
                    "403 Forbidden — el sitio bloquea scrapers.\n"
                    "  Opciones:\n"
                    "  • Cambia URL_FUENTE por otro sitio\n"
                    "  • Agrega cookies reales en HEADERS\n"
                    "  • Usa Selenium: pip install selenium"
                )
            if resp.status_code == 404:
                raise FileNotFoundError("404 — verifica que URL_FUENTE sea correcta.")

            resp.raise_for_status()
            print(f"  [✓] HTML descargado — {len(resp.text):,} caracteres")
            return BeautifulSoup(resp.text, "html.parser")

        except (PermissionError, FileNotFoundError):
            raise

        except (requests.ConnectionError, requests.Timeout) as e:
            print(f"  [!] Error de red: {e}")
            if intento < MAX_REINTENTOS:
                print(f"  [→] Reintentando en {ESPERA_REINTENTOS}s…")
                time.sleep(ESPERA_REINTENTOS)
            else:
                raise ConnectionError(
                    f"Sin conexión tras {MAX_REINTENTOS} intentos.\n"
                    "  Verifica tu internet."
                )


def descargar_imagen(url_imagen: str, rank: int) -> str | None:
    """
    Descarga la imagen desde url_imagen y la guarda como
    assets/images/posters/poster_01.jpg
    Devuelve la ruta relativa para el JSON, o None si falla.
    """
    if not url_imagen:
        return None

    try:
        os.makedirs(POSTERS_DIR, exist_ok=True)
        nombre  = f"poster_{rank:02d}.jpg"
        ruta    = os.path.join(POSTERS_DIR, nombre)

        resp = requests.get(url_imagen, headers=HEADERS, timeout=15, stream=True)
        resp.raise_for_status()

        with open(ruta, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        ruta_relativa = f"assets/images/posters/{nombre}"
        print(f"    [✓] Imagen #{rank:02d} → {nombre}")
        return ruta_relativa

    except Exception as e:
        print(f"    [!] No se pudo descargar imagen #{rank}: {e}")
        return None



def extraer_imagen_url(elemento) -> str | None:
    img = elemento.find("img") if elemento else None
    if not img:
        return None
    for attr in SELECTORES["img_attrs"]:
        val = (img.get(attr) or "").strip()
        if not val:
            continue
        if "," in val:  # srcset → tomar primera URL
            val = val.split(",")[0].strip().split(" ")[0]
        if val.startswith("http"):
            return val
    return None


def limpiar_titulo(texto: str) -> str:
    return re.sub(r"^[#\s]*\d{1,2}[\s.\-\u2013\u2014:]+", "", texto).strip()


def es_heading_ranking(texto: str) -> bool:
    return bool(re.match(r"^[#\s]*\d{1,2}[\s.\-\u2013\u2014:]", texto.strip()))


def extraer_recaudacion(nodo) -> str | None:
    for _ in range(4):
        nodo = nodo.find_next_sibling()
        if not nodo:
            break
        t = nodo.get_text(strip=True)
        if any(kw in t.lower() for kw in SELECTORES["revenue_keywords"]):
            m = re.search(r"[\$\u20AC\u00A3][\d,\.]+(\s*(millones?|billion|mill\.))?", t, re.I)
            return m.group(0) if m else t[:80]
    return None


def estrategia_headings(soup: BeautifulSoup) -> list[dict]:
    contenedor = soup.find("article") or soup.find("main") or soup.body
    peliculas  = []

    for h in contenedor.find_all(SELECTORES["heading_tags"]):
        texto = h.get_text(separator=" ", strip=True)
        if not es_heading_ranking(texto):
            continue
        titulo = limpiar_titulo(texto)
        if not titulo or len(titulo) < 2:
            continue
        peliculas.append({
            "rank":        len(peliculas) + 1,
            "titulo":      titulo,
            "recaudacion": extraer_recaudacion(h),
            "imagen_url":  extraer_imagen_url(h.parent) or extraer_imagen_url(h.find_next("figure")),
        })
        if len(peliculas) >= TOP_N:
            break

    return peliculas


def estrategia_lista_ol(soup: BeautifulSoup) -> list[dict]:
    ol = soup.find("ol")
    if not ol:
        return []
    peliculas = []
    for i, li in enumerate(ol.find_all("li", recursive=False), start=1):
        titulo = limpiar_titulo(li.get_text(separator=" ", strip=True))
        if not titulo or len(titulo) < 2:
            continue
        peliculas.append({
            "rank":        i,
            "titulo":      titulo,
            "recaudacion": None,
            "imagen_url":  extraer_imagen_url(li),
        })
        if len(peliculas) >= TOP_N:
            break
    return peliculas


def estrategia_parrafos(soup: BeautifulSoup) -> list[dict]:
    patron  = re.compile(
        r"^[#\s]*(\d{1,2})[\s.\-\u2013\u2014:]+(.+?)(?:[\s\-\u2013\u2014]*(\$[\d,\.]+.*))?$",
        re.IGNORECASE,
    )
    peliculas = []
    vistos    = set()

    for tag in soup.find_all(["p", "li", "div", "span"]):
        texto = tag.get_text(separator=" ", strip=True)
        m     = patron.match(texto)
        if not m:
            continue
        rank   = int(m.group(1))
        titulo = m.group(2).strip()
        rev    = m.group(3).strip() if m.group(3) else None
        if 1 <= rank <= 10 and len(titulo) > 1 and titulo not in vistos:
            vistos.add(titulo)
            peliculas.append({
                "rank":        rank,
                "titulo":      titulo,
                "recaudacion": rev,
                "imagen_url":  extraer_imagen_url(tag),
            })

    peliculas.sort(key=lambda x: x["rank"])
    return peliculas[:TOP_N]

def scrape(url: str) -> list[dict]:
    soup = obtener_html(url)

    estrategias = [
        ("headings numerados",  estrategia_headings),
        ("lista <ol>",          estrategia_lista_ol),
        ("párrafos con patrón", estrategia_parrafos),
    ]

    for nombre, fn in estrategias:
        print(f"  [→] Estrategia: {nombre}…", end=" ")
        try:
            resultado = fn(soup)
        except Exception as e:
            print(f"error — {e}")
            continue

        if len(resultado) >= 3:
            print(f"✓  {len(resultado)} películas")
            return resultado
        else:
            print(f"✗  solo {len(resultado)}, descartada")

    raise ValueError(
        "Ninguna estrategia extrajo suficientes datos.\n"
        "  Inspecciona el HTML del sitio y ajusta SELECTORES."
    )


DATOS_MANUALES = [
    {"rank": 1,  "titulo": "Avatar",                       "recaudacion": "$2,923,706,026", "imagen": "assets/images/posters/poster_01.jpg"},
    {"rank": 2,  "titulo": "Avengers: Endgame",            "recaudacion": "$2,799,439,100", "imagen": "assets/images/posters/poster_02.jpg"},
    {"rank": 3,  "titulo": "Avatar: The Way of Water",     "recaudacion": "$2,320,250,281", "imagen": "assets/images/posters/poster_03.jpg"},
    {"rank": 4,  "titulo": "Titanic",                      "recaudacion": "$2,264,743,305", "imagen": "assets/images/posters/poster_04.jpg"},
    {"rank": 5,  "titulo": "Star Wars: The Force Awakens", "recaudacion": "$2,071,310,218", "imagen": "assets/images/posters/poster_05.jpg"},
    {"rank": 6,  "titulo": "Avengers: Infinity War",       "recaudacion": "$2,052,415,039", "imagen": "assets/images/posters/poster_06.jpg"},
    {"rank": 7,  "titulo": "Spider-Man: No Way Home",      "recaudacion": "$1,921,847,111", "imagen": "assets/images/posters/poster_07.jpg"},
    {"rank": 8,  "titulo": "Inside Out 2",                 "recaudacion": "$1,698,857,492", "imagen": "assets/images/posters/poster_08.jpg"},
    {"rank": 9,  "titulo": "Jurassic World",               "recaudacion": "$1,671,713,208", "imagen": "assets/images/posters/poster_09.jpg"},
    {"rank": 10, "titulo": "The Lion King (2019)",         "recaudacion": "$1,663,075,401", "imagen": "assets/images/posters/poster_10.jpg"},
]


def main():
    print("=" * 60)
    print("  FILMANALYTICS SCRAPER")
    print(f"  Fuente: {URL_FUENTE}")
    print("=" * 60)

    peliculas = None

    try:
        peliculas_raw = scrape(URL_FUENTE)

        print(f"\n[→] Descargando imágenes…")
        peliculas = []
        for p in peliculas_raw:
            imagen_local = descargar_imagen(p.pop("imagen_url", None), p["rank"])
            peliculas.append({
                "rank":        p["rank"],
                "titulo":      p["titulo"],
                "recaudacion": p["recaudacion"],
                "imagen":      imagen_local,
            })

    except Exception as e:
        print(f"\n[✗] Scraping falló: {e}")
        print("\n[→] Usando datos manuales para esta entrega…")
        peliculas = DATOS_MANUALES

    # Guardar JSON
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(peliculas, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] JSON → {os.path.abspath(OUTPUT_PATH)}\n")
    for p in peliculas:
        img = "✓" if p["imagen"] else "—"
        print(f"  #{p['rank']:>2}  {p['titulo']:<40} {p['recaudacion']:<20} img:{img}")
    print()


if __name__ == "__main__":
    main()