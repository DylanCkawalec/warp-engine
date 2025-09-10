from warpengine.metrics.text_stats import (
    tokenize_words,
    tokenize_sentences,
    count_syllables,
    basic_counts,
    type_token_ratio,
    top_ngrams,
    flesch_reading_ease,
    flesch_kincaid_grade,
)


def test_text_stats_basic():
    text = "This is a simple sentence. This is another one!"
    words = tokenize_words(text)
    sents = tokenize_sentences(text)
    assert len(words) >= 9
    assert len(sents) >= 2
    counts = basic_counts(text)
    assert counts["words"] == len(words)
    assert counts["sentences"] == len(sents)


def test_syllables_and_readability():
    assert count_syllables("language") >= 2
    text_easy = "This is a short sentence. It is easy to read."
    fre = flesch_reading_ease(text_easy)
    fk = flesch_kincaid_grade(text_easy)
    assert fre > 50
    assert fk >= 0


def test_lexical_and_ngrams():
    text = "word word word test test alpha beta beta gamma"
    ttr = type_token_ratio(text)
    assert 0 < ttr <= 1
    bigrams = top_ngrams(text, n=2, top_k=5)
    assert isinstance(bigrams, list)
