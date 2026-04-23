from modules.crawler import crawl
from modules.extractor import extract_features
from modules.model import compute_final_score, predict_with_ml


def main():
    url1 = input("Enter first URL: ")
    url2 = input("Enter second URL: ")

    print("\n🔄 Crawling...")
    crawl(url1, url2)

    print("\n🔍 Extracting features...")
    data1 = extract_features("data/raw/site1.html")
    data2 = extract_features("data/raw/site2.html")

    print("\n📊 Computing similarity...")
    score, details = compute_final_score(data1, data2)

    print("\nFeature Scores:", details)
    print("Final Score:", score)

    if score >= 0.8:
        print("🚨 Clone Website Detected")
    elif score >= 0.5:
        print("⚠️ Suspicious Website")
    else:
        print("✅ Safe Website")

    print("\n🤖 ML Prediction...")
    ml_result, prob = predict_with_ml(data1, data2)

    print(f"Confidence: {prob:.2f}")

    if ml_result == 1:
        print("🤖 Clone Website")
    else:
        print("🤖 Safe Website")


if __name__ == "__main__":
    main()