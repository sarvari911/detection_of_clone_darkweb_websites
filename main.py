from modules.crawler import crawl
from modules.extractor import extract_features
from modules.model import compute_final_score, predict_with_ml

def main():
    url1 = input("Enter first URL: ")
    url2 = input("Enter second URL: ")

    # Step 1: Crawl
    crawl(url1, url2)

    # Step 2: Extract features
    data1 = extract_features("data/raw/site1.html")
    data2 = extract_features("data/raw/site2.html")

    # Debug info
    print("\n🔍 Wallets in Site 1:", data1["wallets"])
    print("🔍 Wallets in Site 2:", data2["wallets"])

    # Step 3: Rule-based scoring
    score, details = compute_final_score(data1, data2)

    print("\n📊 Feature Scores:")
    print(details)

    print("\n🔢 Final Score:", score)

    # Step 4: Rule-based decision
    if score >= 0.8:
        print("🚨 Clone Website Detected")
    elif score >= 0.5:
        print("⚠️ Suspicious Website")
    else:
        print("✅ Safe Website")

    # Step 5: ML prediction
    ml_result = predict_with_ml(data1, data2)

    if ml_result == 1:
        print("🤖 ML Prediction: Clone Website")
    else:
        print("🤖 ML Prediction: Safe Website")


if __name__ == "__main__":
    main()