"""
Feature Extractor Module
Extracts structural fingerprints from HTML pages for clone detection.
These features are hard to change without breaking the site.
"""

import re
import hashlib
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extracts comparison features from HTML pages.
    Focuses on STRUCTURE not content because:
    - Cloners change visible text (easy)
    - Cloners keep code structure (hard to change without breaking)
    """

    def __init__(self):
        """Initialize the feature extractor"""
        self.features = {}

    def extract_all(self, html_content, page_title=""):
        """
        Extract all features from HTML content.
        This is the main method you'll call.

        Args:
            html_content: Raw HTML string
            page_title: Title of the page (optional)

        Returns:
            dict: All extracted features as a fingerprint
        """
        if not html_content:
            logger.error("No HTML content to extract features from")
            return None

        soup = BeautifulSoup(html_content, 'html.parser')

        fingerprint = {
            'title': page_title,
            'html_structure': self._extract_structure(soup),
            'tag_density': self._extract_tag_density(soup),
            'css_fingerprint': self._extract_css_fingerprint(soup),
            'form_fingerprint': self._extract_form_fingerprint(soup),
            'meta_fingerprint': self._extract_meta_fingerprint(soup),
            'link_pattern': self._extract_link_pattern(soup),
            'script_fingerprint': self._extract_script_fingerprint(soup),
            'image_fingerprint': self._extract_image_fingerprint(soup),
            'hidden_elements': self._extract_hidden_elements(soup),
            'text_structure': self._extract_text_structure(soup),
            'overall_hash': self._compute_structure_hash(soup),
        }

        logger.info(f"Extracted fingerprint for: {page_title[:50]}")
        return fingerprint

    # ============================================
    # INDIVIDUAL FEATURE EXTRACTORS
    # ============================================

    def _extract_structure(self, soup):
        """
        Extract the DOM tree structure.
        Count of each HTML tag type.
        
        Example output:
        {'div': 45, 'p': 12, 'a': 30, 'img': 8, ...}
        """
        tags = {}
        for tag in soup.find_all():
            tag_name = tag.name
            tags[tag_name] = tags.get(tag_name, 0) + 1
        
        return tags

    def _extract_tag_density(self, soup):
        """
        Calculate how densely tags are nested.
        Deeply nested sites have different structure.
        
        Returns: Average nesting depth
        """
        def get_depth(element, current_depth=0):
            children = element.find_all(recursive=False)
            if not children:
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in children)

        body = soup.find('body')
        if body:
            return get_depth(body)
        return 0

    def _extract_css_fingerprint(self, soup):
        """
        Extract CSS class names and IDs.
        Cloners often keep the same class names.
        
        Returns: Sorted list of unique class names and IDs
        """
        classes = set()
        ids = set()

        for element in soup.find_all(attrs={'class': True}):
            for cls in element.get('class', []):
                classes.add(cls)

        for element in soup.find_all(attrs={'id': True}):
            ids.add(element.get('id', ''))

        return {
            'class_count': len(classes),
            'id_count': len(ids),
            'sample_classes': sorted(list(classes))[:50],  # First 50
            'sample_ids': sorted(list(ids))[:50]           # First 50
        }

    def _extract_form_fingerprint(self, soup):
        """
        Extract form structures.
        Forms reveal backend architecture.
        Cloners keep same field names so phishing works.
        
        Returns: Form field names and types
        """
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'fields': []
            }
            for field in form.find_all(['input', 'select', 'textarea']):
                form_data['fields'].append({
                    'name': field.get('name', ''),
                    'type': field.get('type', 'text'),
                    'id': field.get('id', '')
                })
            forms.append(form_data)

        return {
            'form_count': len(forms),
            'forms': forms
        }

    def _extract_meta_fingerprint(self, soup):
        """
        Extract meta tags.
        Often copied exactly by cloners.
        
        Returns: Meta name:content pairs
        """
        metas = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content', '')
            if name:
                metas[name] = content[:200]  # Truncate long values

        return metas

    def _extract_link_pattern(self, soup):
        """
        Extract link structures.
        Reveals navigation patterns and external dependencies.
        
        Returns: Statistics about links
        """
        links = []
        internal_count = 0
        external_count = 0
        onion_count = 0

        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            links.append(href[:200])  # Truncate long URLs
            
            if href.endswith('.onion') or '.onion/' in href:
                onion_count += 1
            elif href.startswith('http') or href.startswith('//'):
                external_count += 1
            else:
                internal_count += 1

        return {
            'total_links': len(links),
            'internal_links': internal_count,
            'external_links': external_count,
            'onion_links': onion_count,
            'sample_links': links[:30]  # First 30 links
        }

    def _extract_script_fingerprint(self, soup):
        """
        Extract JavaScript files.
        Same scripts loaded = likely same site.
        
        Returns: List of script sources
        """
        scripts = []
        inline_count = 0

        for script in soup.find_all('script'):
            src = script.get('src', '')
            if src:
                scripts.append(src[:200])
            else:
                # Inline script - hash its content
                if script.string:
                    content_hash = hashlib.md5(
                        script.string.encode()
                    ).hexdigest()
                    inline_count += 1

        return {
            'script_count': len(scripts),
            'inline_scripts': inline_count,
            'script_sources': scripts[:30]  # First 30
        }

    def _extract_image_fingerprint(self, soup):
        """
        Extract image sources.
        Same images = strong clone indicator.
        
        Returns: Image source patterns
        """
        images = []
        for img in soup.find_all('img', src=True):
            src = img.get('src', '')
            alt = img.get('alt', '')
            images.append({
                'src': src[:200],
                'alt': alt[:100]
            })

        return {
            'image_count': len(images),
            'images': images[:30]  # First 30
        }

    def _extract_hidden_elements(self, soup):
        """
        Find hidden elements.
        Cloners often leave hidden admin panels, debug info,
        or the original site's hidden tracking code.
        
        Returns: Count and types of hidden elements
        """
        hidden = []
        for element in soup.find_all(style=True):
            style = element.get('style', '').lower()
            if 'display:none' in style or 'visibility:hidden' in style:
                hidden.append({
                    'tag': element.name,
                    'class': element.get('class', []),
                    'id': element.get('id', ''),
                    'text_preview': element.get_text()[:100].strip()
                })

        return {
            'hidden_count': len(hidden),
            'hidden_elements': hidden[:20]  # First 20
        }

    def _extract_text_structure(self, soup):
        """
        Extract text structure, not content.
        Measures: heading hierarchy, text-to-code ratio, etc.
        
        Returns: Structure statistics
        """
        # Get text from body only
        body = soup.find('body')
        if not body:
            body = soup

        visible_text = body.get_text(separator=' ', strip=True)
        html_size = len(str(soup))
        text_size = len(visible_text)

        # Heading structure
        headings = {}
        for level in range(1, 7):
            headings[f'h{level}'] = len(soup.find_all(f'h{level}'))

        # Paragraph count
        paragraphs = len(soup.find_all('p'))

        return {
            'text_length': text_size,
            'html_length': html_size,
            'text_to_code_ratio': round(text_size / max(html_size, 1), 4),
            'headings': headings,
            'paragraphs': paragraphs,
            'avg_heading_text_length': self._avg_heading_length(soup)
        }

    def _avg_heading_length(self, soup):
        """Calculate average length of heading text"""
        total = 0
        count = 0
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                total += len(heading.get_text(strip=True))
                count += 1
        return round(total / max(count, 1), 2)

    def _compute_structure_hash(self, soup):
        """
        Create a unique hash of the HTML structure.
        Same structure = same hash.
        Ignores text content, only looks at tag order.
        
        Returns: MD5 hash string
        """
        # Get only tag names in order (ignore text)
        tag_sequence = []
        for tag in soup.find_all():
            tag_sequence.append(tag.name)

        # Create hash from tag sequence
        sequence_string = '|'.join(tag_sequence)
        return hashlib.md5(sequence_string.encode()).hexdigest()


# ============================================
# QUICK TEST
# ============================================

def test_extractor():
    """Test the feature extractor with sample HTML"""
    print("\n🧪 Testing Feature Extractor\n")
    print("=" * 50)

    # Sample HTML simulating two similar sites
    original_html = """
    <html>
    <head>
        <title>Original Bank</title>
        <meta name="description" content="Secure banking">
        <meta name="author" content="BankCorp">
    </head>
    <body>
        <div class="header">
            <img src="/logo.png" alt="Bank Logo">
            <nav class="main-nav">
                <a href="/login">Login</a>
                <a href="/register">Register</a>
            </nav>
        </div>
        <div class="content">
            <h1>Welcome to Original Bank</h1>
            <p>Your trusted banking partner.</p>
            <form action="/login" method="POST">
                <input type="text" name="username" placeholder="Username">
                <input type="password" name="password" placeholder="Password">
                <input type="submit" value="Login">
            </form>
        </div>
        <div class="footer" style="display:none">
            <p>Debug: version 2.4.1</p>
        </div>
        <script src="/js/main.js"></script>
        <script src="/js/jquery.min.js"></script>
    </body>
    </html>
    """

    clone_html = """
    <html>
    <head>
        <title>Fake Bank - Login</title>
        <meta name="description" content="Secure banking">
        <meta name="author" content="BankCorp">
    </head>
    <body>
        <div class="header">
            <img src="/logo.png" alt="Bank Logo">
            <nav class="main-nav">
                <a href="/login">Login</a>
                <a href="/register">Register</a>
            </nav>
        </div>
        <div class="content">
            <h1>Welcome to Fake Bank</h1>
            <p>Enter your credentials below.</p>
            <form action="/steal.php" method="POST">
                <input type="text" name="username" placeholder="Username">
                <input type="password" name="password" placeholder="Password">
                <input type="submit" value="Login">
            </form>
        </div>
        <div class="footer" style="display:none">
            <p>Debug: version 2.4.1</p>
        </div>
        <script src="/js/main.js"></script>
        <script src="/js/jquery.min.js"></script>
    </body>
    </html>
    """

    extractor = FeatureExtractor()

    print("📄 Extracting features from ORIGINAL site...")
    original_features = extractor.extract_all(original_html, "Original Bank")
    
    print("📄 Extracting features from CLONE site...")
    clone_features = extractor.extract_all(clone_html, "Fake Bank")

    print("\n" + "=" * 50)
    print("COMPARISON PREVIEW")
    print("=" * 50)

    # Compare structure hash (same structure = same hash)
    print(f"\nStructure Hash:")
    print(f"  Original: {original_features['overall_hash']}")
    print(f"  Clone:    {clone_features['overall_hash']}")
    print(f"  Match:    {'✅ YES - Same Structure!' if original_features['overall_hash'] == clone_features['overall_hash'] else '❌ NO'}")
    
    # Compare CSS fingerprint
    print(f"\nCSS Classes:")
    print(f"  Original: {original_features['css_fingerprint']['class_count']} classes")
    print(f"  Clone:    {clone_features['css_fingerprint']['class_count']} classes")
    
    # Compare form fingerprint
    print(f"\nForm Fields:")
    orig_fields = [f['name'] for f in original_features['form_fingerprint']['forms'][0]['fields']]
    clone_fields = [f['name'] for f in clone_features['form_fingerprint']['forms'][0]['fields']]
    print(f"  Original: {orig_fields}")
    print(f"  Clone:    {clone_fields}")
    print(f"  Match:    {'✅ Same fields!' if orig_fields == clone_fields else '❌ Different'}")
    
    # Hidden elements
    print(f"\nHidden Elements:")
    print(f"  Original: {original_features['hidden_elements']['hidden_count']} hidden")
    print(f"  Clone:    {clone_features['hidden_elements']['hidden_count']} hidden")

    print("\n✅ Feature extraction test complete!")
    print("Notice: Same STRUCTURE but different TEXT = CLONE DETECTED")
    
    return original_features, clone_features


if __name__ == "__main__":
    test_extractor()