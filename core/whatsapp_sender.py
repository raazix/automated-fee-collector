"""
core/whatsapp_sender.py
All imports at top level — no more missing EC errors.
Text via URL prefill. Image via direct file input send_keys.
"""

import logging
import os
import random
import sys
import time
from typing import Optional
from urllib.parse import quote

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

logger = logging.getLogger(__name__)

WA_URL    = "https://web.whatsapp.com/send?phone={phone}&text={text}"
CHAT_CSS  = '#pane-side, div[aria-label="Chat list"], div[aria-label="Chats"], div[id="side"], div[data-tab="3"]'
BOX_CSS   = 'div[contenteditable="true"][data-tab="10"]'
BOX_CSS2  = 'div[contenteditable="true"][data-lexical-editor="true"]'
SEND_CSS  = 'button[data-testid="send"], span[data-testid="send"], span[data-icon="send"], div[aria-label="Send"], button[aria-label="Send"], div[aria-label^="Send "], span[aria-label^="Send "], button[aria-label^="Send "]'
BAD_PHONE = "Phone number shared via url is invalid"


def _detect_chrome_major_version() -> Optional[int]:
    """Detect installed Google Chrome major version dynamically on Windows."""
    try:
        import winreg
        for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for subkey in (
                r"Software\Google\Chrome\BLBeacon",
                r"Software\Wow6432Node\Google\Update\Clients\{8A69D345-D564-463c-AFF1-A69D9E530F96}",
            ):
                try:
                    with winreg.OpenKey(root, subkey) as key:
                        val, _ = winreg.QueryValueEx(key, "version")
                        if val:
                            return int(val.split(".")[0])
                except Exception:
                    pass
    except Exception:
        pass
    return None


