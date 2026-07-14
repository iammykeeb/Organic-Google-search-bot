from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def setup_driver(headless=True):
    options = Options()
    
    # --- Required for Colab / Linux environments ---
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    if headless:
        options.add_argument('--headless')
    options.binary_location = '/usr/bin/chromium-browser'  # change if needed

    # --- Anti-detection (hide automation) ---
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        executable_path='/usr/bin/chromedriver',  # change if needed
        options=options
    )
    
    # Remove webdriver fingerprint
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Page load strategy: 'eager' speeds up loading (don't wait for all resources)
    driver.execute_cdp_cmd('Page.setLifecycleEventsEnabled', {'enabled': True})
    # Alternatively, set the page load strategy via capabilities (if using ChromeOptions)
    # options.set_capability('pageLoadStrategy', 'eager')
    
    return driver

def search_and_click(keyword, target_url=None, visits=1, headless=True):
    """
    Performs a Google search and clicks the target URL (or the first organic result).
    
    Args:
        keyword (str): Search term.
        target_url (str, optional): If provided, only clicks a result that contains
                                    this substring. Otherwise clicks the first link.
        visits (int): Number of times to repeat.
        headless (bool): Run browser in headless mode (faster).
    """
    for i in range(visits):
        driver = None
        try:
            driver = setup_driver(headless=headless)
            
            # Go to Google
            driver.get("https://www.google.com")
            # Accept cookies if the popup appears (quick)
            try:
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="L2AGLb"]'))
                ).click()
            except:
                pass
            
            # Type search and submit
            search_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results to appear (just enough)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # Find the link to click
            if target_url:
                # Find a result containing the target URL
                links = driver.find_elements(By.XPATH, "//a[contains(@href, '{}')]".format(target_url))
                if links:
                    link = links[0]
                else:
                    print(f"⚠️ Target '{target_url}' not found, using first result.")
                    link = driver.find_element(By.XPATH, "//div[@class='yuRUbf']/a")
            else:
                # First organic result (modern Google)
                try:
                    link = driver.find_element(By.XPATH, "//div[@class='yuRUbf']/a")
                except:
                    link = driver.find_element(By.XPATH, "//h3/ancestor::a")
            
            href = link.get_attribute("href")
            print(f"Visit {i+1}: Clicking {href}")
            
            # Click the link
            link.click()
            
            # Optional: wait a short moment for the page to start loading (referrer sent)
            time.sleep(1)  # you can remove or adjust
            
            print(f"✅ Organic click generated for visit {i+1}")
            
        except Exception as e:
            print(f"❌ Error on visit {i+1}: {e}")
        finally:
            if driver:
                driver.quit()
            # Small gap between visits (can be reduced or removed)
            if i < visits - 1:
                time.sleep(random.uniform(1, 3))

# ========== CONFIGURE ==========
KEYWORD = "your search keyword"
TARGET_SITE = "yoursite.com"   # optional: if you want a specific landing page
NUM_VISITS = 5
HEADLESS = True               # Set False to see the browser

search_and_click(KEYWORD, TARGET_SITE, NUM_VISITS, HEADLESS)
