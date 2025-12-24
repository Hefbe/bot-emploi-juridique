import requests
from bs4 import BeautifulSoup
import os

# Configuration récupérée depuis les secrets GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_wttj():
    def get_wttj():
    """Recherche sur WTTJ - Filtre CDI et CDD"""
    # On ajoute le paramètre 'contract_type=full_time,temporary' pour CDI et CDD
    query = "juriste%20propriete%20intellectuelle%20audiovisuel%20medias%20business%20affairs"
    url = f"https://www.welcometothejungle.com/fr/jobs?query={query}&aroundQuery=France&sortBy=mostRecent&f=contract_type%3Afull_time%2Ctemporary"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Note: on ajuste la recherche des balises si nécessaire
        jobs = soup.find_all('div', data_testimonial_id=False) 
        
        results = "🌴 **WELCOME TO THE JUNGLE (CDI/CDD)**\n"
        # ... reste du code identique ...
        
        results = "🌴 **WELCOME TO THE JUNGLE**\n"
        for job in jobs[:5]:
            title = job.find('h4').text.strip()
            company = job.find('span', class_='sc-6i2fy3-5').text.strip()
            link = "https://www.welcometothejungle.com" + job.find('a')['href'].split('?')[0]
            results += f"🏢 {company}\n⚖️ {title}\n🔗 {link}\n\n"
        return results
    except Exception as e:
        return f"❌ Erreur WTTJ: {e}"

def get_linkedin():
    """Recherche sur LinkedIn (version publique)"""
    # Filtre f_TPR=r86400 pour les dernières 24h
   # Recherche groupée : on utilise OR pour cibler tous les intitulés d'un coup
    keywords = '"Juriste PI" OR "Business Affairs" OR "Droit de l\'audiovisuel" OR "Droit des médias"'
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location=France&f_TPR=r86400&sortBy=DD"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('li')
        
        results = "💙 **LINKEDIN (24h)**\n"
        count = 0
        for job in jobs:
            if count >= 5: break
            title_tag = job.find('h3', class_='base-search-card__title')
            if title_tag:
                title = title_tag.text.strip()
                company = job.find('h4', class_='base-search-card__subtitle').text.strip()
                link = job.find('a', class_='base-card__full-link')['href'].split('?')[0]
                results += f"🏢 {company}\n⚖️ {title}\n🔗 {link}\n\n"
                count += 1
        return results
    except Exception as e:
        return f"❌ Erreur LinkedIn: {e}"

def send_to_telegram(text):
    """Envoie le message final sur Telegram"""
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True
    }
    requests.post(send_url, data=payload)

if __name__ == "__main__":
    # 1. On récupère les deux listes
    wttj_results = get_wttj()
    linkedin_results = get_linkedin()
    
    # 2. On fusionne
    final_message = f"📢 **VEILLE JURIDIQUE PI & BA**\n\n{wttj_results}\n{linkedin_results}"
    
    # 3. On envoie
    send_to_telegram(final_message)
