# EchoWeaver

**Social Media OSINT Tool** — Temporal Correlation + Stylometric Analysis

Unique tool for linking accounts across platforms by timing patterns and writing style. Public data only.

## Live Demo

Once GitHub Pages is enabled, the tool will be available at:

**https://masterxhackerx420-oss.github.io/echoweaver/**

## Features

- Temporal correlation (posts within a configurable time window)
- Lightweight stylometric fingerprinting
- Combined confidence scoring (HIGH / MEDIUM / LOW)
- Fully client-side — no server, no tracking
- Demo data included

## Usage

1. Paste a JSON array of accounts (or click **Load Demo**)
2. Set the time window in minutes
3. Click **Analyze**

### Input Format

```json
[
  {
    "handle": "@username",
    "platform": "X",
    "posts": [
      { "text": "Post content", "timestamp": "2026-10-14 14:22:00" }
    ]
  }
]
```

## Python CLI

The original Python version is also in this repo (`echoweaver.py`).

```bash
python3 echoweaver.py --demo
python3 echoweaver.py --input sample_input.json --export report.json
```

## License

Research and educational use. Public data only.

DebianGang / WolfSec
