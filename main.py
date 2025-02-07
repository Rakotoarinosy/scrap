from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Chargement sécurisé du fichier CSV
csv_file = "countries_info.csv"

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    df.rename(columns={"Nom du pays": "Pays"}, inplace=True)

    # Vérification des colonnes
    expected_columns = {"Pays", "Capitale", "Population", "Superficie", "Latitude", "Longitude"}
    missing_columns = expected_columns - set(df.columns)
    
    if missing_columns:
        print(f"Colonnes manquantes : {missing_columns}")
        for col in missing_columns:
            df[col] = "Inconnu"  # Remplissage des valeurs manquantes
else:
    print("Fichier CSV introuvable. Initialisation d'un DataFrame vide.")
    df = pd.DataFrame(columns=["Pays", "Capitale", "Population", "Superficie", "Latitude", "Longitude"])

@app.get("/")
def home(request: Request):
    countries = df["Pays"].dropna().tolist() if "Pays" in df.columns else []
    return templates.TemplateResponse("index.html", {"request": request, "countries": countries})

@app.get("/countries")
def get_countries():
    return df["Pays"].dropna().tolist()

@app.get("/country/{country_name}")
def country_details(request: Request, country_name: str):
    country_data = df[df["Pays"].str.lower() == country_name.lower()]

    if country_data.empty:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Pays non trouvé."})

    row = country_data.iloc[0]
    return templates.TemplateResponse("Carte.html", {
        "request": request,
        "country": row["Pays"],
        "capital": row["Capitale"],
        "population": row["Population"],
        "superficie": row["Superficie"],
        "latitude": row["Latitude"],
        "longitude": row["Longitude"]
    })
