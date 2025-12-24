import requests
from bs4 import BeautifulSoup
import os

# Configuration récupérée depuis les secrets GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def filter_job(title):
    """Filtre anti-stage et alternance"""
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
        res = "🌴 **WELCOME TO THE JUNGLE**\n"
        count = 0
        for job in jobs[:5]:
            title = job.find('h4').text.strip()
            if filter_job(title):
                company = job.find('span', class_='sc-6i2fy3-5').text.strip()
                link = "https://www.welcometothejungle.com" + job.find('a')['href'].split('?')[0]
                res += f"• **{company}** - {title}\n🔗 {link}\n\n"
                count += 1
        return res if count > 0 else "🌴 *WTTJ : Aucune nouvelle offre.*\n\n"
    except: return "🌴 *WTTJ : Erreur de connexion.*\n\n"

def get_linkedin():
    keywords = '"Juriste PI" OR "Business Affairs" OR "Droit de l\'audiovisuel"'
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location=France&f_TPR=r86400&f_JT=F%2CT&sortBy=DD"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('li')
        res = "💙 **LINKEDIN (24h)**\n"
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
        return res if count > 0 else "💙 *LinkedIn : Aucune nouvelle offre.*\n\n"
    except: return "💙 *LinkedIn : Erreur de connexion.*\n\n"

def get_profil_culture():
    url = "https://www.profilculture.com/annonce/liste.php?mots_cles=juriste"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding 
        soup = BeautifulSoup(response.text, 'html.parser')
        # On cherche tous les liens d'annonces
        links = soup.find_all('a', href=True)
        res = "🎭 **PROFIL CULTURE**\n"
        count = 0
        seen = []
        for l in links:
            t = l.get_text().strip()
            if "juriste" in t.lower() and filter_job(t) and t not in seen:
                full_url = "https://www.profilculture.com" + l['href']
                res += f"• {t}\n🔗 {full_url}\n\n"
                seen.append(t)
                count += 1
            if count >= 5: break
        return res if count > 0 else "🎭 *Profil Culture : Pas de nouvelles offres 'Juriste'.*\n\n"
    except: return "🎭 *Profil Culture : Erreur de connexion.*\n\n"

def get_others():
    # Liens directs pour les sites protégés
    apec = "https://www.apec.fr/candidat/recherche-emploi.html/liste-offres?motsCles=Juriste%20Propri%C3%A9t%C3%A9%20Intellectuelle&typesContrat=101888&typesContrat=101889"
    ft = "https://candidat.pole-emploi.fr/offres/recherche?motsCles=Juriste+Propriete+Intellectuelle&offresPartenaires=true"
    mc = "https://mediaclubjobs.fr/emploi/"
    
    res = "📑 **AUTRES SOURCES (LIENS DIRECTS)**\n"
    res += f"• 🎓 [APEC - Juriste PI]({apec})\n"
    res += f"• 🇫🇷 [France Travail - PI]({ft})\n"
    res += f"• 🎬 [Media Club Jobs]({mc})\n"
    return res

if __name__ == "__main__":
    message = "🚀 **VEILLE JURIDIQUE PI & BUSINESS AFFAIRS**\n\n"
    message += get_wttj()
    message += get_linkedin()
    message += get_profil_culture()
    message += get_others()
    
    # Envoi Telegram
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID, 
        'text': message, 
        'parse_mode': 'Markdown', 
        'disable_web_page_preview': True
    }
    requests.post(send_url, data=payload)
