"""Dynamic scanner using Playwright for web application analysis."""

import asyncio
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Browser, Page


class DynamicScanner:
    """Scans web applications dynamically using Playwright."""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.browser: Optional[Browser] = None
    
    async def scan_url(self, url: str, max_depth: int = 3) -> Dict:
        """Scan a web application starting from a URL."""
        if not self.enabled:
            raise RuntimeError("Dynamic scanning is not enabled. Enable in settings first.")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            self.browser = browser
            
            try:
                page = await browser.new_page()
                results = await self._crawl_page(page, url, max_depth, set())
                return results
            finally:
                await browser.close()
                self.browser = None
    
    async def _crawl_page(self, page: Page, url: str, max_depth: int, visited: set) -> Dict:
        """Crawl a page and extract information."""
        if url in visited or max_depth <= 0:
            return {}
        
        visited.add(url)
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            return {"error": str(e), "url": url}
        
        # Extract page information
        title = await page.title()
        content = await page.content()
        
        # Extract links
        links = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links.map(a => a.href).filter(href => href.startsWith('http'));
            }
        """)
        
        # Extract forms
        forms = await page.evaluate("""
            () => {
                const forms = Array.from(document.querySelectorAll('form'));
                return forms.map(form => ({
                    action: form.action,
                    method: form.method,
                    inputs: Array.from(form.querySelectorAll('input')).map(i => ({
                        name: i.name,
                        type: i.type
                    }))
                }));
            }
        """)
        
        # Extract API endpoints (from network requests)
        network_requests = []
        # Note: This would require intercepting requests, simplified here
        
        result = {
            "url": url,
            "title": title,
            "links": links[:20],  # Limit links
            "forms": forms,
            "network_requests": network_requests,
            "content_length": len(content)
        }
        
        # Recursively crawl linked pages (limited)
        if max_depth > 1:
            child_results = []
            for link in links[:5]:  # Limit recursion
                if link not in visited:
                    child_result = await self._crawl_page(page, link, max_depth - 1, visited)
                    if child_result:
                        child_results.append(child_result)
            result["children"] = child_results
        
        return result

