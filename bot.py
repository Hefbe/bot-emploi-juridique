def get_linkedin():
    # Requête ultra-complète pour Juriste PI / Médias / Digital
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
