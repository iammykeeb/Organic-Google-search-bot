from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# List of proxies (format: IP:PORT)
PROXY_LIST = [
    "proxy1:8080",
    "proxy2:8080",
    # add more
]

def setup_driver(proxy=None):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def generate_organic_click(keyword, target_url_substring, visits=5):
    for i in range(visits):
        proxy = random.choice(PROXY_LIST) if PROXY_LIST else None
        driver = None
        try:
            driver = setup_driver(proxy)
            driver.get("https://www.google.com")
            time.sleep(random.uniform(1,2))
            # accept cookies
            try:
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="L2AGLb"]'))
                ).click()
            except:
                pass
            search_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.send_keys(keyword + Keys.RETURN)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{target_url_substring}')]")
            if not links:
                links = driver.find_elements(By.XPATH, "//div[@class='yuRUbf']/a")
            if links:
                links[0].click()
                time.sleep(2)
                print(f"✅ Visit {i+1} with proxy {proxy} succeeded.")
            else:
                print(f"❌ Visit {i+1}: no link found.")
        except Exception as e:
            print(f"❌ Visit {i+1} failed: {e}")
        finally:
            if driver:
                driver.quit()
            time.sleep(random.uniform(3,6))
