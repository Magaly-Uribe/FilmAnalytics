import pickle
import sys
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(BASE_DIR, 'modelo.pkl')

with open(MODELO_PATH, 'rb') as f:
    bundle = pickle.load(f)

model        = bundle['model']
scaler       = bundle['scaler']
le           = bundle['encoders']
features_num = bundle['features_num']
features_cat = bundle['features_cat']

def predecir(anio, genero, budget, company, country, language):
    df = pd.DataFrame([{
        'year':              int(anio),
        'budget':            int(budget),
        'genre_main':        genero,
        'country_main':      country,
        'original_language': language,
        'company_main':      company
    }])

    for col in features_cat:
        if col in df.columns:
            try:
                df[col] = le[col].transform(df[col])
            except ValueError:
                df[col] = 0

    df[features_num] = scaler.transform(df[features_num])

    X         = df[features_num + features_cat]
    prob      = model.predict_proba(X)[0][1]
    etiqueta  = 'exitosa' if prob >= 0.5 else 'no exitosa'
    confianza = round(prob * 100, 2)

    return etiqueta, confianza

if __name__ == '__main__':
    if len(sys.argv) == 7:
        anio     = sys.argv[1]
        genero   = sys.argv[2]
        budget   = sys.argv[3]
        company  = sys.argv[4]
        country  = sys.argv[5]
        language = sys.argv[6]
    else:
        anio     = 2024
        genero   = 'Action'
        budget   = 150000000
        company  = 'Paramount'
        country  = 'United States of America'
        language = 'en'

    etiqueta, confianza = predecir(anio, genero, budget, company, country, language)
    print(f"Etiqueta: {etiqueta}")
    print(f"Confianza: {confianza}%")
