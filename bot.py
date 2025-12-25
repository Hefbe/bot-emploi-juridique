import requests
from bs4 import BeautifulSoup
import os
import urllib.parse

# Configuration des accès
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def filter_job(title):
    """Filtre anti-stage et alternance"""
    titre_min = title.lower()
    forbidden = ["stage", "alternance", "apprentissage", "internship", "stagiaire"]
    return not any(x in titre_min for x in forbidden)

def get_linkedin():
    keywords = '"Juriste" AND ("PI" OR "Propriété Intellectuelle" OR "Business Affairs" OR "Audiovisuel" OR "Musique" OR "Jeu Vidéo" OR "Digital")'
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location=France&f_TPR=r86400&f_JT=F%2CT&sortBy=DD"
    res = "💙 **LINKEDIN (Dernières 24h)**\n"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('li')
        count = 0
        for job in jobs[:5]:
            title_tag = job.find('h3', class_='base-search-card__title')
            if title_tag:
                title = title_tag.text.strip()
                if filter_job(title):
                    company = job.find('h4', class_='base-search-card__subtitle').text.strip()
                    link = job.find('a', class_='base-card__full-link')['href'].split('?')[0]
                    res += f"• **{company}** - {title}\n🔗 {link}\n\n"
                    count += 1
        return res if count > 0 else "💙 *LinkedIn : Pas d'offres en 24h.*\n\n"
    except: return ""

def get_village_justice():
    url = "https://www.village-justice.com/annonces/index.php?action=search&keywords=juriste+propriete+intellectuelle+musique+digital"
    res = "💙 **VILLAGE DE LA JUSTICE**\n"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        count = 0
        for l in links:
            t = l.get_text().strip()
            if "juriste" in t.lower() and filter_job(t):
                if "index.php?action=view" in l['href']:
                    link = "https://www.village-justice.com/annonces/" + l['href']
                    res += f"• {t}\n🔗 {link}\n\n"
                    count += 1
            if count >= 3: break
        return res if count > 0 else "💙 *Village Justice : Pas d'offres récentes.*\n\n"
    except: return ""

def get_mediaclub():
    url = "https://mediaclubjobs.fr/emploi/"
    res = "💙 **MEDIACLUB JOBS**\n"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all(['h2', 'h3'], class_='loop-item-title')
        count = 0
        for art in articles:
            link_tag = art.find('a')
            if link_tag:
                title = link_tag.get_text().strip()
                if any(word in title.lower() for word in ["juriste", "affairs", "droit", "legal"]):
                    if filter_job(title):
                        res += f"• {title}\n🔗 {link_tag['href']}\n\n"
                        count += 1
            if count >= 3: break
        return res if count > 0 else "💙 *MediaClub Jobs : Pas d'offres récentes.*\n\n"
    except: return ""

def get_profil_culture():
    url = "https://www.profilculture.com/annonce/liste.php?mots_cles=juriste"
    res = "💙 **PROFIL CULTURE**\n"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding 
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        count = 0
        seen = []
        for l in links:
            t = l.get_text().strip()
            if "juriste" in t.lower() and filter_job(t) and t not in seen:
                full_url = "https://www.profilculture.com" + l['href']
                res += f"• {t}\n🔗 {full_url}\n\n"
                seen.append(t)
                count += 1
            if count >= 3: break
        return res if count > 0 else "💙 *Profil Culture : Pas d'offres récentes.*\n\n"
    except: return ""

def check_specific_companies():
    domains = [
        "carrieres.groupe-tf1.fr", "joinus.canalplus.com", "careers.publicisgroupe.com",
        "wd3.myworkdaysite.com/fr-FR/recruiting/havas", "lvmh.com/fr/nous-rejoindre",
        "corporate.sacem.fr", "career.mediawan.com", "welcometothejungle.com/fr/companies/federation-studios"
    ]
    query = f"site:({' OR '.join(domains)}) juriste (PI OR 'Propriété Intellectuelle' OR 'Business Affairs')"
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&tbs=qdr:d"
    res = "💙 **ALERTES GRANDS GROUPES (Dernières 24h)**\n"
    res += f"👉 [Vérifier les nouveautés TF1, Canal, LVMH, etc.]({search_url})\n\n"
    return res

if __name__ == "__main__":
    content = get_linkedin() + get_village_justice() + get_mediaclub() + get_profil_culture() + check_specific_companies()
    
    if content.strip():
        final_msg = f"🚀 **VEILLE JURIDIQUE COMPLÈTE**\n\n{content}"
        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': final_msg, 'parse_mode': 'Markdown', 'disable_web_page_preview': True}
        requests.post(send_url, data=payload)
