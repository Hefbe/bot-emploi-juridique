import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def filter_job(title):
    titre_min = title.lower()
    forbidden = ["stage", "alternance", "apprentissage", "internship", "stagiaire"]
    return not any(x in titre_min for x in forbidden)

# --- FONCTIONS DE SCRAPING (LINKEDIN, VILLAGE, MEDIACLUB, PROFIL CULTURE) ---
# [Ici se trouvent vos fonctions habituelles que nous avons déjà validées]

def check_specific_companies():
    """Cherche via Google si de nouvelles pages 'Juriste' sont apparues sur les sites cibles"""
    # Liste des domaines à surveiller
    domains = [
        "carrieres.groupe-tf1.fr",
        "joinus.canalplus.com",
        "careers.publicisgroupe.com",
        "wd3.myworkdaysite.com/fr-FR/recruiting/havas",
        "lvmh.com/fr/nous-rejoindre",
        "corporate.sacem.fr",
        "career.mediawan.com"
    ]
    
    query = f"site:({' OR '.join(domains)}) juriste (PI OR 'Propriété Intellectuelle' OR 'Business Affairs')"
    # On encode la requête pour Google
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&tbs=qdr:d" # tbs=qdr:d limite aux dernières 24h
    
    res = "💙 **ALERTES GRANDS GROUPES (Dernières 24h)**\n"
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        if "did not match any documents" in response.text:
            return "💙 *Grands Groupes : Aucune nouvelle annonce directe.*\n\n"
        
        # Si Google trouve des résultats, on donne le lien de recherche direct pour que vous voyiez les nouveautés
        res += f"👉 [Cliquez ici pour voir les nouveautés détectées sur TF1, Canal, LVMH, etc.]({search_url})\n\n"
        return res
    except:
        return ""

# --- BLOC PRINCIPAL ---
if __name__ == "__main__":
    # On mixe les deux approches : Scraping précis + Surveillance Google
    content = get_linkedin()
    content += get_village_justice()
    content += get_mediaclub()
    content += get_profil_culture()
    content += check_specific_companies() # La nouvelle fonction
    
    if content.strip():
        final_msg = f"🚀 **VEILLE JURIDIQUE COMPLÈTE**\n\n{content}"
        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': final_msg, 'parse_mode': 'Markdown', 'disable_web_page_preview': True}
        requests.post(send_url, data=payload)
