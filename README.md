# security_aware_platform
# 🕵️ Dark Web Clone Website Detection System

A Python-based system that crawls `.onion` dark web sites through Tor and detects cloned/phishing websites by comparing structural fingerprints.

---

## 📋 Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Web Dashboard](#web-dashboard)
- [How It Works](#how-it-works)
- [Sample Output](#sample-output)
- [Safety & Ethics](#safety--ethics)
- [Team](#team)
- [License](#license)

---

## ✨ Features

- 🔒 **Anonymous Crawling** - Crawls `.onion` sites through Tor network
- 🔍 **Clone Detection** - Compares HTML structure, CSS, forms, scripts, and meta tags
- 📊 **Weighted Scoring** - Each feature is weighted by importance for accurate detection
- 🌐 **Web Dashboard** - User-friendly Flask dashboard with real-time results
- 📄 **Report Generation** - HTML and JSON reports for documentation
- 💾 **Data Persistence** - Saves crawled pages and detection history

---

## 📂 Project Structure
detection_of_clone_darkweb_websites/
│
├── modules/
│ ├── darkweb_crawler.py # Tor-based .onion crawler
│ ├── tor_handle.py # Tor connection manager
│ ├── extractor.py # Feature extraction from HTML
│ ├── model.py # Clone detection algorithm
│ └── reporter.py # Report generation (JSON/HTML)
│
├── dashboard/
│ ├── app.py # Flask web dashboard
│ └── templates/
│ └── dashboard.html # Dashboard UI
│
├── data/
│ ├── raw/ # Crawled page data
│ ├── features/ # Extracted features & results
│ └── dataset/ # Training datasets
│
├── output/ # Generated reports
├── logs/ # Application logs
├── main.py # CLI entry point
├── config.py # Configuration settings
├── requirements.txt # Python dependencies
└── README.md # This file

text

---

## 📦 Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.8+ | Runtime |
| Tor Browser | Latest | Anonymous routing |
| Flask | 3.0+ | Web dashboard |

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sarvari911/detection_of_clone_darkweb_websites.git
cd detection_of_clone_darkweb_websites
2. Install Python Dependencies
bash
pip install -r requirements.txt
3. Download & Install Tor Browser
Download from: https://www.torproject.org/download/

Install and keep it open while running the system

4. Configure Environment
The .env file is already configured for Tor Browser (port 9150):

text
TOR_PROXY_PORT=9150
REQUEST_TIMEOUT=60
SIMILARITY_THRESHOLD=0.85
💻 Usage
Command Line Interface
bash
python main.py
Menu Options:

Option	Description
1	Crawl & Compare two .onion sites
2	Compare already-crawled pages
3	Crawl a single .onion site
4	View saved detection results
5	Exit
Web Dashboard
bash
cd dashboard
python app.py
Open: http://127.0.0.1:5000

🧠 How It Works
Phase 1: Crawling
text
User Input (.onion URLs)
        ↓
Tor Connection (via SOCKS5 proxy)
        ↓
HTTP Request through Tor
        ↓
Save HTML to data/raw/
Phase 2: Feature Extraction
text
Raw HTML
    ↓
┌─────────────────────────────┐
│ Extract:                    │
│ • HTML Tag Structure        │
│ • CSS Classes & IDs         │
│ • Form Fields & Actions     │
│ • JavaScript Sources        │
│ • Meta Tags                 │
│ • Link Patterns             │
│ • Hidden Elements           │
│ • Text Structure            │
└─────────────────────────────┘
    ↓
Structural Fingerprint
Phase 3: Clone Detection
text
Fingerprint 1 + Fingerprint 2
        ↓
┌───────────────────────────────────────┐
│ Weighted Comparison:                  │
│ • Structure Hash     (25%)  ⭐⭐⭐⭐⭐    │
│ • Form Fields        (20%)  ⭐⭐⭐⭐      │
│ • CSS Classes        (15%)  ⭐⭐⭐       │
│ • Script Sources     (10%)  ⭐⭐        │
│ • Link Patterns      (10%)  ⭐⭐        │
│ • Tag Density        (10%)  ⭐⭐        │
│ • Meta Tags          (5%)   ⭐         │
│ • Hidden Elements    (5%)   ⭐         │
└───────────────────────────────────────┘
        ↓
Similarity Score (0-100%)
        ↓
Verdict: CLONE / NOT CLONE
Why Structure Matters
Approach	Easy to Clone?
❌ Text content	Yes - cloners just change text
❌ Images/Logos	Yes - cloners copy images easily
✅ HTML structure	No - breaks the site if changed
✅ CSS class names	No - breaks styling
✅ Form field names	No - backend validation fails
✅ Script dependencies	No - breaks functionality
📊 Sample Output
text
============================================================
🔍 CLONE DETECTION REPORT
============================================================

📊 Similarity Score: 92.5%
⚖️  Threshold: 85.0%

📋 Verdict: ⚠️ CLONE DETECTED

FEATURE BREAKDOWN (sorted by importance)
------------------------------------------------------------

🔴 HIGH HTML structure match
   Raw Score: 100.0%
   Contribution: 25.00%

🔴 HIGH Form fields match
   Raw Score: 95.0%
   Contribution: 19.00%

🔴 HIGH CSS classes/IDs match
   Raw Score: 90.0%
   Contribution: 13.50%

🟡 MED JavaScript files match
   Raw Score: 70.0%
   Contribution: 7.00%

🟢 LOW Meta tags match
   Raw Score: 30.0%
   Contribution: 1.50%

============================================================
⚠️  WARNING: High probability of cloned website!
============================================================
🌐 Dashboard Screenshots
Main Interface
🔵 Tor connection status indicator

📡 Live crawling interface

💾 Saved pages comparison

📊 Detection history table

Results View
⭕ Animated similarity score circle

🔴🟢 Color-coded risk levels (CRITICAL/HIGH/MEDIUM/LOW)

📊 Feature breakdown with progress bars

📄 Downloadable reports

🛡️ Safety & Ethics
⚠️ Important Guidelines
✅ DO	❌ DON'T
Use for academic research	Access illegal content
Test with known safe sites	Share crawled data publicly
Keep Tor Browser updated	Use without proper authorization
Respect robots.txt	Overload .onion servers
Follow local laws	Use for malicious purposes
Safe .onion Sites for Testing
Site	URL
DuckDuckGo	duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion
Tor Project	2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion
ProtonMail	protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion
🔧 Tech Stack
Component	Technology
Backend	Python 3.13
Web Framework	Flask
Proxy	Tor SOCKS5
HTML Parsing	BeautifulSoup4
Data Storage	JSON
Frontend	HTML5, CSS3, JavaScript
Version Control	Git & GitHub
👥 Team
Project Lead: [Your Name]

Feature Extraction: [Teammate Name]

Clone Detection Model: [Teammate Name]

Web Dashboard: [Your Name]

Detection of Clone Dark Web Websites - Academic Project

📄 License
This project is created for academic and research purposes only.

All rights reserved © 2026

🙏 Acknowledgments
The Tor Project for anonymous routing

BeautifulSoup for HTML parsing

Flask for the web framework

text

---

## After Replacing README.md:

```cmd
git add README.md
git commit -m "Updated README with full documentation"
git push
Your GitHub repo will now look professional with a complete README! 🎉

This response is AI-generated, for reference only.
team mates names g eswar , p tejaswi, p bhavya, sarvari khatoon
I'll update the team section. Replace just the team part in README.md with this:

markdown
## 👥 Team

| Name | Role |
|------|------|
| **G Eswar** | Project Lead, Dark Web Crawler & Web Dashboard |
| **P Tejaswi** | Feature Extraction Module |
| **P Bhavya** | Clone Detection Model |
| **Sarvari Khatoon** | Report Generation & Documentation |

*Detection of Clone Dark Web Websites - Academic Project*
To Update:
cmd
notepad README.md
Find the ## 👥 Team section and replace it with the above. Then:

cmd
git add README.md
git commit -m "Added team member names"
git push
Done! 🎉

This response is AI-generated, for reference only.
not mention all team mates wroked equal so it better only prsnt names for and give a copied full text for read me file
Here's the complete README.md. Copy everything and replace:

markdown
# 🕵️ Dark Web Clone Website Detection System

A Python-based system that crawls `.onion` dark web sites through Tor and detects cloned/phishing websites by comparing structural fingerprints.

---

## 📋 Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Web Dashboard](#web-dashboard)
- [How It Works](#how-it-works)
- [Sample Output](#sample-output)
- [Safety & Ethics](#safety--ethics)
- [Team](#team)

---

## ✨ Features

- 🔒 **Anonymous Crawling** - Crawls `.onion` sites through Tor network
- 🔍 **Clone Detection** - Compares HTML structure, CSS, forms, scripts, and meta tags
- 📊 **Weighted Scoring** - Each feature is weighted by importance for accurate detection
- 🌐 **Web Dashboard** - User-friendly Flask dashboard with real-time results
- 📄 **Report Generation** - HTML and JSON reports for documentation
- 💾 **Data Persistence** - Saves crawled pages and detection history

---

## 📂 Project Structure
detection_of_clone_darkweb_websites/
│
├── modules/
│ ├── darkweb_crawler.py # Tor-based .onion crawler
│ ├── tor_handle.py # Tor connection manager
│ ├── extractor.py # Feature extraction from HTML
│ ├── model.py # Clone detection algorithm
│ └── reporter.py # Report generation (JSON/HTML)
│
├── dashboard/
│ ├── app.py # Flask web dashboard
│ └── templates/
│ └── dashboard.html # Dashboard UI
│
├── data/
│ ├── raw/ # Crawled page data
│ ├── features/ # Extracted features & results
│ └── dataset/ # Training datasets
│
├── output/ # Generated reports
├── logs/ # Application logs
├── main.py # CLI entry point
├── config.py # Configuration settings
├── requirements.txt # Python dependencies
└── README.md # This file

text

---

## 📦 Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.8+ | Runtime |
| Tor Browser | Latest | Anonymous routing |
| Flask | 3.0+ | Web dashboard |

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sarvari911/detection_of_clone_darkweb_websites.git
cd detection_of_clone_darkweb_websites
2. Install Python Dependencies
bash
pip install -r requirements.txt
3. Download & Install Tor Browser
Download from: https://www.torproject.org/download/

Install and keep it open while running the system

4. Configure Environment
The .env file is already configured for Tor Browser (port 9150):

text
TOR_PROXY_PORT=9150
REQUEST_TIMEOUT=60
SIMILARITY_THRESHOLD=0.85
💻 Usage
Command Line Interface
bash
python main.py
Menu Options:

Option	Description
1	Crawl & Compare two .onion sites
2	Compare already-crawled pages
3	Crawl a single .onion site
4	View saved detection results
5	Exit
Web Dashboard
bash
cd dashboard
python app.py
Open: http://127.0.0.1:5000

🧠 How It Works
Phase 1: Crawling
text
User Input (.onion URLs)
        ↓
Tor Connection (via SOCKS5 proxy)
        ↓
HTTP Request through Tor
        ↓
Save HTML to data/raw/
Phase 2: Feature Extraction
text
Raw HTML
    ↓
┌─────────────────────────────┐
│ Extract:                    │
│ • HTML Tag Structure        │
│ • CSS Classes & IDs         │
│ • Form Fields & Actions     │
│ • JavaScript Sources        │
│ • Meta Tags                 │
│ • Link Patterns             │
│ • Hidden Elements           │
│ • Text Structure            │
└─────────────────────────────┘
    ↓
Structural Fingerprint
Phase 3: Clone Detection
text
Fingerprint 1 + Fingerprint 2
        ↓
┌───────────────────────────────────────┐
│ Weighted Comparison:                  │
│ • Structure Hash     (25%)  ⭐⭐⭐⭐⭐    │
│ • Form Fields        (20%)  ⭐⭐⭐⭐      │
│ • CSS Classes        (15%)  ⭐⭐⭐       │
│ • Script Sources     (10%)  ⭐⭐        │
│ • Link Patterns      (10%)  ⭐⭐        │
│ • Tag Density        (10%)  ⭐⭐        │
│ • Meta Tags          (5%)   ⭐         │
│ • Hidden Elements    (5%)   ⭐         │
└───────────────────────────────────────┘
        ↓
Similarity Score (0-100%)
        ↓
Verdict: CLONE / NOT CLONE
Why Structure Matters
Approach	Easy to Clone?
❌ Text content	Yes - cloners just change text
❌ Images/Logos	Yes - cloners copy images easily
✅ HTML structure	No - breaks the site if changed
✅ CSS class names	No - breaks styling
✅ Form field names	No - backend validation fails
✅ Script dependencies	No - breaks functionality
📊 Sample Output
text
============================================================
🔍 CLONE DETECTION REPORT
============================================================

📊 Similarity Score: 92.5%
⚖️  Threshold: 85.0%

📋 Verdict: ⚠️ CLONE DETECTED

FEATURE BREAKDOWN (sorted by importance)
------------------------------------------------------------

🔴 HIGH HTML structure match
   Raw Score: 100.0%
   Contribution: 25.00%

🔴 HIGH Form fields match
   Raw Score: 95.0%
   Contribution: 19.00%

🔴 HIGH CSS classes/IDs match
   Raw Score: 90.0%
   Contribution: 13.50%

🟡 MED JavaScript files match
   Raw Score: 70.0%
   Contribution: 7.00%

🟢 LOW Meta tags match
   Raw Score: 30.0%
   Contribution: 1.50%

============================================================
⚠️  WARNING: High probability of cloned website!
============================================================
🛡️ Safety & Ethics
⚠️ Important Guidelines
✅ DO	❌ DON'T
Use for academic research	Access illegal content
Test with known safe sites	Share crawled data publicly
Keep Tor Browser updated	Use without proper authorization
Respect robots.txt	Overload .onion servers
Follow local laws	Use for malicious purposes
Safe .onion Sites for Testing
Site	URL
DuckDuckGo	duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion
Tor Project	2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion
ProtonMail	protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion
🔧 Tech Stack
Component	Technology
Backend	Python 3.13
Web Framework	Flask
Proxy	Tor SOCKS5
HTML Parsing	BeautifulSoup4
Data Storage	JSON
Frontend	HTML5, CSS3, JavaScript
Version Control	Git & GitHub
👥 Team
G Eswar | P Tejaswi | P Bhavya | Sarvari Khatoon

Detection of Clone Dark Web Websites - Academic Project

text

---

Then push:

```cmd
git add README.md
git commit -m "Updated README with team names"
git push
Done! 🎉