def search_web(query: str, max_results: int = 3) -> list:
    """DuckDuckGo se live web search karta hai aur relevant information summarize karta hai."""
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            clean_results = []
            for r in results:
                clean_results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", "")
                })
            return clean_results if clean_results else [{"message": f"Koi web results nahi mile for: {query}"}]
    except Exception as e:
        return [{"error": f"Web search failed: {e}"}]
