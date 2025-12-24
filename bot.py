import requests
from bs4 import BeautifulSoup
import os

# Configuration via les secrets GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def search_jobs():
    # URL ciblée : Juriste PI ou Business Affairs en France
    url = "https://www.welcometothejungle.com/fr/jobs?query=juriste%20propriete%20intellectuelle%20business%20affairs&aroundQuery=France"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # On cherche les articles d'annonces
    jobs = soup.find_all('div', class_='sc-6i2fy3-3') 
    
    message = "🔍 NOUVELLES ANNONCES PI / BUSINESS AFFAIRS :\n\n"
    
    if not jobs:
        return # Si rien n'est trouvé, on n'envoie rien
        
    for job in jobs[:5]: # On prend les 5 plus récentes
        try:
            title = job.find('h4').text
            company = job.find('span', class_='sc-6i2fy3-5').text
            link = "https://www.welcometothejungle.com" + job.find('a')['href']
            message += f"🏢 {company}\n⚖️ {title}\n🔗 {link}\n\n"
        except:
            continue

    # Envoi vers Telegram
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(send_url)

if __name__ == "__main__":
    search_jobs()
