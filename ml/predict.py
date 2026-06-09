import pickle
import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Cargar modelo
with open('/var/www/html/webapp/Proyecto filmin/ml/modelo.pkl', 'rb') as f:
    bundle = pickle.load(f)

model        = bundle['model']
scaler       = bundle['scaler']
le           = bundle['encoders']
features_num = bundle['features_num']
features_cat = bundle['features_cat']

def predecir(anio, genero, budget, company):
    df = pd.DataFrame([{
        'year':              int(anio),
        'budget':            int(budget),
        'genre_main':        genero,
        'country_main':      'United States of America',
        'original_language': 'en',
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
    if len(sys.argv) == 5:
        anio    = sys.argv[1]
        genero  = sys.argv[2]
        budget  = sys.argv[3]
        company = sys.argv[4]
    else:
        # Valores por defecto para prueba
        anio, genero, budget, company = 2024, 'Action', 150000000, 'Paramount'

    etiqueta, confianza = predecir(anio, genero, budget, company)
    print(f"Etiqueta: {etiqueta}")
    print(f"Confianza: {confianza}%")
