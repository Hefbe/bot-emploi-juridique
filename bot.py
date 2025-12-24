import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def get_wttj():
    query = "juriste%20propriete%20intellectuelle%20audiovisuel%20medias%20business%20affairs"
    # URL avec filtre CDI et CDD intégré
    url = f"https://www.welcometothejungle.com/fr/jobs?query={query}&aroundQuery=France&sortBy=mostRecent&f=contract_type%3Afull_time%2Ctemporary"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('div', data_testimonial_id=False) 
        
        results = "🌴 **WELCOME TO THE JUNGLE (CDI/CDD)**\n"
        count = 0
        for job in jobs:
            if count >= 5: break
            try:
                title = job.find('h4').text.strip()
                
                # --- LE FILTRAGE EST ICI ---
                titre_min = title.lower()
                if any(x in titre_min for x in ["stage", "alternance", "apprentissage", "internship"]):
                    continue # On ignore cette annonce et on passe à la suivante
                # ---------------------------

                company = job.find('span', class_='sc-6i2fy3-5').text.strip()
                link = "https://www.welcometothejungle.com" + job.find('a')['href'].split('?')[0]
                results += f"🏢 **{company}**\n⚖️ {title}\n🔗 {link}\n\n"
                count += 1
            except:
                continue
        return results if count > 0 else ""
    except Exception as e:
        return f"❌ Erreur WTTJ: {e}"

def get_linkedin():
    keywords = '"Juriste PI" OR "Business Affairs" OR "Droit de l\'audiovisuel" OR "Droit des médias"'
    # URL avec filtre CDI (F) et CDD (T)
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location=France&f_TPR=r86400&f_JT=F%2CT&sortBy=DD"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('li')
        
        results = "💙 **LINKEDIN (CDI/CDD 24h)**\n"
        count = 0
        for job in jobs:
            if count >= 5: break
            try:
                title_tag = job.find('h3', class_='base-search-card__title')
                if title_tag:
                    title = title_tag.text.strip()
                    
                    # --- LE FILTRAGE EST ICI ---
                    titre_min = title.lower()
                    if any(x in titre_min for x in ["stage", "alternance", "apprentissage", "internship"]):
                        continue
                    # ---------------------------

                    company = job.find('h4', class_='base-search-card__subtitle').text.strip()
                    link = job.find('a', class_='base-card__full-link')['href'].split('?')[0]
                    results += f"🏢 **{company}**\n⚖️ {title}\n🔗 {link}\n\n"
                    count += 1
            except:
                continue
        return results if count > 0 else ""
    except Exception as e:
        return f"❌ Erreur LinkedIn: {e}"

def send_to_telegram(text):
    if not text.strip() or text.count('\n') < 5: # N'envoie rien si pas d'offres réelles
        return
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown', 'disable_web_page_preview': True}
    requests.post(send_url, data=payload)

if __name__ == "__main__":
    wttj = get_wttj()
    linkedin = get_linkedin()
    final_message = f"📢 **VEILLE JURIDIQUE PI & BA**\n\n{wttj}\n{linkedin}"
    send_to_telegram(final_message)
