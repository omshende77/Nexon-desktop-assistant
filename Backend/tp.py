import requests
from bs4 import BeautifulSoup
import webbrowser

# Simulated app opener (replace with AppOpener in real use)
def appopen(app, match_closest=True, output=True, throw_error=True):
    raise Exception(f"{app.upper()} is not running")

def extract_links(html):
    if html is None:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    
    # DuckDuckGo Lite HTML uses <a rel="nofollow" class="result__a" href="...">
    results = soup.find_all("a", attrs={"class": "result__a", "href": True})
    if not results:
        # Try fallback: any <a> inside a result block
        results = soup.select("div.result a[href]")
    
    return [a['href'] for a in results if a['href'].startswith("http")]

def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        print(f"✅ Successfully opened {app}")
        return True
    except Exception as e:
        print(f"⚠️ App '{app}' not found. Error: {e}")
        print(f"🌐 Searching for '{app}' on DuckDuckGo...")

        query = app.replace(" ", "+")
        url = f"https://html.duckduckgo.com/html/?q={query}"

        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            print(f"🌐 [DEBUG] Request to DuckDuckGo: {response.status_code}")
            html = response.text
            print("\n🔍 [DEBUG] HTML preview:")
            print(html[:1000])

            links = extract_links(html)
            print(f"\n🔍 [DEBUG] Found {len(links)} result link(s).")
            print("🔍 [DEBUG] Extracted links:")
            print(links)

            if links:
                print(f"✅ Opening: {links[0]}")
                webbrowser.open(links[0])
                return True
            else:
                print("❌ No valid links found in DuckDuckGo results.")
                return False
        except Exception as net_err:
            print(f"❌ Network error during DuckDuckGo search: {net_err}")
            return False

# Run it
if __name__ == "__main__":
    OpenApp("Facebook")
