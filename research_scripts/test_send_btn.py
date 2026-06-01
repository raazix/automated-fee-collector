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
    
    attach_selector = 'div[aria-label="Attach"], button[aria-label="Attach"], div[title="Attach"], button[title="Attach"]'
    attach = driver.find_element(By.CSS_SELECTOR, attach_selector)
    driver.execute_script("arguments[0].click();", attach)
    print("Clicked Attach button.")
    time.sleep(2)
    
    inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
    with open("dummy.png", "wb") as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
    abs_path = os.path.abspath("dummy.png")
    
    inp = inputs[0]
    driver.execute_script(
        """
        arguments[0].style.display    = 'block';
        arguments[0].style.visibility = 'visible';
        arguments[0].style.opacity    = '1';
        arguments[0].style.height     = '1px';
        arguments[0].style.width      = '1px';
        """,
        inp
    )
    inp.send_keys(abs_path)
    print("Sent file path.")
    time.sleep(5)
    
    SEND_CSS  = 'button[data-testid="send"], span[data-testid="send"], span[data-icon="send"], div[aria-label="Send"], button[aria-label="Send"], div[role="button"][aria-label="Send"]'
    send_btns = driver.find_elements(By.CSS_SELECTOR, SEND_CSS)
    print(f"Found {len(send_btns)} send buttons.")
    for i, b in enumerate(send_btns):
        print(f"Send btn {i}: tag={b.tag_name}, class={b.get_attribute('class')}, displayed={b.is_displayed()}")
        
    # Let's try JS click first to see if it actually sends
    for b in send_btns:
        if b.is_displayed():
            try:
                print("Trying JS click...")
                driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", b)
                time.sleep(2)
                print("JS clicked.")
            except Exception as e:
                print(f"JS click failed: {e}")
                
            # If still here (not sent and page didn't change), try Selenium click
            try:
                print("Trying Selenium click...")
                b.click()
                print("Selenium clicked successfully!")
            except Exception as e:
                print(f"Selenium click failed: {e}")
                
    time.sleep(3)
finally:
    driver.quit()
    if os.path.exists("dummy.png"):
        os.remove("dummy.png")
