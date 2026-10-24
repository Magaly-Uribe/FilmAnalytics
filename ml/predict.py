import os
import sys
import pickle
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(BASE_DIR, 'modelo.pkl')

with open(MODELO_PATH, 'rb') as f:
    modelo = pickle.load(f)


def predecir(anio, genero, budget, company, country, language):
    datos = pd.DataFrame([{
        'year':              int(anio),
        'budget':            int(budget),
        'genre_main':        genero,
        'country_main':      country,
        'original_language': language,
        'company_main':      company,
    }])

    prob      = modelo.predict_proba(datos)[0][1]
    etiqueta  = 'exitosa' if prob >= 0.5 else 'no exitosa'
    confianza = round(prob * 100, 2)
    return etiqueta, confianza


if __name__ == '__main__':
    if len(sys.argv) == 7:
        anio, genero, budget, company, country, language = sys.argv[1:7]
    else:
        anio, genero, budget = 2024, 'Action', 150000000
        company, country, language = 'Paramount', 'United States of America', 'en'

    etiqueta, confianza = predecir(anio, genero, budget, company, country, language)
    print(f"Etiqueta: {etiqueta}")
    print(f"Confianza: {confianza}%")