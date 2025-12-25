import requests
from bs4 import BeautifulSoup
import os

# Secrets GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
MON_CV = os.getenv('MON_PARCOURS')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def filter_job(title):
    """Filtre anti-stage et alternance"""
    titre_min = title.lower()
    forbidden = ["stage", "alternance", "apprentissage", "internship", "stagiaire"]
    return not any(x in titre_min for x in forbidden)

def generer_arguments_ia(job_title, company):
    """Demande à Gemini de générer un argumentaire de motivation"""
    if not GEMINI_KEY or not MON_CV:
        return "⚠️ (IA non configurée)"
    
    prompt = f"""
    En tant qu'expert en recrutement juridique, aide-moi à préparer ma candidature.
    ENTREPRISE : {company}
    POSTE : {job_title}
    MON PARCOURS : {MON_CV}
    
    Rédige 3 points d'accroche percutants (maximum 4 lignes total) montrant le lien entre mon expérience et ce poste spécifique. 
    Sois professionnel et précis.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "❌ Erreur génération IA."

def get_linkedin():
    keywords = '"Juriste PI" OR "Business Affairs" OR "Droit de l\'audiovisuel"'
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location=France&f_TPR=r86400&f_JT=F%2CT&sortBy=DD"
    res = "💙 **LINKEDIN**\n"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('li')
        count = 0
        for job in jobs[:3]:
            title_tag = job.find('h3', class_='base-search-card__title')
            if title_tag:
                title = title_tag.text.strip()
                if filter_job(title):
                    company = job.find('h4', class_='base-search-card__subtitle').text.strip()
                    link = job.find('a', class_='base-card__full-link')['href'].split('?')[0]
                    args = generer_arguments_ia(title, company)
                    res += f"• **{company}** - {title}\n🔗 {link}\n💡 *Arguments :*\n{args}\n\n"
                    count += 1
        return res if count > 0 else ""
    except: return ""

def get_village_justice():
    """Recherche sur Village de la Justice"""
    url = "https://www.village-justice.com/annonces/index.php?action=search&keywords=juriste+propriete+intellectuelle"
    res = "💙 **VILLAGE DE LA JUSTICE**\n"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        # On cherche les blocs d'annonces
        articles = soup.find_all('div', class_='row mb-3')
        count = 0
        for art in articles[:4]:
            link_tag = art.find('a', href=True)
            if link_tag and filter_job(link_tag.text):
                title = link_tag.text.strip()
                link = "https://www.village-justice.com/annonces/" + link_tag['href']
                res += f"• {title}\n🔗 {link}\n\n"
                count += 1
        return res if count > 0 else ""
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
            if count >= 4: break
        return res if count > 0 else ""
    except: return ""

def get_others():
    wttj = "https://www.welcometothejungle.com/fr/jobs?query=juriste%20propriete%20intellectuelle&aroundQuery=France&sortBy=mostRecent&f=contract_type%3Afull_time%2Ctemporary"
    apec = "https://www.apec.fr/candidat/recherche-emploi.html/liste-offres?motsCles=Juriste%20Propri%C3%A9t%C3%A9%20Intellectuelle"
    
    res = "💙 **AUTRES LIENS DIRECTS**\n"
    res += f"• [Welcome To The Jungle]({wttj})\n"
    res += f"• [APEC - Juriste PI]({apec})\n"
    res += f"• [Media Club Jobs](https://mediaclubjobs.fr/emploi/)\n"
    return res

if __name__ == "__main__":
    content = get_linkedin() + get_village_justice() + get_profil_culture() + get_others()
    
    if content.strip():
        final_msg = f"🚀 **VEILLE JURIDIQUE PI & BA**\n\n{content}"
        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID, 
            'text': final_msg, 
            'parse_mode': 'Markdown', 
            'disable_web_page_preview': True
        }
        requests.post(send_url, data=payload)
