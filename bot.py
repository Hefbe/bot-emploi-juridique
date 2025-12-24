import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def filter_job(title):
    """Retourne True si l'annonce est valide (pas un stage)"""
    titre_min = title.lower()
    forbidden = ["stage", "alternance", "apprentissage", "internship", "stagiaire"]
    return not any(x in titre_min for x in forbidden)

def get_wttj():
    query = "juriste%20propriete%20intellectuelle%20audiovisuel%20medias%20business%20affairs"
    url = f"https://www.welcometothejungle.com/fr/jobs?query={query}&aroundQuery=France&sortBy=mostRecent&f=contract_type%3Afull_time%2Ctemporary"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('div', data_testimonial_id=False)
        res = "🌴 **WTTJ**\n"
        count = 0
        for job in jobs[:8]:
            title = job.find('h4').text.strip()
            if filter_job(title):
                company = job.find('span', class_='sc-6i2fy3-5').text.strip()
                link = "https://www.welcometothejungle.com" + job.find('a')['href'].split('?')[0]
                res += f"• **{company}** - {title}\n🔗 {link}\n\n"
                count += 1
        return res if count > 0 else ""
    except: return ""

def get_linkedin():
    keywords = '"Juriste PI" OR "Business Affairs" OR "Droit de l\'audiovisuel"'
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location=France&f_TPR=r86400&f_JT=F%2CT&sortBy=DD"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('li')
        res = "💙 **LINKEDIN**\n"
        count = 0
        for job in jobs[:8]:
            title_tag = job.find('h3', class_='base-search-card__title')
            if title_tag:
                title = title_tag.text.strip()
                if filter_job(title):
                    company = job.find('h4', class_='base-search-card__subtitle').text.strip()
                    link = job.find('a', class_='base-card__full-link')['href'].split('?')[0]
                    res += f"• **{company}** - {title}\n🔗 {link}\n\n"
                    count += 1
        return res if count > 0 else ""
    except: return ""

def get_profil_culture():
    # Profil Culture est LA référence pour l'audiovisuel
    url = "https://www.profilculture.com/annonce/liste.php?mots_cles=juriste"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('div', class_='offre')
        res = "🎭 **PROFIL CULTURE**\n"
        count = 0
        for job in jobs[:5]:
            title = job.find('h3').text.strip()
            if filter_job(title):
                link = "https://www.profilculture.com" + job.find('a')['href']
                res += f"• {title}\n🔗 {link}\n\n"
                count += 1
        return res if count > 0 else ""
    except: return ""

def get_apec():
    # L'APEC est excellent pour les cadres juridiques
    url = "https://www.apec.fr/candidat/recherche-emploi.html/liste-offres?motsCles=Juriste%20Propri%C3%A9t%C3%A9%20Intellectuelle&typesContrat=101888&typesContrat=101889"
    # Note: Le scraping APEC est complexe, on fournit ici le lien direct de veille
    return f"🎓 **APEC (Lien Veille)**\n🔗 [Consulter les offres Juriste PI/BA]( {url} )\n\n"

def get_france_travail():
    url = "https://candidat.pole-emploi.fr/offres/recherche?motsCles=Juriste+Propriete+Intellectuelle&offresPartenaires=true"
    return f"🇫🇷 **FRANCE TRAVAIL**\n🔗 [Lien vers les offres du jour]({url})\n\n"

def get_mediaclub():
    # MediaClub Jobs
    url = "https://mediaclubjobs.fr/emploi/"
    return f"🎬 **MEDIA CLUB JOBS**\n🔗 [Vérifier les nouvelles offres]({url})\n\n"

if __name__ == "__main__":
    content = ""
    content += get_wttj()
    content += get_linkedin()
    content += get_profil_culture()
    content += get_apec()
    content += get_france_travail()
    content += get_mediaclub()
    
    if content.strip():
        final_msg = f"🚀 **VOTRE VEILLE JURIDIQUE COMPLÈTE**\n\n{content}"
        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': final_msg, 'parse_mode': 'Markdown', 'disable_web_page_preview': True}
        requests.post(send_url, data=payload)
