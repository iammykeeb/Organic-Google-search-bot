from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_google_redirect_url(keyword, target_landing_url):
    """
    Returns the Google redirect URL (the one with /url?q=...&ved=...)
    that, when clicked, counts as an organic click in GSC.
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        driver.get("https://www.google.com")
        # Accept cookies if needed
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="L2AGLb"]'))
            ).click()
        except:
            pass

        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        # Wait for results
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "search"))
        )

        # Find the result link that points to your landing page
        # We look for any <a> whose href contains the landing URL
        link_elements = driver.find_elements(By.XPATH, f"//a[contains(@href, '{target_landing_url}')]")
        if not link_elements:
            # If not found, take the first organic result
            link_elements = driver.find_elements(By.XPATH, "//div[@class='yuRUbf']/a")
            if not link_elements:
                link_elements = driver.find_elements(By.XPATH, "//h3/ancestor::a")

        if not link_elements:
            raise RuntimeError("No result link found.")

        # The href is the Google redirect URL (starts with /url?q=...)
        redirect_url = link_elements[0].get_attribute("href")
        # If it's relative, prepend domain
        if redirect_url.startswith("/url?"):
            redirect_url = "https://www.google.com" + redirect_url

        print(f"✅ Generated redirect URL:\n{redirect_url}")
        return redirect_url

    finally:
        driver.quit()

# ========== CONFIGURE ==========
KEYWORD = "your search keyword"
LANDING_PAGE = "yoursite.com"   # e.g., "example.com/product"

if __name__ == "__main__":
    url = get_google_redirect_url(KEYWORD, LANDING_PAGE)
    # Now you can copy this URL and use it in your Facebook ad.
