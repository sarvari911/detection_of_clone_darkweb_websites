"""
Report Generator Module
Creates professional reports from clone detection results.
Outputs: Console report, JSON report, HTML report
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates clone detection reports in multiple formats.
    
    Output formats:
    1. Console - Printed to terminal
    2. JSON - Machine-readable data
    3. HTML - Beautiful report you can open in browser
    """

    def __init__(self, output_dir="output"):
        """
        Initialize the report generator
        
        Args:
            output_dir: Folder where reports are saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure .gitkeep exists
        gitkeep = self.output_dir / '.gitkeep'
        if not gitkeep.exists():
            gitkeep.touch()

    def generate(self, original_url, suspect_url, original_data, suspect_data, detection_result):
        """
        Generate a complete clone detection report.
        
        Args:
            original_url: URL of the original site
            suspect_url: URL of the suspected clone
            original_data: Crawled data from original site
            suspect_data: Crawled data from suspect site
            detection_result: Results from CloneDetector.compare()
            
        Returns:
            dict: Complete report data
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build report
        report = {
            'report_metadata': {
                'generated_at': timestamp,
                'tool': 'Dark Web Clone Detection System',
                'version': '1.0.0'
            },
            'sites_analyzed': {
                'original': {
                    'url': original_url,
                    'title': original_data.get('title', 'Unknown') if original_data else 'N/A',
                    'response_time': original_data.get('response_time', 'N/A') if original_data else 'N/A',
                    'page_size': original_data.get('html_length', 0) if original_data else 0
                },
                'suspect': {
                    'url': suspect_url,
                    'title': suspect_data.get('title', 'Unknown') if suspect_data else 'N/A',
                    'response_time': suspect_data.get('response_time', 'N/A') if suspect_data else 'N/A',
                    'page_size': suspect_data.get('html_length', 0) if suspect_data else 0
                }
            },
            'detection_result': detection_result,
            'summary': self._create_summary(detection_result)
        }
        
        return report

    def _create_summary(self, result):
        """Create a human-readable summary"""
        if not result:
            return "No results available."
        
        score = result.get('similarity_score', 0)
        is_clone = result.get('is_clone', False)
        
        if score >= 0.90:
            risk = "CRITICAL"
            summary = "Almost identical structure detected. This is very likely a clone."
        elif score >= 0.75:
            risk = "HIGH"
            summary = "Strong similarities found. Further investigation recommended."
        elif score >= 0.50:
            risk = "MEDIUM"
            summary = "Some similarities detected. May share common templates."
        else:
            risk = "LOW"
            summary = "Sites appear to be structurally different."
        
        return {
            'risk_level': risk,
            'is_clone': is_clone,
            'similarity': f"{score:.1%}",
            'message': summary
        }

    def save_json(self, report, filename=None):
        """
        Save report as JSON file
        
        Args:
            report: Report data dict
            filename: Optional custom filename
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"clone_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON report saved: {filepath}")
        print(f"📄 JSON report saved: {filepath}")
        
        return str(filepath)

    def save_html(self, report, filename=None):
        """
        Save report as a beautiful HTML file.
        You can open this in your browser to show your professor!
        
        Args:
            report: Report data dict
            filename: Optional custom filename
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"clone_report_{timestamp}.html"
        
        filepath = self.output_dir / filename
        
        # Build HTML content
        html = self._build_html_report(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"HTML report saved: {filepath}")
        print(f"🌐 HTML report saved: {filepath}")
        print(f"   Open this file in your browser to view!")
        
        return str(filepath)

    def print_console(self, report):
        """
        Print a formatted report to the console
        
        Args:
            report: Report data dict
        """
        meta = report.get('report_metadata', {})
        sites = report.get('sites_analyzed', {})
        result = report.get('detection_result', {})
        summary = report.get('summary', {})
        
        print("\n" + "=" * 65)
        print("🕵️  DARK WEB CLONE DETECTION REPORT")
        print("=" * 65)
        
        # Metadata
        print(f"\n📅 Generated: {meta.get('generated_at', 'N/A')}")
        print(f"🔧 Tool: {meta.get('tool', 'N/A')}")
        
        # Sites analyzed
        print("\n" + "-" * 65)
        print("📡 SITES ANALYZED")
        print("-" * 65)
        
        original = sites.get('original', {})
        suspect = sites.get('suspect', {})
        
        print(f"\n🔵 ORIGINAL SITE:")
        print(f"   URL: {original.get('url', 'N/A')}")
        print(f"   Title: {original.get('title', 'N/A')}")
        print(f"   Page Size: {original.get('page_size', 0):,} characters")
        print(f"   Response Time: {original.get('response_time', 'N/A')}s")
        
        print(f"\n🔴 SUSPECT SITE:")
        print(f"   URL: {suspect.get('url', 'N/A')}")
        print(f"   Title: {suspect.get('title', 'N/A')}")
        print(f"   Page Size: {suspect.get('page_size', 0):,} characters")
        print(f"   Response Time: {suspect.get('response_time', 'N/A')}s")
        
        # Detection Result
        print("\n" + "-" * 65)
        print("🔍 DETECTION RESULT")
        print("-" * 65)
        
        print(f"\n📊 Similarity Score: {result.get('similarity_score', 0):.2%}")
        print(f"⚖️  Threshold: {result.get('threshold', 0.85):.2%}")
        
        verdict = result.get('verdict', 'Unknown')
        print(f"\n📋 Verdict: {verdict}")
        
        # Risk Summary
        print("\n" + "-" * 65)
        print("⚠️  RISK ASSESSMENT")
        print("-" * 65)
        
        print(f"\n   Risk Level: {summary.get('risk_level', 'N/A')}")
        print(f"   Clone Detected: {'⚠️ YES' if summary.get('is_clone') else '✅ NO'}")
        print(f"   Similarity: {summary.get('similarity', 'N/A')}")
        print(f"\n   {summary.get('message', '')}")
        
        # Feature Breakdown
        breakdown = result.get('breakdown', [])
        if breakdown:
            print("\n" + "-" * 65)
            print("📊 FEATURE BREAKDOWN")
            print("-" * 65)
            
            for item in breakdown[:5]:  # Top 5 features
                indicator = item.get('indicator', '')
                explanation = item.get('explanation', '')
                weighted = item.get('weighted_score', 0)
                bar = "█" * int(weighted * 20)
                print(f"\n   {indicator} {explanation}")
                print(f"   Score: {weighted:.2%}  [{bar}]")
        
        print("\n" + "=" * 65)
        print("END OF REPORT")
        print("=" * 65 + "\n")

    def _build_html_report(self, report):
        """
        Build a beautiful HTML report.
        This creates a standalone HTML file you can open anywhere.
        """
        meta = report.get('report_metadata', {})
        sites = report.get('sites_analyzed', {})
        result = report.get('detection_result', {})
        summary = report.get('summary', {})
        
        original = sites.get('original', {})
        suspect = sites.get('suspect', {})
        
        # Color coding for risk
        risk_colors = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107',
            'LOW': '#28a745'
        }
        risk_color = risk_colors.get(summary.get('risk_level', 'LOW'), '#28a745')
        
        # Build feature breakdown rows
        breakdown_rows = ""
        for item in result.get('breakdown', []):
            weighted = item.get('weighted_score', 0)
            bar_width = int(weighted * 100)
            bar_color = '#dc3545' if weighted > 0.08 else '#fd7e14' if weighted > 0.04 else '#28a745'
            breakdown_rows += f"""
            <tr>
                <td>{item.get('indicator', '')}</td>
                <td>{item.get('explanation', '')}</td>
                <td>{item.get('raw_score', 0):.1%}</td>
                <td>{item.get('weight', 0):.0%}</td>
                <td>
                    <div style="background:#e9ecef; border-radius:4px; height:20px;">
                        <div style="background:{bar_color}; width:{bar_width}%; height:100%; border-radius:4px;"></div>
                    </div>
                    {weighted:.1%}
                </td>
            </tr>"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clone Detection Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ background: #16213e; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
        .header h1 {{ color: #e94560; font-size: 28px; }}
        .header p {{ color: #aaa; margin-top: 5px; }}
        .card {{ background: #16213e; padding: 25px; border-radius: 10px; margin-bottom: 20px; }}
        .card h2 {{ color: #e94560; margin-bottom: 15px; font-size: 20px; }}
        .sites {{ display: flex; gap: 20px; }}
        .site {{ flex: 1; background: #0f3460; padding: 20px; border-radius: 8px; }}
        .site.original {{ border-left: 4px solid #28a745; }}
        .site.suspect {{ border-left: 4px solid #dc3545; }}
        .site h3 {{ margin-bottom: 10px; }}
        .site p {{ color: #ccc; font-size: 14px; margin: 5px 0; }}
        .verdict {{ text-align: center; padding: 20px; font-size: 24px; font-weight: bold; border-radius: 8px; margin: 20px 0; }}
        .verdict.clone {{ background: #dc354533; color: #dc3545; border: 2px solid #dc3545; }}
        .verdict.safe {{ background: #28a74533; color: #28a745; border: 2px solid #28a745; }}
        .score {{ font-size: 48px; font-weight: bold; text-align: center; }}
        .risk-badge {{ display: inline-block; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ color: #e94560; font-size: 14px; }}
        td {{ font-size: 14px; color: #ccc; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕵️ Dark Web Clone Detection Report</h1>
            <p>Generated: {meta.get('generated_at', 'N/A')}</p>
        </div>
        
        <div class="card">
            <h2>📡 Sites Analyzed</h2>
            <div class="sites">
                <div class="site original">
                    <h3>🔵 Original Site</h3>
                    <p><strong>URL:</strong> {original.get('url', 'N/A')[:60]}...</p>
                    <p><strong>Title:</strong> {original.get('title', 'N/A')}</p>
                    <p><strong>Size:</strong> {original.get('page_size', 0):,} chars</p>
                    <p><strong>Response:</strong> {original.get('response_time', 'N/A')}s</p>
                </div>
                <div class="site suspect">
                    <h3>🔴 Suspect Site</h3>
                    <p><strong>URL:</strong> {suspect.get('url', 'N/A')[:60]}...</p>
                    <p><strong>Title:</strong> {suspect.get('title', 'N/A')}</p>
                    <p><strong>Size:</strong> {suspect.get('page_size', 0):,} chars</p>
                    <p><strong>Response:</strong> {suspect.get('response_time', 'N/A')}s</p>
                </div>
            </div>
        </div>
        
        <div class="card" style="text-align:center;">
            <h2>🔍 Detection Result</h2>
            <div class="score" style="color: {risk_color};">{result.get('similarity_score', 0):.1%}</div>
            <p style="color:#aaa;">Similarity Score</p>
            <div class="verdict {'clone' if summary.get('is_clone') else 'safe'}">
                {summary.get('risk_level', 'N/A')} RISK - {result.get('verdict', 'N/A')}
            </div>
            <span class="risk-badge" style="background:{risk_color}; color:white;">
                {summary.get('risk_level', 'N/A')}
            </span>
            <p style="margin-top:15px; color:#ccc;">{summary.get('message', '')}</p>
        </div>
        
        <div class="card">
            <h2>📊 Feature Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Indicator</th>
                        <th>Feature</th>
                        <th>Score</th>
                        <th>Weight</th>
                        <th>Contribution</th>
                    </tr>
                </thead>
                <tbody>
                    {breakdown_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Dark Web Clone Detection System v1.0 | Generated for academic research purposes
        </div>
    </div>
</body>
</html>"""
        
        return html


