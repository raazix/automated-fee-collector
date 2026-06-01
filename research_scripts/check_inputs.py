import sys, os, time, logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, BOX_CSS + "," + BOX_CSS2)))
    print("Chatbox found.")
    time.sleep(3)
    
    inputs_before = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
    print(f"Inputs before click: {len(inputs_before)}")
    for i, inp in enumerate(inputs_before):
        print(f"  {i}: accept={inp.get_attribute('accept')}")
        
    attach_selector = 'div[aria-label="Attach"], button[aria-label="Attach"], div[title="Attach"], button[title="Attach"]'
    attach = driver.find_element(By.CSS_SELECTOR, attach_selector)
    driver.execute_script("arguments[0].click();", attach)
    print("Clicked Attach button.")
    time.sleep(2)
    
    inputs_after = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
    print(f"Inputs after click: {len(inputs_after)}")
    for i, inp in enumerate(inputs_after):
        print(f"  {i}: accept={inp.get_attribute('accept')}")

finally:
    driver.quit()
