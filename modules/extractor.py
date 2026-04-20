from bs4 import BeautifulSoup
import re

def extract_features(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # 🔹 Remove unwanted tags
    for tag in soup(["script", "style"]):
        tag.decompose()

    # -------------------------
    # 1. TEXT
    # -------------------------
    text = soup.get_text(separator=" ")
    text = " ".join(text.split())

    # -------------------------
    # 2. TAG FREQUENCY
    # -------------------------
    tag_freq = {}
    for tag in soup.find_all():
        tag_name = tag.name
        tag_freq[tag_name] = tag_freq.get(tag_name, 0) + 1

    # -------------------------
    # 3. LINKS
    # -------------------------
    links = []
    for a in soup.find_all("a", href=True):
        links.append(a["href"])

    # -------------------------
    # 4. CRYPTO WALLET DETECTION
    # -------------------------
    wallets = []

    # Bitcoin pattern (basic)
    btc_pattern = r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b"
    wallets += re.findall(btc_pattern, text)

    # Ethereum pattern
    eth_pattern = r"\b0x[a-fA-F0-9]{40}\b"
    wallets += re.findall(eth_pattern, text)

    return {
        "text": text,
        "tag_freq": tag_freq,
        "links": links,
        "wallets": wallets
    }
