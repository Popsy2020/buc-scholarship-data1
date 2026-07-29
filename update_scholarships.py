import os
import json
import sys
import google.generativeai as genai

try:
    # Authenticate using the hidden GitHub Secret
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    # Updated to the current active model alias
    model = genai.GenerativeModel('gemini-flash-latest')

    prompt = """
    Search the web for newly announced, updated, or reopened FUNDED scholarships (full or partial) for undergraduate or postgraduate study in Applied Arts, Fine Arts, Fashion Design, Textile Design, Visual Communication, Film, Photography, Architecture, or Heritage Conservation — suitable for Egyptian nationals to study abroad.

    Only include opportunities that are currently open, upcoming, or newly announced (not expired).

    Respond with ONLY a raw JSON array of exactly 5 objects. 

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

    # We force the model to respond in perfect JSON format
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        )
    )
    
    new_data = json.loads(response.text)
    
    # Save the array directly to a local JSON file
    with open("latest_scholarships.json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
        
    print("Successfully fetched and saved new scholarships.")

except Exception as e:
    print(f"Error fetching data: {e}")
    # Force the GitHub Action to fail properly so it doesn't try to commit nothing
    sys.exit(1)
