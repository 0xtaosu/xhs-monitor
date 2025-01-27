import logging
from playwright.sync_api import sync_playwright
from time import sleep

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def xhs_sign(uri, data=None, a1="", web_session=""):
    attempt = 0
    for _ in range(10):
        attempt += 1
        logger.info(f"Attempt {attempt}/10: Trying to sign request for URI: {uri}")
        try:
            with sync_playwright() as playwright:
                stealth_js_path = "public/stealth.min.js"
                chromium = playwright.chromium
                logger.debug("Launching browser...")
                browser = chromium.launch(headless=True)

                browser_context = browser.new_context()
                browser_context.add_init_script(path=stealth_js_path)
                context_page = browser_context.new_page()
                logger.info("Navigating to xiaohongshu.com...")
                context_page.goto("https://www.xiaohongshu.com")
                
                logger.debug(f"Setting cookies - a1: {a1[:10]}...")
                browser_context.add_cookies([
                    {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
                )
                context_page.reload()
                logger.debug("Waiting after cookie setup...")
                sleep(1)
                
                logger.info("Attempting to get signature...")
                encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                logger.info("Successfully obtained signature")
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
            if attempt == 10:
                logger.error("All attempts exhausted")
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")