# ============================================
# QUICK TEST
# ============================================

def test_reporter():
    """Test the report generator"""
    print("\n🧪 Testing Report Generator\n")
    
    # Create sample data (simulating a complete detection)
    original_data = {
        'title': 'Original Bank - Secure Login',
        'response_time': 3.45,
        'html_length': 45231,
        'url': 'http://originalbank.onion'
    }
    
    suspect_data = {
        'title': 'Bank Login - Verify Account',
        'response_time': 5.21,
        'html_length': 44890,
        'url': 'http://fakebank.onion'
    }
    
    detection_result = {
        'is_clone': True,
        'similarity_score': 0.92,
        'threshold': 0.85,
        'verdict': '⚠️ CLONE DETECTED',
        'breakdown': [
            {'indicator': '🔴 HIGH', 'explanation': 'HTML structure match', 
             'raw_score': 1.0, 'weight': 0.25, 'weighted_score': 0.25},
            {'indicator': '🔴 HIGH', 'explanation': 'Form fields match', 
             'raw_score': 0.95, 'weight': 0.20, 'weighted_score': 0.19},
            {'indicator': '🔴 HIGH', 'explanation': 'CSS classes/IDs match', 
             'raw_score': 0.90, 'weight': 0.15, 'weighted_score': 0.135},
            {'indicator': '🟡 MED', 'explanation': 'JavaScript files match', 
             'raw_score': 0.70, 'weight': 0.10, 'weighted_score': 0.07},
            {'indicator': '🟢 LOW', 'explanation': 'Meta tags match', 
             'raw_score': 0.30, 'weight': 0.05, 'weighted_score': 0.015},
        ]
    }
    
    reporter = ReportGenerator()
    
    # Generate report
    report = reporter.generate(
        original_url="http://originalbank.onion",
        suspect_url="http://fakebank.onion",
        original_data=original_data,
        suspect_data=suspect_data,
        detection_result=detection_result
    )
    
    # Print to console
    reporter.print_console(report)
    
    # Save JSON
    reporter.save_json(report)
    
    # Save HTML
    reporter.save_html(report)
    
    print("\n✅ Report test complete!")
    return report


if __name__ == "__main__":
    test_reporter()