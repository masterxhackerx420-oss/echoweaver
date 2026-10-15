#!/usr/bin/env python3
"""
EchoWeaver - Social Media OSINT Tool
Temporal Correlation + Stylometric Analysis Engine

Unique OSINT tool for linking accounts across platforms by timing and writing style.
Public data only. For research and educational use.
"""

import argparse
import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import List, Dict

VERSION = "0.1.0"
TOOL_NAME = "EchoWeaver"

def extract_style_features(text: str) -> Dict[str, float]:
    if not text:
        return {}
    words = re.findall(r"\b\w+\b", text.lower())
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    features = {
        "avg_word_length": sum(len(w) for w in words) / max(len(words), 1),
        "avg_sentence_length": len(words) / max(len(sentences), 1),
        "unique_word_ratio": len(set(words)) / max(len(words), 1),
        "punctuation_density": len(re.findall(r'[.,!?;:]', text)) / max(len(text), 1),
        "emoji_count": len(re.findall(r'[\U0001F600-\U0001F64F]', text)),
        "caps_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1),
    }
    return features

def style_similarity(features_a: Dict, features_b: Dict) -> float:
    if not features_a or not features_b:
        return 0.0
    keys = set(features_a.keys()) & set(features_b.keys())
    if not keys:
        return 0.0
    scores = []
    for k in keys:
        a, b = features_a[k], features_b[k]
        if a == 0 and b == 0:
            scores.append(1.0)
        else:
            diff = abs(a - b) / max(a, b, 0.001)
            scores.append(1.0 - min(diff, 1.0))
    return sum(scores) / len(scores)

def parse_time(ts: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    return datetime.now()

def temporal_overlap(posts_a: List[Dict], posts_b: List[Dict], window_minutes: int = 15) -> float:
    if not posts_a or not posts_b:
        return 0.0
    matches = 0
    for pa in posts_a:
        ta = parse_time(pa.get("timestamp", ""))
        for pb in posts_b:
            tb = parse_time(pb.get("timestamp", ""))
            delta = abs((ta - tb).total_seconds()) / 60
            if delta <= window_minutes:
                content_sim = SequenceMatcher(None, pa.get("text", "")[:100].lower(), pb.get("text", "")[:100].lower()).ratio()
                if content_sim > 0.3 or delta < 5:
                    matches += 1
    return min(matches / max(len(posts_a), 1), 1.0)

def generate_mock_data() -> List[Dict]:
    return [
        {"handle": "@target_alpha", "platform": "X", "posts": [
            {"text": "Just saw the news about the data center outage. This is getting serious.", "timestamp": "2026-10-14 14:22:00"},
            {"text": "Anyone else notice the pattern here? Same playbook every time.", "timestamp": "2026-10-14 14:35:00"},
            {"text": "The timeline doesn't add up. Something's off.", "timestamp": "2026-10-14 18:10:00"}
        ]},
        {"handle": "@shadow_beta", "platform": "Reddit", "posts": [
            {"text": "Saw the data center outage news. This is getting serious.", "timestamp": "2026-10-14 14:24:00"},
            {"text": "Same pattern every single time. Not a coincidence.", "timestamp": "2026-10-14 14:38:00"},
            {"text": "Timeline is inconsistent. Digging deeper.", "timestamp": "2026-10-14 18:15:00"}
        ]},
        {"handle": "@unrelated_gamma", "platform": "X", "posts": [
            {"text": "Beautiful weather today. Going for a hike.", "timestamp": "2026-10-14 09:00:00"},
            {"text": "Coffee and code. Perfect morning.", "timestamp": "2026-10-14 11:30:00"},
            {"text": "New album dropped. Highly recommend.", "timestamp": "2026-10-14 20:00:00"}
        ]},
        {"handle": "@alt_delta", "platform": "Instagram", "posts": [
            {"text": "The outage is bigger than they're saying. Pattern recognition.", "timestamp": "2026-10-14 14:26:00"},
            {"text": "Not buying the official story. Timeline is cooked.", "timestamp": "2026-10-14 18:12:00"}
        ]}
    ]

def analyze_accounts(accounts: List[Dict], window_minutes: int = 15) -> List[Dict]:
    results = []
    for acc in accounts:
        all_text = " ".join(p.get("text", "") for p in acc.get("posts", []))
        acc["style"] = extract_style_features(all_text)
    for i, a in enumerate(accounts):
        for b in accounts[i+1:]:
            temp_score = temporal_overlap(a.get("posts", []), b.get("posts", []), window_minutes)
            style_score = style_similarity(a.get("style", {}), b.get("style", {}))
            confidence = (temp_score * 0.65) + (style_score * 0.35)
            if confidence > 0.15:
                results.append({
                    "account_a": f"{a['handle']} ({a['platform']})",
                    "account_b": f"{b['handle']} ({b['platform']})",
                    "temporal_score": round(temp_score, 3),
                    "style_score": round(style_score, 3),
                    "confidence": round(confidence, 3),
                    "signal": "HIGH" if confidence > 0.6 else "MEDIUM" if confidence > 0.35 else "LOW"
                })
    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results

def print_banner():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ECHOWEAVER v0.1.0                                      ║
    ║   Temporal Correlation • Stylometric OSINT                 ║
    ║                                                           ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

def print_results(results: List[Dict]):
    print("\n" + "═" * 70)
    print("  CORRELATION RESULTS")
    print("═" * 70)
    if not results:
        print("  No significant correlations found.")
        return
    for i, r in enumerate(results, 1):
        signal_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(r["signal"], "⚪")
        print(f"\n  [{i}] {signal_color} {r['signal']} CONFIDENCE: {r['confidence']:.1%}")
        print(f"      {r['account_a']}")
        print(f"      ↔ {r['account_b']}")
        print(f"      Temporal: {r['temporal_score']:.1%}  |  Style: {r['style_score']:.1%}")
    print("\n" + "═" * 70)

def main():
    parser = argparse.ArgumentParser(description="EchoWeaver - Social Media Temporal & Stylometric OSINT Tool")
    parser.add_argument("--demo", action="store_true", help="Run with built-in demo data")
    parser.add_argument("--window", type=int, default=15, help="Temporal window in minutes")
    parser.add_argument("--export", type=str, help="Export results to JSON file")
    parser.add_argument("--input", type=str, help="Path to JSON input file")
    args = parser.parse_args()
    print_banner()
    if args.input:
        with open(args.input) as f:
            accounts = json.load(f)
        print(f"  Loaded {len(accounts)} accounts from {args.input}")
    else:
        accounts = generate_mock_data()
        print("  Running in DEMO mode with synthetic data")
    print(f"  Temporal window: ±{args.window} minutes")
    print(f"  Analyzing {len(accounts)} accounts...\n")
    results = analyze_accounts(accounts, args.window)
    print_results(results)
    if args.export:
        with open(args.export, "w") as f:
            json.dump({"tool": TOOL_NAME, "version": VERSION, "results": results}, f, indent=2)
        print(f"\n  Report exported → {args.export}")
    print("\n  EchoWeaver complete.\n")

if __name__ == "__main__":
    main()
