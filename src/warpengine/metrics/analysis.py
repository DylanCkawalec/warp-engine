from __future__ import annotations

import json
from typing import Dict, Any

from .text_stats import (
    basic_counts,
    flesch_kincaid_grade,
    flesch_reading_ease,
    type_token_ratio,
    top_ngrams,
)


def analyze_text(text: str) -> Dict[str, Any]:
    counts = basic_counts(text)
    fre = flesch_reading_ease(text)
    fk = flesch_kincaid_grade(text)
    ttr = type_token_ratio(text)
    bigrams = top_ngrams(text, n=2, top_k=10)
    trigrams = top_ngrams(text, n=3, top_k=10)
    return {
        "counts": counts,
        "readability": {
            "flesch_reading_ease": round(fre, 3),
            "flesch_kincaid_grade": round(fk, 3),
        },
        "lexical": {
            "type_token_ratio": round(ttr, 4),
        },
        "top_bigrams": bigrams,
        "top_trigrams": trigrams,
    }


def analyze_text_pair(input_text: str, output_text: str) -> Dict[str, Any]:
    inp = analyze_text(input_text)
    out = analyze_text(output_text)
    # Simple deltas
    delta = {
        "chars": (out["counts"]["chars"] - inp["counts"]["chars"]),
        "words": (out["counts"]["words"] - inp["counts"]["words"]),
        "sentences": (out["counts"]["sentences"] - inp["counts"]["sentences"]),
        "unique_words": (out["counts"]["unique_words"] - inp["counts"]["unique_words"]),
        "flesch_reading_ease": (
            out["readability"]["flesch_reading_ease"]
            - inp["readability"]["flesch_reading_ease"]
        ),
        "flesch_kincaid_grade": (
            out["readability"]["flesch_kincaid_grade"]
            - inp["readability"]["flesch_kincaid_grade"]
        ),
        "type_token_ratio": (
            out["lexical"]["type_token_ratio"] - inp["lexical"]["type_token_ratio"]
        ),
    }
    return {"input": inp, "output": out, "delta": delta}


def extract_printable_metrics(metrics: Dict[str, Any]) -> str:
    # Pretty-print a concise report
    counts_in = metrics.get("input", {}).get("counts", {})
    counts_out = metrics.get("output", {}).get("counts", {})
    read_in = metrics.get("input", {}).get("readability", {})
    read_out = metrics.get("output", {}).get("readability", {})
    lex_in = metrics.get("input", {}).get("lexical", {})
    lex_out = metrics.get("output", {}).get("lexical", {})
    delta = metrics.get("delta", {})
    report = {
        "input_counts": counts_in,
        "output_counts": counts_out,
        "input_readability": read_in,
        "output_readability": read_out,
        "input_lexical": lex_in,
        "output_lexical": lex_out,
        "delta": delta,
    }
    return json.dumps(report, indent=2)
