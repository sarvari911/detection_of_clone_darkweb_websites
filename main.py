from modules.crawler import crawl
from modules.extractor import extract_features
from modules.model import compute_final_score

def main():
    url1 = input("Enter first URL: ")
    url2 = input("Enter second URL: ")

    # Step 1: Crawl
    crawl(url1, url2)

    # Step 2: Extract features
    data1 = extract_features("data/raw/site1.html")
    data2 = extract_features("data/raw/site2.html")

    # Debug info (useful for viva)
    print("\n🔍 Wallets found in Site 1:", data1["wallets"])
    print("🔍 Wallets found in Site 2:", data2["wallets"])

    # Step 3: Compute similarity
    score, details = compute_final_score(data1, data2)

    print("\n📊 Detailed Scores:")
    print(details)

    print("\n🔢 Final Score:", score)

    # Step 4: Decision
    if score >= 0.8:
        print("🚨 Clone Website Detected")
    elif score >= 0.5:
        print("⚠️ Suspicious Website")
    else:
        print("✅ Safe Website")

if __name__ == "__main__":
    main()
