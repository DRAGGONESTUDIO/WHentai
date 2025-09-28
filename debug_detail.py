import requests
from bs4 import BeautifulSoup

# Test URL from the videos.json file
url = "https://www.cartoonpornvideos.com/out/?l=3AASdM4ZpjDyq1hlUGZCVDJZZjVmAtkhaHR0cHM6Ly94aC5wYXJ0bmVycy94L3hoRWlsVko/cHc9zQGGonRjAQGncG9wdWxhcgHZMHsiYWxsIjoiIiwib3JpZW50YXRpb24iOiJzdHJhaWdodCIsInByaWNpbmciOiIifcDOaNf4xMDOABLpicDZPVt7IjEiOiJjNGRMUUZRd3VEUiJ9LHsiMiI6InNlY0ZTajM2bnQ2In0seyIzIjoiSWl6V2dxVUFBRHkifV0%3D&c=43a8e449&v=3&"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; AnimeScraper/1.0; +https://yourdomain.example/)",
    "Accept-Language": "en-US,en;q=0.9"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    print("=== Page Title ===")
    print(soup.title.string if soup.title else "No title")
    
    print("\n=== All Links ===")
    for i, a in enumerate(soup.find_all("a", href=True)):
        # Safely get attributes
        href = ""
        text = ""
        target = ""
        rel = ""
        classes = ""
        
        try:
            if hasattr(a, 'get'):
                href = a.get("href", "")
        except:
            pass
            
        try:
            if hasattr(a, 'get_text'):
                text = a.get_text().strip()
        except:
            pass
            
        try:
            if hasattr(a, 'get'):
                target = a.get("target", "")
        except:
            pass
            
        try:
            if hasattr(a, 'get'):
                rel = a.get("rel", "")
        except:
            pass
            
        try:
            if hasattr(a, 'get'):
                classes = a.get("class", "")
        except:
            pass
            
        print(f"{i+1}. href: {href}")
        print(f"   text: {text}")
        print(f"   target: {target}")
        print(f"   rel: {rel}")
        print(f"   classes: {classes}")
        print()
        
    print("\n=== Meta Refresh (if any) ===")
    meta_refresh = soup.find("meta", attrs={"http-equiv": "refresh"})
    if meta_refresh:
        print(meta_refresh)
    else:
        print("No meta refresh found")
        
    print("\n=== First 2000 characters of page ===")
    print(response.text[:2000])
        
except Exception as e:
    print(f"Error: {e}")