class WhatsAppSender:

    def __init__(self):
        self.driver: Optional[object] = None
        self._profile = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         "..", ".chrome_wa_profile")
        )

    def __enter__(self):
        self._launch()
        return self

    def __exit__(self, *_):
        self.quit()

    def _launch(self):
        import undetected_chromedriver as uc

        logger.info("Launching Chrome (undetected)...")
        opts = uc.ChromeOptions()
        opts.add_argument(f"--user-data-dir={self._profile}")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        major_ver = _detect_chrome_major_version()
        if major_ver:
            logger.info(f"Detected Chrome major version: {major_ver}")
            self.driver = uc.Chrome(options=opts, version_main=major_ver)
        else:
            self.driver = uc.Chrome(options=opts)

        self.driver.maximize_window()
        self.driver.get("https://web.whatsapp.com")

        logger.info(
            "Waiting for WhatsApp Web...\n"
            "  >>> FIRST RUN ONLY: Scan the QR code in the browser window with your phone. <<<"
        )
        login_timeout = max(180, config.WA_LOAD_TIMEOUT * 2)
        WebDriverWait(self.driver, login_timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, CHAT_CSS))
        )
        logger.info("WhatsApp Web is ready.")

    def quit(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def send(self, phone, message, qr_path, name=""):
        label = name or phone
        for attempt in range(1, config.MAX_RETRIES + 2):
            try:
                if self._once(phone, message, qr_path):
                    logger.info(f"  [OK] {label} (attempt {attempt})")
                    return True
            except Exception as exc:
                logger.warning(f"  [ERR] {label} attempt {attempt}: {exc}")
            if attempt <= config.MAX_RETRIES:
                logger.info("  Retrying in 5s...")
                time.sleep(5)
        logger.error(f"  [FAIL] {label}")
        return False

    @staticmethod
    def random_delay():
        d = random.uniform(config.SEND_DELAY_MIN, config.SEND_DELAY_MAX)
        logger.info(f"  Waiting {d:.1f}s before next message...")
        time.sleep(d)

    def _find_box(self, wait):
        for css in (BOX_CSS, BOX_CSS2):
            try:
                return wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, css))
                )
            except Exception:
                continue
        return None

    def _click_send(self, wait, fallback=None):
        """Click Send button via JS. Falls back to Enter key."""
        try:
            btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SEND_CSS))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView(); arguments[0].click();", btn
            )
            return True
        except Exception:
            if fallback:
                try:
                    fallback.send_keys(Keys.ENTER)
                    return True
                except Exception:
                    pass
        return False

    def _attach_image(self, qr_path, wait):
        """
        Click paperclip, click 'Photos & videos', intercept the hidden file input
        and send file path directly to it — no OS dialog opens.
        """
        abs_path = os.path.abspath(qr_path)
        
        # Override click to intercept OS file dialog
        self.driver.execute_script("""
            window.interceptedFileInput = null;
            if (!HTMLInputElement.prototype._originalClick) {
                HTMLInputElement.prototype._originalClick = HTMLInputElement.prototype.click;
                HTMLInputElement.prototype.click = function() {
                    if (this.type === 'file') {
                        window.interceptedFileInput = this;
                    } else {
                        this._originalClick();
                    }
                };
            }
        """)

        # 1. Click paperclip and wait for 'Photos & videos'
        photo_btn = None
        photo_selector = (
            'button[aria-label="Photos & videos"], '
            'li[aria-label="Photos & videos"], '
            'span[aria-label="Photos & videos"], '
            'button[aria-label="Photos and videos"], '
            'li[aria-label="Photos and videos"], '
            'div[aria-label="Photos & videos"], '
            'div[aria-label="Photos and videos"]'
        )
        attach_selector = (
            'div[title="Attach"], '
            'button[title="Attach"], '
            'div[aria-label="Attach"], '
            'button[aria-label="Attach"], '
            '[data-testid="clip"], '
            'span[data-icon="clip"], '
            'span[data-icon="plus"]'
        )

        for clip_attempt in range(2):
            try:
                attach = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, attach_selector))
                )
                time.sleep(0.3)
                try:
                    attach.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", attach)

                logger.info("  Paperclip clicked.")
                
                short_wait = WebDriverWait(self.driver, 5)
                photo_btn = short_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, photo_selector))
                )
                if photo_btn:
                    break
            except Exception:
                logger.warning(f"  Attach menu attempt {clip_attempt + 1} retry...")
                time.sleep(0.8)

        if not photo_btn:
            logger.warning("  Photos & videos button not found after retries.")
            return False

        try:
            self.driver.execute_script("arguments[0].click();", photo_btn)
            logger.info("  Clicked 'Photos & videos'.")
            time.sleep(0.4)
        except Exception as e:
            logger.warning(f"  Failed clicking Photos & videos: {e}")
            return False

        # 3. Retrieve the intercepted input
        inp = self.driver.execute_script("return window.interceptedFileInput;")
        if not inp:
            logger.warning("  Failed to intercept file input.")
            return False

        # 4. Unhide and send keys to the intercepted input
        try:
            self.driver.execute_script(
                """
                arguments[0].style.display    = 'block';
                arguments[0].style.visibility = 'visible';
                arguments[0].style.opacity    = '1';
                arguments[0].style.height     = '1px';
                arguments[0].style.width      = '1px';
                """,
                inp
            )
            time.sleep(0.2)
            inp.send_keys(abs_path)
            logger.info("  Path sent to intercepted input — waiting for preview...")
            time.sleep(1.2)

            # Confirm preview loaded — Send button becomes active
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, SEND_CSS)
                    )
                )
                logger.info("  Image preview confirmed.")
                return True
            except Exception:
                logger.info("  Image preview not confirmed, but proceeding...")
                return True

        except Exception as e:
            logger.warning(f"  Error sending path to intercepted input: {e}")
            return False

    def _once(self, phone, message, qr_path):
        has_image = bool(qr_path and os.path.isfile(qr_path))
        if not has_image:
            logger.warning(f"QR image missing: {qr_path}")

        # ── Step 1: Open chat ────────────────────
        # If we have an image, we open empty chat URL.
        # Otherwise (original text-only mode), prefill text via URL.
        use_url_text = not has_image
        encoded = quote(message) if use_url_text else ""
        self.driver.get(WA_URL.format(phone=phone, text=encoded))
        time.sleep(random.uniform(1.5, 2.5))

        wait = WebDriverWait(self.driver, 20)

        # Check for invalid phone
        try:
            WebDriverWait(self.driver, 4).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//*[contains(text(),'{BAD_PHONE}')]")
                )
            )
            logger.error(f"Invalid phone: {phone}")
            return False
        except Exception:
            pass

        # Confirm chat loaded
        box = self._find_box(wait)
        if box is None:
            raise RuntimeError("Chat did not load.")

        if not has_image:
            # ── Step 2: Send text only ────────────────────
            logger.info("  Sending text...")
            self._click_send(wait, fallback=box)
            time.sleep(3.0)
        else:
            # ── Step 3: Attach image and send with caption ────────────────────────────
            logger.info("  Attaching QR image...")
            preview_ok = self._attach_image(qr_path, wait)

            if preview_ok:
                logger.info("  Typing caption and sending...")
                try:
                    caption_selector = 'div[contenteditable="true"][aria-label="Type a message"], div[contenteditable="true"][aria-label="Add a caption"]'
                    caption_boxes = self.driver.find_elements(By.CSS_SELECTOR, caption_selector)
                    
                    if caption_boxes:
                        caption_box = caption_boxes[0]
                        # Type each line and press Shift+Enter to preserve line breaks in WhatsApp Web
                        lines = message.split("\n")
                        for idx, line in enumerate(lines):
                            if line:
                                self.driver.execute_script("""
                                    var el = arguments[0];
                                    var text = arguments[1];
                                    el.focus();
                                    if (typeof window.getSelection != 'undefined' && typeof document.createRange != 'undefined') {
                                        var range = document.createRange();
                                        range.selectNodeContents(el);
                                        range.collapse(false);
                                        var sel = window.getSelection();
                                        sel.removeAllRanges();
                                        sel.addRange(range);
                                    }
                                    document.execCommand('insertText', false, text);
                                """, caption_box, line)
                            if idx < len(lines) - 1:
                                caption_box.send_keys(Keys.SHIFT + Keys.ENTER)
                                time.sleep(0.05)
                        time.sleep(0.3)
                        
                        logger.info("  Sending image with caption...")
                        sent = False
                        
                        # Attempt 1: Selenium click the send button
                        try:
                            send_btns = self.driver.find_elements(By.CSS_SELECTOR, SEND_CSS)
                            if send_btns:
                                btn = send_btns[-1]
                                btn.click()
                                sent = True
                        except Exception:
                            pass
                            
                        # Attempt 2: Press ENTER in the caption box
                        if not sent:
                            try:
                                caption_box.send_keys(Keys.ENTER)
                                sent = True
                            except Exception:
                                pass

                        # Attempt 3: JS click
                        if not sent:
                            try:
                                if send_btns:
                                    self.driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", send_btns[-1])
                                    sent = True
                            except Exception:
                                pass
                                
                        if sent:
                            time.sleep(1.2)
                            logger.info("  Image sent.")
                            return True
                        else:
                            logger.warning("  Send button not found or failed to click.")
                            return False
                    else:
                        logger.warning("  Caption box not found.")
                        return False
                except Exception as e:
                    logger.warning(f"  Failed to set caption or click send: {e}")
                    return False
            else:
                logger.warning("  Image not sent — preview failed.")
                return False

        return True