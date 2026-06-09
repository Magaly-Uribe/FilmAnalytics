import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup


URL_FUENTE   = "https://www.septima-ars.com/las-10-peliculas-mas-vendidas-de-la-historia-cine/"
TMDB_API_KEY = "279a4064cfda5f11563c96f2aeb0a7d2"

TOP_N             = 10
MAX_REINTENTOS    = 3
ESPERA_REINTENTOS = 2

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

EMOJI_A_NUM = {
    "\u0031\ufe0f\u20e3": 1,
    "\u0032\ufe0f\u20e3": 2,
    "\u0033\ufe0f\u20e3": 3,
    "\u0034\ufe0f\u20e3": 4,
    "\u0035\ufe0f\u20e3": 5,
    "\u0036\ufe0f\u20e3": 6,
    "\u0037\ufe0f\u20e3": 7,
    "\u0038\ufe0f\u20e3": 8,
    "\u0039\ufe0f\u20e3": 9,
    "\U0001f51f":         10,
}

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "data", "peliculas.json")

TITULO_EN_INGLES = {
    "Avatar (2009)":                                "Avatar",
    "Avengers: Endgame (2019)":                     "Avengers: Endgame",
    "Titanic (1997)":                               "Titanic",
    "Star Wars: El Despertar de la Fuerza (2015)":  "Star Wars: The Force Awakens",
    "Avengers: Infinity War (2018)":                "Avengers: Infinity War",
    "Spider-Man: No Way Home (2021)":               "Spider-Man: No Way Home",
    "Jurassic World (2015)":                        "Jurassic World",
    "El Rey Leon (2019)":                           "The Lion King",
    "Los Vengadores (2012)":                        "The Avengers",
    "Rapidos y Furiosos 7 (2015)":                  "Furious 7",
}


def obtener_html(url):
    session = requests.Session()
    session.headers.update(HEADERS)
    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            print(f"  [->] Intento {intento}/{MAX_REINTENTOS} — conectando...")
            resp = session.get(url, timeout=20)
            if resp.status_code == 403:
                raise PermissionError("403 Forbidden.")
            if resp.status_code == 404:
                raise FileNotFoundError("404 — URL incorrecta.")
            resp.raise_for_status()
            print(f"  [OK] HTML descargado — {len(resp.text):,} caracteres")
            return BeautifulSoup(resp.text, "html.parser")
        except (PermissionError, FileNotFoundError):
            raise
        except (requests.ConnectionError, requests.Timeout) as e:
            print(f"  [!] Error de red: {e}")
            if intento < MAX_REINTENTOS:
                time.sleep(ESPERA_REINTENTOS)
            else:
                raise ConnectionError(f"Sin conexion tras {MAX_REINTENTOS} intentos.")


def buscar_poster_tmdb(titulo, rank):
    query        = TITULO_EN_INGLES.get(titulo, titulo)
    anio_match   = re.search(r"\((\d{4})\)", titulo)
    anio         = anio_match.group(1) if anio_match else None
    query_limpio = re.sub(r"\s*\(\d{4}\)", "", query).strip()

    try:
        params = {"api_key": TMDB_API_KEY, "query": query_limpio, "language": "es-MX"}
        if anio:
            params["year"] = anio

        resp = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params=params, timeout=10,
        )
        resp.raise_for_status()
        resultados = resp.json().get("results", [])

        if not resultados:
            print(f"    [!] TMDB: no encontro '{query_limpio}'")
            return None

        poster_path = resultados[0].get("poster_path")
        if not poster_path:
            print(f"    [!] TMDB: sin poster para '{query_limpio}'")
            return None

        url_imagen = f"https://image.tmdb.org/t/p/w500{poster_path}"
        print(f"    [OK] Poster #{rank:02d} — {resultados[0].get('title')}")
        return url_imagen

    except Exception as e:
        print(f"    [!] Error TMDB #{rank}: {e}")
        return None


def estrategia_emoji_headings(soup):
    contenedor = soup.body if soup.body else soup
    peliculas  = []
    for h in contenedor.find_all(["h2", "h3", "h4"]):
        texto = h.get_text(separator=" ", strip=True)
        rank  = None
        for emoji, num in EMOJI_A_NUM.items():
            if emoji in texto:
                rank = num
                break
        if rank is None:
            continue
        texto_limpio = texto
        for emoji in EMOJI_A_NUM:
            texto_limpio = texto_limpio.replace(emoji, "").strip()
        partes      = re.split(r"\s*[–\-]\s*(?=\$)", texto_limpio)
        titulo      = partes[0].strip()
        recaudacion = partes[1].strip() if len(partes) > 1 else None
        peliculas.append({"rank": rank, "titulo": titulo, "recaudacion": recaudacion})
        if len(peliculas) >= TOP_N:
            break
    peliculas.sort(key=lambda x: x["rank"])
    return peliculas


