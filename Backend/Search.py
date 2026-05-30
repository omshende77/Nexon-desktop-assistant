"""
Search.py — DuckDuckGo real-time web search tool for Nexon AI.
"""

from duckduckgo_search import DDGS

def get_realtime_search_results(query: str, max_results: int = 4) -> str:
    """
    Searches the web and returns a formatted string of the top results.
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        
        if not results:
            return "No recent real-time information found on the web."
            
        formatted = "Here are the latest real-time web search results:\n\n"
        for idx, res in enumerate(results, 1):
            title = res.get('title', 'No Title')
            body = res.get('body', 'No Description')
            href = res.get('href', '')
            formatted += f"[{idx}] {title}\nSummary: {body}\nSource: {href}\n\n"
            
        formatted += "\nPlease provide a concise answer using the above real-time data. Cite sources if appropriate."
        return formatted
    except Exception as e:
        print(f"[Search Engine Error] {e}")
        return "An error occurred while searching the web for real-time data."
