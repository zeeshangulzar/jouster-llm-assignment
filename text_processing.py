import re
from collections import Counter
from typing import List

def extract_keywords(text: str) -> List[str]:
    """Extract 3 most frequent nouns from text"""
    # Simple noun extraction using regex
    words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
    # Filter out common words
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'}
    words = [word for word in words if word not in stop_words and len(word) > 3]
    word_counts = Counter(words)
    return [word for word, count in word_counts.most_common(3)]
