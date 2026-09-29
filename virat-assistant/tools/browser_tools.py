from playwright.sync_api import sync_playwright, Page, Browser

class BrowserAgent:
    def __init__(self):
        self._pw = None
        self._browser = None
        self._page: Page = None

    def _ensure_session(self):
        if not self._browser or not self._browser.is_connected():
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=False, args=["--start-maximized"])
            context = self._browser.new_context(no_viewport=True)
            self._page = context.new_page()

    def search_youtube(self, query: str) -> str:
        self._ensure_session()
        self._page.goto(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
        
        # Primary result title selector on YouTube desktop
        title_selector = "ytd-video-renderer #video-title"
        self._page.wait_for_selector(title_selector, timeout=12000)
        self._page.click(title_selector)
        return f"Streaming top YouTube result for '{query}'"

    def interact(self, action_type: str) -> str:
        if not self._page:
            return "No active browser session detected."
        try:
            if action_type == "like":
                selector = "like-button-view-model button, button[aria-label*='like this video']"
                self._page.wait_for_selector(selector, timeout=5000)
                self._page.click(selector)
                return "Liked the currently playing video."
            elif action_type == "subscribe":
                selector = "ytd-subscribe-button-renderer button, button[aria-label*='Subscribe']"
                self._page.wait_for_selector(selector, timeout=5000)
                self._page.click(selector)
                return "Subscribed to channel."
        except Exception as e:
            return f"Interaction failed: {str(e)}"
        return "Unknown web interaction."

    def terminate(self):
        if self._browser:
            self._browser.close()
            self._pw.stop()
            self._browser = None