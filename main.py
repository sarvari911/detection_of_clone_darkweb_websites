"""
Dark Web Clone Detection System
Main entry point - ties all modules together
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from modules.tor_handle import TorHandler
from modules.darkweb_crawler import DarkWebCrawler
from modules.extractor import FeatureExtractor
from modules.model import CloneDetector
from modules.reporter import ReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup():
    """Initialize everything"""
    print("\n" + "=" * 60)
    print("🌐 DARK WEB CLONE DETECTION SYSTEM")
    print("=" * 60)

    # Create directories
    Config.create_directories()

    # Check Tor Browser
    print("\n📡 Checking Tor connection...")
    tor = TorHandler(proxy_port=9150)

    if not tor.is_tor_running():
        print("\n❌ Tor is NOT running!")
        print("\nPlease:")
        print("  1. Open Tor Browser")
        print("  2. Wait for it to connect")
        print("  3. Keep it open")
        print("  4. Run this program again")
        return False

    print("✅ Tor is running on port 9150")

    # Verify we can reach Tor network
    crawler = DarkWebCrawler(proxy_port=9150)
    if not crawler.verify_connection():
        print("\n❌ Cannot connect through Tor")
        return False

    print("\n✅ System ready!")
    return True


def crawl_and_detect(original_url, suspect_url):
    """
    Crawl two sites and detect cloning

    Args:
        original_url: Original .onion site
        suspect_url: Suspected clone .onion site
    """
    crawler = DarkWebCrawler(proxy_port=9150)

    # Step 1: Crawl both sites
    print("\n" + "=" * 60)
    print("📡 PHASE 1: CRAWLING")
    print("=" * 60)

    original_data = crawler.fetch_page(original_url)

    if not original_data:
        print("\n❌ Failed to crawl original site")
        return None

    # Wait between requests
    print(f"\n⏳ Waiting 15 seconds before next request...")
    time.sleep(15)

    suspect_data = crawler.fetch_page(suspect_url)

    if not suspect_data:
        print("\n❌ Failed to crawl suspect site")
        return None

    # Save both
    print("\n💾 Saving crawled data...")
    path1 = crawler.save_page(original_data)
    path2 = crawler.save_page(suspect_data)

    # Step 2: Extract features using teammate's extractor
    print("\n" + "=" * 60)
    print("📊 PHASE 2: FEATURE EXTRACTION")
    print("=" * 60)

    extractor = FeatureExtractor()

    print(f"\n📄 Extracting features from original...")
    features1 = extractor.extract_all(original_data['html'], original_data['title'])

    print(f"📄 Extracting features from suspect...")
    features2 = extractor.extract_all(suspect_data['html'], suspect_data['title'])

    print(f"   Original: {len(features1.get('html_structure', {}))} tag types found")
    print(f"   Suspect:  {len(features2.get('html_structure', {}))} tag types found")

    # Step 3: Compare using teammate's model
    print("\n" + "=" * 60)
    print("🔍 PHASE 3: CLONE DETECTION")
    print("=" * 60)

    detector = CloneDetector(threshold=0.85)
    result = detector.compare(features1, features2)

    if result:
        # Print the report from model
        detector.print_report(result)

        # Save detection result JSON
        save_dir = Path('data/features')
        save_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = save_dir / f"detection_result_{timestamp}.json"

        result['original_url'] = original_url
        result['suspect_url'] = suspect_url

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"💾 Detection result saved: detection_result_{timestamp}.json")

        # Step 4: Generate final report
        print("\n" + "=" * 60)
        print("📄 PHASE 4: GENERATING REPORTS")
        print("=" * 60)

        reporter = ReportGenerator()
        report = reporter.generate(
            original_url=original_url,
            suspect_url=suspect_url,
            original_data=original_data,
            suspect_data=suspect_data,
            detection_result=result
        )

        reporter.print_console(report)
        reporter.save_json(report)
        reporter.save_html(report)

    return result


def show_menu():
    """Display main menu"""
    print("\n" + "=" * 60)
    print("MAIN MENU")
    print("=" * 60)
    print("1. Crawl & Compare two .onion sites")
    print("2. Compare already-crawled pages")
    print("3. Crawl a single .onion site")
    print("4. View saved results")
    print("5. Exit")
    print("-" * 60)


def compare_saved_pages():
    """Compare two already-crawled pages from data/raw"""
    raw_dir = Path('data/raw')
    json_files = list(raw_dir.glob('page_*.json'))

    if len(json_files) < 2:
        print(f"\n❌ Need at least 2 crawled pages. Found: {len(json_files)}")
        print("Use option 1 or 3 to crawl pages first")
        return

    print(f"\n📁 Available pages ({len(json_files)}):")
    for i, f in enumerate(json_files, 1):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                title = data.get('title', 'No title')[:60]
            print(f"  {i}. {f.name} - {title}")
        except:
            print(f"  {i}. {f.name}")

    try:
        choice1 = int(input("\nSelect ORIGINAL page number: ")) - 1
        choice2 = int(input("Select SUSPECT page number: ")) - 1

        file1 = str(json_files[choice1])
        file2 = str(json_files[choice2])

        # Load pages
        with open(file1, 'r', encoding='utf-8') as f:
            page1 = json.load(f)
        with open(file2, 'r', encoding='utf-8') as f:
            page2 = json.load(f)

        # Step 1: Extract features
        extractor = FeatureExtractor()
        print("\n📊 Extracting features...")
        features1 = extractor.extract_all(page1['html'], page1['title'])
        features2 = extractor.extract_all(page2['html'], page2['title'])

        # Step 2: Compare
        detector = CloneDetector()
        result = detector.compare(features1, features2)

        if result:
            detector.print_report(result)

            # Save detection result
            save_dir = Path('data/features')
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = save_dir / f"detection_result_{timestamp}.json"
            result['original_url'] = page1.get('url', '')
            result['suspect_url'] = page2.get('url', '')

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"💾 Detection result saved: detection_result_{timestamp}.json")

            # Step 3: Generate report
            print("\n📄 Generating reports...")
            reporter = ReportGenerator()
            report = reporter.generate(
                original_url=page1.get('url', ''),
                suspect_url=page2.get('url', ''),
                original_data=page1,
                suspect_data=page2,
                detection_result=result
            )
            reporter.print_console(report)
            reporter.save_json(report)
            reporter.save_html(report)

    except (ValueError, IndexError):
        print("❌ Invalid selection")
    except Exception as e:
        print(f"❌ Error: {e}")


def crawl_single():
    """Crawl a single .onion site"""
    url = input("\nEnter .onion URL: ").strip()

    if not url:
        print("❌ URL cannot be empty")
        return

    crawler = DarkWebCrawler(proxy_port=9150)
    data = crawler.fetch_page(url)

    if data:
        crawler.save_page(data)
        print(f"\n✅ Crawled: {data['title'][:80]}")


def view_results():
    """View saved detection results"""
    features_dir = Path('data/features')
    result_files = list(features_dir.glob('detection_result_*.json'))

    if not result_files:
        print("\n❌ No detection results found")
        print("Use option 1 or 2 to run clone detection first")
        return

    print(f"\n📁 Saved results ({len(result_files)}):")
    for i, f in enumerate(result_files, 1):
        print(f"  {i}. {f.name}")

    try:
        choice = int(input("\nSelect result to view (0 to cancel): "))
        if choice == 0:
            return

        filepath = result_files[choice - 1]

        with open(filepath, 'r', encoding='utf-8') as f:
            result = json.load(f)

        print("\n" + "=" * 60)
        print("📊 SAVED DETECTION RESULT")
        print("=" * 60)
        print(f"Original URL: {result.get('original_url', 'N/A')}")
        print(f"Suspect URL:  {result.get('suspect_url', 'N/A')}")
        print(f"Similarity:   {result.get('similarity_score', 0):.2%}")
        print(f"Threshold:    {result.get('threshold', 0):.2%}")
        print(f"Verdict:      {result.get('verdict', 'N/A')}")
        print("=" * 60)

        if 'breakdown' in result:
            print("\n📋 Feature Breakdown:")
            for item in result['breakdown'][:5]:
                print(f"   {item.get('indicator', '')} {item.get('explanation', '')}: {item.get('raw_score', 0):.1%}")

    except (ValueError, IndexError):
        print("❌ Invalid selection")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main program loop"""
    if not setup():
        return

    while True:
        show_menu()
        choice = input("\nEnter choice (1-5): ").strip()

        if choice == '1':
            print("\nEnter .onion URLs to compare:")
            url1 = input("Original site URL: ").strip()
            url2 = input("Suspect site URL: ").strip()

            if url1 and url2:
                crawl_and_detect(url1, url2)
            else:
                print("❌ Both URLs required")

        elif choice == '2':
            compare_saved_pages()

        elif choice == '3':
            crawl_single()

        elif choice == '4':
            view_results()

        elif choice == '5':
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice (1-5)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")