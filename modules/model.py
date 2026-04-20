from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------
# TEXT SIMILARITY
# -------------------------
def text_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([text1, text2])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return score


# -------------------------
# TAG STRUCTURE SIMILARITY
# -------------------------
def tag_similarity(tags1, tags2):
    all_tags = set(tags1.keys()).union(set(tags2.keys()))

    v1 = []
    v2 = []

    for tag in all_tags:
        v1.append(tags1.get(tag, 0))
        v2.append(tags2.get(tag, 0))

    return cosine_similarity([v1], [v2])[0][0]


# -------------------------
# LINK SIMILARITY
# -------------------------
def link_similarity(links1, links2):
    set1 = set(links1)
    set2 = set(links2)

    if not set1 and not set2:
        return 0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union


# -------------------------
# FINAL COMBINED SCORE
# -------------------------
def compute_final_score(data1, data2):
    text_score = text_similarity(data1["text"], data2["text"])
    tag_score = tag_similarity(data1["tag_freq"], data2["tag_freq"])
    link_score = link_similarity(data1["links"], data2["links"])

    # 🔥 Weighted scoring (important for viva)
    final_score = (
        0.5 * text_score +
        0.3 * tag_score +
        0.2 * link_score
    )

    details = {
        "text_similarity": round(text_score, 4),
        "tag_similarity": round(tag_score, 4),
        "link_similarity": round(link_score, 4)
    }

    return round(final_score, 4), details