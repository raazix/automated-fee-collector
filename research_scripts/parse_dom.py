import re
with open("dom_dump.html", "r", encoding="utf-8") as f:
    html = f.read()

print("File size:", len(html))
print("contenteditable occurrences:", html.lower().count("contenteditable"))
print("aria-label occurrences:", html.lower().count("aria-label"))
print("data-testid occurrences:", html.lower().count("data-testid"))

import json
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
send_btns = soup.find_all(attrs={"data-testid": "send"})
print(f"Found {len(send_btns)} data-testid=send")

send_icons = soup.find_all(attrs={"data-icon": "send"})
print(f"Found {len(send_icons)} data-icon=send")

aria_send = soup.find_all(attrs={"aria-label": "Send"})
print(f"Found {len(aria_send)} aria-label=Send")

print("All elements with aria-label containing 'end':")
for el in soup.find_all(attrs={"aria-label": lambda x: x and "end" in x.lower()}):
    print(f"Tag: {el.name}, aria-label: {el.get('aria-label')}")
    
print("All contenteditable boxes:")
for el in soup.find_all(attrs={"contenteditable": "true"}):
    print(f"Tag: {el.name}, aria-label: {el.get('aria-label')}, title: {el.get('title')}, class: {el.get('class')}")
    
print("All buttons and roles with send:")
for el in soup.find_all(["button", "div", "span"]):
    if "send" in (el.get("aria-label") or "").lower() or "send" in (el.get("title") or "").lower():
         print(f"Found something with send: {el.name}, aria={el.get('aria-label')}, class={el.get('class')}")
         
print("All input[type='text']:")
for el in soup.find_all("input", type="text"):
    print(f"Input text: aria-label={el.get('aria-label')}, placeholder={el.get('placeholder')}")
