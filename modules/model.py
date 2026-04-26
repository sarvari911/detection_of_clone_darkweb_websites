"""
Clone Detection Model
Compares extracted features to determine if two sites are clones.
Uses multiple comparison methods and weights them by importance.
"""

import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class CloneDetector:
    """
    Detects cloned websites by comparing structural fingerprints.
    
    How it works:
    1. Takes fingerprints from two sites (from extractor.py)
    2. Compares each feature separately
    3. Gives each feature a weight (some matter more than others)
    4. Calculates final similarity score (0 to 100%)
    """

    def __init__(self, threshold=0.85):
        """
        Initialize the clone detector
        
        Args:
            threshold: Score above this = CLONE (default 0.85 = 85%)
        """
        self.threshold = threshold
        
        # Weights: Which features matter most?
        # Total = 1.0 (100%)
        self.weights = {
            'structure_hash': 0.25,    # 25% - Most important! Same structure = same site
            'css_fingerprint': 0.15,   # 15% - Same CSS classes
            'form_fingerprint': 0.20,  # 20% - Same form fields (login forms especially)
            'tag_density': 0.10,       # 10% - Same nesting depth
            'script_fingerprint': 0.10,# 10% - Same JavaScript files
            'meta_fingerprint': 0.05,  # 5%  - Same meta tags
            'link_pattern': 0.10,      # 10% - Same navigation structure
            'hidden_elements': 0.05,   # 5%  - Same hidden elements (cloners forget these)
        }

    def compare(self, features1, features2):
        """
        Main comparison method.
        
        Args:
            features1: Fingerprint from original site
            features2: Fingerprint from suspected clone
            
        Returns:
            dict: Full comparison results with scores
        """
        if not features1 or not features2:
            logger.error("Missing features for comparison")
            return None

        logger.info("Comparing site fingerprints...")

        # Compare each feature
        scores = {
            'structure_hash': self._compare_hashes(
                features1.get('overall_hash', ''),
                features2.get('overall_hash', '')
            ),
            'css_fingerprint': self._compare_css(
                features1.get('css_fingerprint', {}),
                features2.get('css_fingerprint', {})
            ),
            'form_fingerprint': self._compare_forms(
                features1.get('form_fingerprint', {}),
                features2.get('form_fingerprint', {})
            ),
            'tag_density': self._compare_density(
                features1.get('tag_density', 0),
                features2.get('tag_density', 0)
            ),
            'script_fingerprint': self._compare_scripts(
                features1.get('script_fingerprint', {}),
                features2.get('script_fingerprint', {})
            ),
            'meta_fingerprint': self._compare_metas(
                features1.get('meta_fingerprint', {}),
                features2.get('meta_fingerprint', {})
            ),
            'link_pattern': self._compare_links(
                features1.get('link_pattern', {}),
                features2.get('link_pattern', {})
            ),
            'hidden_elements': self._compare_hidden(
                features1.get('hidden_elements', {}),
                features2.get('hidden_elements', {})
            ),
        }

        # Calculate weighted final score
        final_score = self._calculate_final_score(scores)

        # Determine verdict
        is_clone = final_score >= self.threshold

        result = {
            'is_clone': is_clone,
            'similarity_score': round(final_score, 4),
            'threshold': self.threshold,
            'verdict': '⚠️ CLONE DETECTED' if is_clone else '✅ Different Sites',
            'feature_scores': scores,
            'breakdown': self._create_breakdown(scores),
        }

        return result

    # ============================================
    # INDIVIDUAL COMPARISON METHODS
    # ============================================

    def _compare_hashes(self, hash1, hash2):
        """
        Compare structure hashes.
        Exact match = 1.0, No match = 0.0
        This is the STRONGEST indicator.
        """
        if not hash1 or not hash2:
            return 0.0
        return 1.0 if hash1 == hash2 else 0.0

    def _compare_css(self, css1, css2):
        """
        Compare CSS class names and IDs.
        What percentage of classes are the same?
        """
        classes1 = set(css1.get('sample_classes', []))
        classes2 = set(css2.get('sample_classes', []))
        ids1 = set(css1.get('sample_ids', []))
        ids2 = set(css2.get('sample_ids', []))

        # Jaccard similarity: intersection / union
        class_sim = self._jaccard_similarity(classes1, classes2)
        id_sim = self._jaccard_similarity(ids1, ids2)

        # Average of class and ID similarity
        if classes1 or classes2:
            return (class_sim * 0.7) + (id_sim * 0.3)
        return 0.0

    def _compare_forms(self, form1, form2):
        """
        Compare form structures.
        Same field names with same types = high similarity.
        """
        fields1 = []
        fields2 = []

        for form in form1.get('forms', []):
            for field in form.get('fields', []):
                fields1.append(f"{field.get('name')}_{field.get('type')}")

        for form in form2.get('forms', []):
            for field in form.get('fields', []):
                fields2.append(f"{field.get('name')}_{field.get('type')}")

        if not fields1 and not fields2:
            return 1.0  # Both have no forms = similar

        return self._jaccard_similarity(set(fields1), set(fields2))

    def _compare_density(self, depth1, depth2):
        """
        Compare HTML nesting depth.
        Similar depth = similar page structure.
        """
        if depth1 == 0 and depth2 == 0:
            return 1.0
        if depth1 == 0 or depth2 == 0:
            return 0.0

        # How close are the depths? (ratio of smaller to larger)
        ratio = min(depth1, depth2) / max(depth1, depth2)
        return ratio

    def _compare_scripts(self, script1, script2):
        """
        Compare JavaScript files loaded.
        Same JS files = very strong indicator.
        """
        sources1 = set(script1.get('script_sources', []))
        sources2 = set(script2.get('script_sources', []))

        if not sources1 and not sources2:
            return 1.0

        return self._jaccard_similarity(sources1, sources2)

    def _compare_metas(self, meta1, meta2):
        """
        Compare meta tags.
        Same author, description, generator = likely clone.
        """
        keys1 = set(meta1.keys())
        keys2 = set(meta2.keys())

        if not keys1 and not keys2:
            return 1.0

        # Check how many meta keys match
        common_keys = keys1 & keys2
        all_keys = keys1 | keys2

        if not all_keys:
            return 0.0

        key_similarity = len(common_keys) / len(all_keys)

        # For matching keys, check if values are same
        value_matches = 0
        for key in common_keys:
            if meta1.get(key, '') == meta2.get(key, ''):
                value_matches += 1

        value_similarity = value_matches / max(len(common_keys), 1)

        return (key_similarity * 0.4) + (value_similarity * 0.6)

    def _compare_links(self, links1, links2):
        """
        Compare link structures.
        Same navigation pattern = same site design.
        """
        sample1 = set(links1.get('sample_links', []))
        sample2 = set(links2.get('sample_links', []))

        if not sample1 and not sample2:
            return 1.0

        return self._jaccard_similarity(sample1, sample2)

    def _compare_hidden(self, hidden1, hidden2):
        """
        Compare hidden elements.
        Cloners often forget to remove hidden debug/backup elements.
        """
        count1 = hidden1.get('hidden_count', 0)
        count2 = hidden2.get('hidden_count', 0)

        if count1 == 0 and count2 == 0:
            return 1.0
        if count1 == 0 or count2 == 0:
            return 0.0

        ratio = min(count1, count2) / max(count1, count2)
        return ratio

    # ============================================
    # HELPER METHODS
    # ============================================

    def _jaccard_similarity(self, set1, set2):
        """
        Calculate Jaccard similarity between two sets.
        
        Jaccard = intersection / union
        
        Example:
        set1 = {A, B, C}
        set2 = {B, C, D}
        intersection = {B, C} = 2
        union = {A, B, C, D} = 4
        similarity = 2/4 = 0.5 (50%)
        """
        if not set1 and not set2:
            return 1.0  # Both empty = similar
        if not set1 or not set2:
            return 0.0  # One empty = different

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _calculate_final_score(self, scores):
        """
        Calculate weighted final similarity score.
        Each feature score is multiplied by its importance weight.
        
        Formula:
        final = (score1 × weight1) + (score2 × weight2) + ...
        """
        final = 0.0
        for feature, score in scores.items():
            weight = self.weights.get(feature, 0.0)
            final += score * weight
        
        return final

    def _create_breakdown(self, scores):
        """
        Create a human-readable breakdown of what matched.
        """
        breakdown = []
        
        explanations = {
            'structure_hash': 'HTML structure match',
            'css_fingerprint': 'CSS classes/IDs match',
            'form_fingerprint': 'Form fields match',
            'tag_density': 'Page depth match',
            'script_fingerprint': 'JavaScript files match',
            'meta_fingerprint': 'Meta tags match',
            'link_pattern': 'Navigation links match',
            'hidden_elements': 'Hidden elements match',
        }

        for feature, score in scores.items():
            weight = self.weights.get(feature, 0)
            weighted_score = score * weight
            explanation = explanations.get(feature, feature)
            
            breakdown.append({
                'feature': feature,
                'raw_score': round(score, 4),
                'weight': weight,
                'weighted_score': round(weighted_score, 4),
                'explanation': explanation,
                'indicator': '🔴 HIGH' if score > 0.8 else '🟡 MED' if score > 0.5 else '🟢 LOW'
            })

        # Sort by importance
        breakdown.sort(key=lambda x: x['weighted_score'], reverse=True)
        
        return breakdown

    def print_report(self, result):
        """
        Print a formatted comparison report to console.
        """
        if not result:
            print("No comparison results to display.")
            return

        print("\n" + "=" * 60)
        print("🔍 CLONE DETECTION REPORT")
        print("=" * 60)

        # Verdict
        verdict = result['verdict']
        score = result['similarity_score']
        print(f"\n📊 Similarity Score: {score:.2%}")
        print(f"⚖️  Threshold: {result['threshold']:.2%}")
        print(f"\n📋 Verdict: {verdict}")

        # Breakdown
        print("\n" + "-" * 60)
        print("FEATURE BREAKDOWN (sorted by importance)")
        print("-" * 60)

        for item in result['breakdown']:
            bar = "█" * int(item['weighted_score'] * 20)
            print(f"\n{item['indicator']} {item['explanation']}")
            print(f"   Raw Score: {item['raw_score']:.2%}")
            print(f"   Weight: {item['weight']:.0%}")
            print(f"   Contribution: {item['weighted_score']:.2%}")
            print(f"   [{bar}]")

        print("\n" + "=" * 60)

        # Final advice
        if result['is_clone']:
            print("⚠️  WARNING: High probability of cloned website!")
            print("   This site likely copied the original's structure.")
        else:
            print("✅ These appear to be different websites.")
        
        print("=" * 60 + "\n")


