import sys, os, time, logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)

profile = os.path.abspath(".chrome_wa_profile")
opts = uc.ChromeOptions()
opts.add_argument(f"--user-data-dir={profile}")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=opts, version_main=147)
driver.get("https://web.whatsapp.com/send?phone=917975144876")
wait = WebDriverWait(driver, 30)

try:
    print("Waiting for chatbox...")
    BOX_CSS   = 'div[contenteditable="true"][data-tab="10"]'
    BOX_CSS2  = 'div[contenteditable="true"][data-lexical-editor="true"]'
    
    box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, BOX_CSS + "," + BOX_CSS2)))
    print("Chatbox found.")
    
    # Send a quick text message
    box.send_keys("Test message from selenium!")
    box.send_keys(Keys.ENTER)
    print("Sent test message.")
    
    time.sleep(5)
finally:
    driver.quit()
