import os
import json
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup

# ==============================================================================
# 1. CONFIGURATION & GEMINI SETUP
# ==============================================================================
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# ==============================================================================
# 2. HARDCODED MASTER TARGET DIRECTORY (ALL 7 CATEGORIES)
# ==============================================================================
TARGET_URLS = [
    # --------------------------------------------------------------------------
    # CATEGORY 1: Egypt-Specific & MENA-Focused Portals & Aggregators
    # --------------------------------------------------------------------------
    "https://egyptscholars.org",
    "https://www.scholars4dev.com/tag/scholarships-for-egyptians/",
    "https://www.scholarshiptab.com/scholarships/egypt",
    "https://www.amideast.org/egypt",
    "https://www.fordfoundation.org",
    "https://www.for9a.com",

    # --------------------------------------------------------------------------
    # CATEGORY 2: International Aggregators, Search Engines & Alerts
    # --------------------------------------------------------------------------
    "https://www.scholarshipportal.com",
    "https://www.mastersportal.com",
    "https://www.phdportal.com",
    "https://www.profellow.com",
    "https://euraxess.ec.europa.eu",
    "https://www.findaphd.com",
    "https://www.daad.de/en/study-and-research-in-germany/scholarships/",
    "https://educationusa.state.gov",
    "https://www.britishcouncil.org.eg/en/study-uk/scholarships",
    "https://egypte.campusfrance.org/en",
    "https://www.studyinholland.nl",
    "https://pivot.proquest.com",
    "https://www.wemakescholars.com",
    "https://opportunitydesk.org",
    "https://www.study.eu",
    "https://www.al-fanarmedia.org",
    "https://catchthatscholarship.com",
    "https://truescho.com",
    "https://scholarshipbob.com",
    "https://scholarshipsads.com",
    "https://brightscholarship.com",
    "https://opportunitiescorners.com",

    # --------------------------------------------------------------------------
    # CATEGORY 3: Government, Bilateral & Geopolitical Mobility Schemes
    # --------------------------------------------------------------------------
    "https://www.chevening.org",
    "https://study-uk.britishcouncil.org",
    "https://fulbright-egypt.org",
    "https://www.daad.eg/en/",
    "https://www.campusfrance.org/en",
    "https://www.turkiyeburslari.gov.tr",
    "https://www.eg.emb-japan.go.jp",
    "https://studyinitaly.esteri.it/en/call-for-applications",
    "https://stipendiumhungaricum.hu",
    "https://studyinchina.csc.edu.cn",
    "https://www.studyinkorea.go.kr",
    "https://www.sbfi.admin.ch",
    "https://ec.europa.eu/programmes/erasmus-plus/opportunities/individuals/students_en",
    "https://www.australiaawardsafrica.org",
    "https://nawa.gov.pl/en/",
    "https://www.msmt.cz",

    # --------------------------------------------------------------------------
    # CATEGORY 4: Regional, Development Bank & Philanthropic Foundations
    # --------------------------------------------------------------------------
    "https://www.sawirisfoundation.org/en/scholarships",
    "https://www.qalaaholdings.com",
    "https://www.akdn.org",
    "https://mekfoundation.org",
    "https://www.alghurairfoundation.org",
    "https://www.isdb.org",
    "https://www.afdb.org",
    "https://twas.org",
    "https://www.arabculturefund.org",
    "https://www.opensocietyfoundations.org",
    "https://www.rotary.org",
    "https://www.aauw.org",
    "http://www.ifs.se",

    # --------------------------------------------------------------------------
    # CATEGORY 5: Industry-Specific & Professional Design Bodies
    # --------------------------------------------------------------------------
    "https://www.britishfashioncouncil.co.uk",
    "https://cfda.com",
    "https://ifdaef.org",
    "https://www.surfacedesign.org",

    # --------------------------------------------------------------------------
    # CATEGORY 6: Specialized Global Art, Design & Partner Universities
    # --------------------------------------------------------------------------
    # United Kingdom
    "https://www.rca.ac.uk",
    "https://www.arts.ac.uk",
    "https://www.westminster.ac.uk",
    "https://www.southampton.ac.uk",
    "https://www.gsa.ac.uk",
    # Italy
    "https://www.polimi.it/en",
    "https://www.accademiaunidee.it",
    "https://www.domusacademy.com",
    "https://www.naba.it/en",
    "https://www.istitutomarangoni.com",
    # United States
    "https://www.newschool.edu/parsons/",
    "https://www.risd.edu",
    "https://www.pratt.edu",
    # Europe & Asia
    "https://caa.at0086.cn",
    "https://www.musabi.ac.jp/english/",
    "https://www.designacademy.nl",
    "https://rietveldacademie.nl",
    "https://mome.hu/en",
    "https://msgsu.edu.tr",
    "https://www.hongik.ac.kr",
    # MENA & Gulf Institutions
    "https://nyuad.nyu.edu",
    "https://qatar.vcu.edu",
    "https://pnu.edu.sa",
    "https://www.aus.edu",
    "https://www.zu.ac.ae",
    "https://www.aucegypt.edu",

    # --------------------------------------------------------------------------
    # CATEGORY 7: Cairo-Based Cultural Offices & Consultancies
    # --------------------------------------------------------------------------
    "https://www.goethe.de/ins/eg/en/index.html",
    "https://institutfrancais-egypte.com",
    "https://www.idp.com/egypt/"
]