# ============================================
# QUICK TEST
# ============================================

def test_model():
    """Test the clone detector with sample fingerprints"""
    print("\n🧪 Testing Clone Detection Model\n")

    # Simulate extracted features from two similar sites
    # (These match what extractor.py produces)
    features_original = {
        'overall_hash': 'abc123def456',
        'tag_density': 5,
        'css_fingerprint': {
            'class_count': 4,
            'id_count': 2,
            'sample_classes': ['header', 'main-nav', 'content', 'footer'],
            'sample_ids': ['logo', 'login-form']
        },
        'form_fingerprint': {
            'form_count': 1,
            'forms': [{
                'action': '/login',
                'method': 'POST',
                'fields': [
                    {'name': 'username', 'type': 'text'},
                    {'name': 'password', 'type': 'password'},
                    {'name': '', 'type': 'submit'}
                ]
            }]
        },
        'script_fingerprint': {
            'script_count': 2,
            'inline_scripts': 0,
            'script_sources': ['/js/main.js', '/js/jquery.min.js']
        },
        'meta_fingerprint': {
            'description': 'Secure banking',
            'author': 'BankCorp'
        },
        'link_pattern': {
            'total_links': 2,
            'sample_links': ['/login', '/register']
        },
        'hidden_elements': {
            'hidden_count': 1
        }
    }

    features_clone = {
        'overall_hash': 'abc123def456',  # SAME hash!
        'tag_density': 5,                 # SAME depth
        'css_fingerprint': {
            'class_count': 4,
            'id_count': 2,
            'sample_classes': ['header', 'main-nav', 'content', 'footer'],
            'sample_ids': ['logo', 'login-form']
        },
        'form_fingerprint': {
            'form_count': 1,
            'forms': [{
                'action': '/steal.php',    # DIFFERENT action
                'method': 'POST',
                'fields': [
                    {'name': 'username', 'type': 'text'},
                    {'name': 'password', 'type': 'password'},
                    {'name': '', 'type': 'submit'}
                ]
            }]
        },
        'script_fingerprint': {
            'script_count': 2,
            'inline_scripts': 0,
            'script_sources': ['/js/main.js', '/js/jquery.min.js']
        },
        'meta_fingerprint': {
            'description': 'Secure banking',  # SAME
            'author': 'BankCorp'              # SAME
        },
        'link_pattern': {
            'total_links': 2,
            'sample_links': ['/login', '/register']
        },
        'hidden_elements': {
            'hidden_count': 1
        }
    }

    # Run detection
    detector = CloneDetector(threshold=0.85)
    result = detector.compare(features_original, features_clone)

    # Print report
    detector.print_report(result)

    return result


if __name__ == "__main__":
    test_model()