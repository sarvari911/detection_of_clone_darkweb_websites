from modules.crawler import crawl
url1 = input("Enter first URL: ")
url2 = input("Enter second URL: ")

crawl(url1, url2)

from modules.extractor import extract_text

text1 = extract_text("data/raw/site1.html")
text2 = extract_text("data/raw/site2.html")

print("\n--- Extracted Text from Site 1 ---\n")
print(text1[:500])   # prints first 500 characters

print("\n--- Extracted Text from Site 2 ---\n")
print(text2[:500])

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer()

vectors = vectorizer.fit_transform([text1, text2])

similarity = cosine_similarity(vectors[0], vectors[1])

print("\nSimilarity Score:", similarity[0][0])

if similarity[0][0] > 0.8:
    print("Result: Clone Website Detected ⚠️")
else:
    print("Result: Not a Clone ✅")