import json

import pandas as pd
import chardet
from forex_python.converter import CurrencyRates
from pymongo import MongoClient


def delete_cols(df, cols):
    df = df.drop(columns=cols)

    return df


def replace_bool(df, cols):
    for col in cols:
        df[col] = df[col].replace({"Yes": True, "No": False})

    return df


def delete_not_utf(df, cols):
    for col in cols:
        df = df[~df[col].str.contains(r'[^\x00-\x7F]')]

    return df


if __name__ == '__main__':
    # Rileva la codifica del file CSV
    with open("zomato.csv", 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']

    df = pd.read_csv("zomato.csv", encoding=encoding)

    # Eliminiamo colonne non rilevanti per ridurre le dimensioni del dataset
    df = delete_cols(df, cols=["Country Code", "Locality Verbose", "Longitude", "Latitude",
                               "Is delivering now", "Switch to order menu", "Rating color", "Rating text"])

    # Rendiamo le colonne "Has Table booking" e "Has Online delivery" da string a booleane
    df = replace_bool(df, cols=["Has Table booking", "Has Online delivery"])

    # Normalizziamo il formato dei nomi delle colonne
    df = df.rename(columns=lambda x: x.lower().replace(' ', '_'))

    # Eliminiamo le righe aventi caratteri con codifica non leggibile
    df = delete_not_utf(df, cols=["restaurant_name", "city", "address", "locality"])

    # Trasformiamo la colonna "cuisines" in un array di stringhe
    df['cuisines'] = df['cuisines'].str.split(', ')

    df.to_csv("dataset.csv", encoding="utf-8", index=False)
    df.to_json("data.json", orient="records")

    print(df.columns)
    print(df.dtypes.to_dict())

    DB_URI = "mongodb://localhost:27017/"

    client = MongoClient(DB_URI)

    db = client["progettoBD2"]

    db_collection = db["ristoranti"]

    json_file = open("data.json")

    db_collection.insert_many(json.load(json_file))
