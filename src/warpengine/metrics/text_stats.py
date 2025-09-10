from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List, Tuple

_word_re = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_sentence_re = re.compile(r"[.!?]+\s+")
_vowels = "aeiouy"


def tokenize_words(text: str) -> List[str]:
    return [m.group(0).lower() for m in _word_re.finditer(text)]


def tokenize_sentences(text: str) -> List[str]:
    # Simple sentence split heuristic
    parts = _sentence_re.split(text)
    # If regex splits by the punctuation separator, restore non-empty parts
    return [p.strip() for p in parts if p.strip()]


def count_syllables(word: str) -> int:
    w = word.lower()
    if not w:
        return 0
    # Remove non-alpha
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 0
    # Heuristic: count contiguous vowel groups
    count = 0
    prev_is_vowel = False
    for ch in w:
        is_vowel = ch in _vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    # Trailing silent 'e'
    if w.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def flesch_reading_ease(text: str) -> float:
    words = tokenize_words(text)
    sents = tokenize_sentences(text)
    if not words or not sents:
        return 0.0
    word_count = len(words)
    sent_count = max(1, len(sents))
    syllables = sum(count_syllables(w) for w in words)
    # Flesch Reading Ease score
    # 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
    return 206.835 - 1.015 * (word_count / sent_count) - 84.6 * (syllables / word_count)


def flesch_kincaid_grade(text: str) -> float:
    words = tokenize_words(text)
    sents = tokenize_sentences(text)
    if not words or not sents:
        return 0.0
    word_count = len(words)
    sent_count = max(1, len(sents))
    syllables = sum(count_syllables(w) for w in words)
    return 0.39 * (word_count / sent_count) + 11.8 * (syllables / word_count) - 15.59


def basic_counts(text: str) -> Dict[str, int]:
    words = tokenize_words(text)
    sents = tokenize_sentences(text)
    return {
        "chars": len(text),
        "words": len(words),
        "sentences": len(sents),
        "unique_words": len(set(words)),
    }


def type_token_ratio(text: str) -> float:
    words = tokenize_words(text)
    return (len(set(words)) / len(words)) if words else 0.0


def top_ngrams(text: str, n: int = 2, top_k: int = 10) -> List[Tuple[str, int]]:
    words = tokenize_words(text)
    if len(words) < n:
        return []
    ngrams = [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]
    counts = Counter(ngrams)
    return counts.most_common(top_k)
