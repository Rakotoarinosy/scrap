import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def clean_text(text):
    """Nettoie le texte des caractères non désirés."""
    return text.replace("\xa0", "").strip() if text else ""

def get_info(soup, label):
    """Récupère la valeur associée à un label dans un tableau Wikipédia."""
    element = soup.find("th", string=label)
    if element:
        next_td = element.find_next("td")
        return clean_text(next_td.text) if next_td else ""
    return "Inconnu"

def scrape_country_info(country_name, country_url, capital_url):
    """Récupère les informations sur un pays et sa capitale."""
    try:
        response = requests.get(country_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        population = get_info(soup, "Population")
        area = get_info(soup, "Superficie")
        capital = get_info(soup, "Capitale")

        response_capital = requests.get(capital_url, timeout=10)
        response_capital.raise_for_status()
        soup_capital = BeautifulSoup(response_capital.content, 'html.parser')

        capital_population = get_info(soup_capital, "Population")
        latitude = soup_capital.find("span", class_="latitude")
        longitude = soup_capital.find("span", class_="longitude")

        return [
            country_name,
            population if population else "Inconnu",
            area if area else "Inconnu",
            capital if capital else "Inconnu",
            capital_population if capital_population else "Inconnu",
            latitude.text if latitude else "Inconnu",
            longitude.text if longitude else "Inconnu"
        ]
    except requests.exceptions.RequestException as e:
        print(f"Erreur pour {country_name}: {e}")
        return []

# Liste des pays à récupérer
countries = [
    ("Japon", "https://fr.wikipedia.org/wiki/Japon", "https://fr.wikipedia.org/wiki/Tokyo"),
    ("France", "https://fr.wikipedia.org/wiki/France", "https://fr.wikipedia.org/wiki/Paris")
]

data = []
for country in countries:
    info = scrape_country_info(*country)
    if info:
        data.append(info)
    time.sleep(2)  # Éviter le blocage par Wikipedia

# Sauvegarde des données
columns = ["Nom du pays", "Population", "Superficie", "Capitale", "Population capitale", "Latitude", "Longitude"]
df = pd.DataFrame(data, columns=columns)
df.to_csv("countries_info.csv", index=False, encoding="utf-8")

print("Scraping terminé et fichier CSV mis à jour.")
