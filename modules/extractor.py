from bs4 import BeautifulSoup

def extract_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style
    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text(separator=" ")

    # Clean text
    lines = [line.strip() for line in text.splitlines()]
    clean_text = " ".join([line for line in lines if line])

    return clean_text