# ==============================================================================
# 3. EVALUATION PROMPT & SCHEMA FOR APPLIED ARTS DEDICATED SCRAPING
# ==============================================================================
SYSTEM_PROMPT = """
You are an expert academic evaluator and data structurer for the School of Applied Arts at Badr University in Cairo (BUC). 
Your task is to analyze raw text scraped from scholarship portals, university pages, and foundation websites. 
You must extract and format valid opportunities into a strict JSON array of scholarship objects.

CRITICAL EVALUATION RULES:
1. ELIGIBILITY: The opportunity MUST explicitly accept applications from Egyptian citizens. Discard opportunities restricted strictly to EU, US, or non-Egyptian citizens.
2. FIELD OF STUDY: The opportunity MUST align with at least one of BUC's core Applied Arts departments and specialties. Explicitly look for matches, subsets, or direct equivalents to the following:
   - Design Fields: Interior Design and Furniture, Industrial Design, Furniture & Metal Constructions Design.
   - Textiles and Apparel: Apparel, Spinning & Weaving, Printing Textiles, Dyeing & Finishing.
   - Media and Visual Arts: Advertising, Print, Publishing and Packaging, Photography, Cinema and Television.
   - Crafts and Applied Formations: Metal Products and Jewelry, Sculpture & Architectural Formation, Glass, Ceramics.
   If the scholarship is strictly for Medical, Pure Sciences, or entirely unrelated fields, discard it.
3. DEADLINES: Extract exact deadlines. If no specific date is given, output "Varies" or "Rolling". Do not invent dates.
4. NO HALLUCINATIONS: Base extraction strictly on the provided text. Use "Not specified" for missing fields.

JSON SCHEMA REQUIREMENT:
Return ONLY a valid JSON array. Each object must contain EXACTLY the following keys:
- "id": (integer, generate a random 4-digit ID)
- "name": (string, name of the scholarship)
- "country": (string, host country)
- "fundingBody": (string, organization providing funds)
- "degreeLevels": (array of strings, e.g., ["BA", "MA"] or ["Residency"])
- "fundingType": (string, "Full", "Partial", or "Varies")
- "coverage": (string, brief summary of covered items)
- "language": (string, "English", "Non-English", or "Both")
- "languageRaw": (string, specific requirement like "IELTS 6.5")
- "deadline": (string, exact date, month, or status)
- "eligibility": (string, brief summary emphasizing Egyptian eligibility)
- "notes": (string, strategic advice for applicants)
- "fields": (array of strings, mapped exactly to the specific BUC department or specialty names matched from Rule 2)
- "competitiveness": (string, "Moderate", "High", "Very High", or "Top Priority")
- "linkDisplay": (string, clean domain name like "daad.de")
- "linkUrl": (string, full URL)
"""

# ==============================================================================
# 4. RESILIENT SCRAPING & GEMINI EXTRACTION LOGIC
# ==============================================================================
def scrape_text_from_url(url):
    """Fetches web page content with anti-bot protection and strict timeouts."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        # Timeout: 5s connection, 15s read
        response = requests.get(url, headers=headers, timeout=(5, 15))
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip script, style, and navigation tags to preserve Gemini tokens
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.extract()
            
        text = ' '.join(soup.stripped_strings)
        return text[:12000] # Token window cap

    except requests.exceptions.Timeout:
        print(f"  ↳ ⏭️ SKIPPED: Timeout at {url}")
        return ""
    except requests.exceptions.HTTPError as e:
        print(f"  ↳ ⏭️ SKIPPED: HTTP {e.response.status_code} at {url}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"  ↳ ⏭️ SKIPPED: Network error at {url}")
        return ""

def evaluate_with_gemini(raw_text):
    """Processes scraped text using gemini-1.5-flash-latest to extract structured JSON."""
    if not raw_text.strip():
        return []

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        system_instruction=SYSTEM_PROMPT
    )
    
    try:
        response = model.generate_content(
            f"Extract scholarship opportunities from this text. Return ONLY a JSON array:\n\n{raw_text}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"  ↳ ⚠️ Gemini extraction failed for chunk: {e}")
        return []

# ==============================================================================
# 5. MAIN EXECUTION PIPELINE
# ==============================================================================
def main():
    all_new_scholarships = []
    total_targets = len(TARGET_URLS)
    
    print(f"🚀 Starting BUC Scholarship Passport Crawler across {total_targets} Master Directory URLs...\n")
    
    for idx, url in enumerate(TARGET_URLS, 1):
        print(f"[{idx}/{total_targets}] Processing: {url}")
        raw_text = scrape_text_from_url(url)
        
        if raw_text:
            extracted_data = evaluate_with_gemini(raw_text)
            print(f"  ↳ ✅ Found {len(extracted_data)} eligible opportunities.")
            
            for item in extracted_data:
                if not item.get("linkUrl"):
                    item["linkUrl"] = url
                all_new_scholarships.append(item)

    # Output writing
    if all_new_scholarships:
        with open("latest_scholarships.json", "w", encoding="utf-8") as f:
            json.dump(all_new_scholarships, f, indent=4, ensure_ascii=False)
        print(f"\n✨ Scan Finished Successfully!")
        print(f"Saved {len(all_new_scholarships)} structured opportunities to 'latest_scholarships.json'.")
    else:
        print("\n⚠️ Scan complete, but no new matching opportunities were parsed.")

if __name__ == "__main__":
    main()
