from modules.crawler import crawl
from modules.extractor import extract_text
from modules.model import compute_similarity

url1 = input("Enter first URL: ")
url2 = input("Enter second URL: ")

# Step 1: Crawl
crawl(url1, url2)

# Step 2: Extract
text1 = extract_text("data/raw/site1.html")
text2 = extract_text("data/raw/site2.html")

# Step 3: Compare
score = compute_similarity(text1, text2)

print("\nSimilarity Score:", score)

# Step 4: Decision
if score > 0.8:
    print("Result: Clone Website Detected 🚨")
else:
    print("Result: Not a Clone ✅")