def estrategia_headings_numericos(soup):
    contenedor = soup.body if soup.body else soup
    peliculas  = []
    for h in contenedor.find_all(["h2", "h3", "h4", "h5"]):
        texto = h.get_text(separator=" ", strip=True)
        m = re.match(r"^[#\s]*(\d{1,2})[\s.\-\u2013:]+(.+)", texto)
        if not m:
            continue
        rank   = int(m.group(1))
        resto  = m.group(2).strip()
        partes = re.split(r"\s*[–\-]\s*(?=\$)", resto)
        titulo = partes[0].strip()
        rec    = partes[1].strip() if len(partes) > 1 else None
        if 1 <= rank <= 10 and len(titulo) > 1:
            peliculas.append({"rank": rank, "titulo": titulo, "recaudacion": rec})
    peliculas.sort(key=lambda x: x["rank"])
    return peliculas[:TOP_N]


def scrape(url):
    soup = obtener_html(url)
    estrategias = [
        ("emojis numericos",    estrategia_emoji_headings),
        ("headings numerados",  estrategia_headings_numericos),
    ]
    for nombre, fn in estrategias:
        print(f"  [->] Estrategia: {nombre}...", end=" ")
        try:
            resultado = fn(soup)
        except Exception as e:
            print(f"error — {e}")
            continue
        if len(resultado) >= 3:
            print(f"OK  {len(resultado)} peliculas encontradas")
            return resultado
        else:
            print(f"X  solo {len(resultado)}, descartada")
    raise ValueError("Ninguna estrategia extrajo suficientes datos.")


DATOS_MANUALES = [
    {"rank": 1,  "titulo": "Avatar (2009)",                               "recaudacion": "$2,923 millones"},
    {"rank": 2,  "titulo": "Avengers: Endgame (2019)",                    "recaudacion": "$2,799 millones"},
    {"rank": 3,  "titulo": "Titanic (1997)",                              "recaudacion": "$2,264 millones"},
    {"rank": 4,  "titulo": "Star Wars: El Despertar de la Fuerza (2015)", "recaudacion": "$2,071 millones"},
    {"rank": 5,  "titulo": "Avengers: Infinity War (2018)",               "recaudacion": "$2,052 millones"},
    {"rank": 6,  "titulo": "Spider-Man: No Way Home (2021)",              "recaudacion": "$1,921 millones"},
    {"rank": 7,  "titulo": "Jurassic World (2015)",                       "recaudacion": "$1,671 millones"},
    {"rank": 8,  "titulo": "El Rey Leon (2019)",                          "recaudacion": "$1,662 millones"},
    {"rank": 9,  "titulo": "Los Vengadores (2012)",                       "recaudacion": "$1,518 millones"},
    {"rank": 10, "titulo": "Rapidos y Furiosos 7 (2015)",                 "recaudacion": "$1,515 millones"},
]


def main():
    print("=" * 60)
    print("  FILMANALYTICS SCRAPER  +  TMDB Posters")
    print(f"  Fuente datos : {URL_FUENTE}")
    print(f"  Fuente poster: TMDB API (URL directa, sin descarga local)")
    print("=" * 60)

    try:
        peliculas_raw = scrape(URL_FUENTE)
    except Exception as e:
        print(f"\n[X] Scraping fallo: {e}")
        print("[->] Usando datos manuales...")
        peliculas_raw = DATOS_MANUALES

    print(f"\n[->] Obteniendo URLs de posters desde TMDB...")
    peliculas = []
    for p in peliculas_raw:
        imagen_url = buscar_poster_tmdb(p["titulo"], p["rank"])
        peliculas.append({
            "rank":        p["rank"],
            "titulo":      p["titulo"],
            "recaudacion": p.get("recaudacion"),
            "imagen":      imagen_url,
        })
        time.sleep(0.25)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(peliculas, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] JSON guardado -> {os.path.abspath(OUTPUT_PATH)}\n")
    imgs_ok = sum(1 for p in peliculas if p.get("imagen"))
    print(f"  Peliculas : {len(peliculas)}/{TOP_N}")
    print(f"  Posters   : {imgs_ok} con URL  |  {TOP_N - imgs_ok} sin imagen\n")
    for p in peliculas:
        img = "OK" if p.get("imagen") else "--"
        print(f"  #{p['rank']:>2}  {p['titulo']:<48} img:{img}")
    print()


if __name__ == "__main__":
    main()