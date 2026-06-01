# Research Scripts Guide

This folder contains the experimental scripts that were created during the debugging session to reverse-engineer WhatsApp Web's latest UI updates and fix the automated messaging system. 

If you are a developer looking to understand how to bypass WhatsApp Web's bot detection or file upload limitations, these scripts show the exact step-by-step progress of how we solved the issues.

All scripts use **Python**, **Selenium**, and **undetected-chromedriver** as their primary tools.

---

### 1. `dump_dom.py`
**Why it was used:** WhatsApp Web is a complex React application where elements dynamically load and disappear. We needed to see the exact HTML structure of the page after the "Attach" button was clicked.
**What it does:** It opens WhatsApp Web, clicks the paperclip attach button, and saves the entire raw HTML (DOM) of the page into a massive file called `dom_dump.html`.
**Tools used:** `selenium` (for clicking), file I/O (for saving the HTML).

### 2. `parse_dom.py`
**Why it was used:** The `dom_dump.html` file generated was over 1.2MB and contained on a single line of text, making standard text search tools fail. We needed a programmatic way to find the hidden buttons and input fields.
**What it does:** It reads the dumped HTML file and uses `BeautifulSoup` to search for specific elements. For example, it counted how many `<input type="file">` elements existed, and found the exact `aria-label` for the "Photos & videos" button.
**Tools used:** `BeautifulSoup4` (HTML parsing library), `re` (Regular Expressions).

### 3. `check_inputs.py`
**Why it was used:** We needed to figure out if WhatsApp Web changes the available file upload boxes when a user clicks the "Attach" button.
**What it does:** It counts the number of `<input type="file">` elements *before* clicking the attach button, clicks it, and then counts them again *after*. It also prints out the `accept` attribute (e.g., `image/*`) to see if the input is meant for Photos, Documents, or Stickers.

### 4. `test_wa.py`
**Why it was used:** A baseline test to make sure `undetected-chromedriver` was successfully bypassing WhatsApp's anti-bot protections.
**What it does:** It simply logs into WhatsApp Web, waits for the chat box to appear, and sends a basic text message using Selenium's `send_keys(Keys.ENTER)`.

### 5. `test_wa_attach.py`
**Why it was used:** To test the basic file upload mechanism.
**What it does:** It finds the hidden file upload `<input>`, unhides it using a Javascript CSS injection (`style.display = 'block'`), and sends a dummy QR code directly into it. *Note: This script caused the "Sticker Bug" because it bypassed the "Photos & videos" button, leading WhatsApp to guess the file type incorrectly.*

### 6. `test_send_btn.py`
**Why it was used:** After an image was successfully attached, the script was timing out because it couldn't find the "Send" button on the image preview screen.
**What it does:** It uploads an image to trigger the preview screen, then uses a generic CSS search to find *any* button on the screen that looks like a Send button. It revealed that WhatsApp changed the button's internal label to `aria-label="Send 1 selected"` instead of just `Send`.

### 7. `test_intercept.py` (The Masterpiece)
**Why it was used:** To solve the "Sticker Bug." If we used `test_wa_attach.py`, WhatsApp assumed PNGs were stickers. If we clicked the "Photos & videos" button natively, it opened a Windows File Explorer popup which Selenium cannot control.
**What it does:** It injects a Javascript spell (`HTMLInputElement.prototype.click` override) into the browser. When it clicks the "Photos & videos" button, instead of opening the Windows file popup, the Javascript catches the exact file upload box WhatsApp *intended* to use and saves it to a variable. We then pass our image directly into that intercepted box.
**Result:** WhatsApp is successfully tricked into opening the standard Photo Preview window, complete with the caption box!
