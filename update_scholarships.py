import os
import json
import google.generativeai as genai

# Authenticate using the hidden GitHub Secret
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use the free-tier model
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = """
Search the web for newly announced, updated, or reopened FUNDED scholarships (full or partial) for undergraduate or postgraduate study in Applied Arts, Fine Arts, Fashion Design, Textile Design, Visual Communication, Film, Photography, Architecture, or Heritage Conservation — suitable for Egyptian nationals to study abroad.

Only include opportunities that are currently open, upcoming, or newly announced (not expired).

Respond with ONLY a raw JSON array (no markdown fences, no prose), of exactly 5 objects. 

Each object must have exactly these fields:
{
  "id": integer (use a random 5-digit number),
  "name": string,
  "country": string,
  "fundingBody": string,
  "degreeLevels": array of strings from ["BA","MA","PhD","Residency","Other"],
  "fundingType": "Full" or "Partial",
  "coverage": string,
  "language": "English" or "Non-English" or "Both",
  "deadline": string (e.g., "October 2026"),
  "eligibility": string,
  "fields": array of strings from ["Fashion","Textiles","Fine Arts","Design","Film","Architecture","Heritage/Conservation","Photography","Arts Management","All Fields (incl. Arts)"],
  "competitiveness": "Top Priority" or "High" or "Very High" or "Moderate",
  "notes": string,
  "linkUrl": string
}
"""

try:
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    
    # Clean formatting if the model adds markdown
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
        
    new_data = json.loads(raw_text.strip())
    
    # Save the array directly to a local JSON file
    with open("latest_scholarships.json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
        
    print("Successfully fetched and saved new scholarships.")
except Exception as e:
    print(f"Error fetching data: {e}")
