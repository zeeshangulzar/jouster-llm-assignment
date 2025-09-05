#!/usr/bin/env python3
"""Simple test for keyword extraction"""

from text_processing import extract_keywords

def test_keywords():
    text = "Artificial intelligence is revolutionizing healthcare"
    keywords = extract_keywords(text)
    print(f"Keywords: {keywords}")
    assert len(keywords) <= 3
    print("Test passed!")

if __name__ == "__main__":
    test_keywords()
