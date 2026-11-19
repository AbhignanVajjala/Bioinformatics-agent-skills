"""Plan or fetch public metadata; network retrieval requires the explicit --live flag."""

import argparse
import json
from pathlib import Path

from bioskills.retrieval import retrieve_metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=["geo", "sra", "ensembl"])
    parser.add_argument("identifier")
    parser.add_argument("--page", type=int, default=0)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output must be a new file")
    result = retrieve_metadata(args.source, args.identifier, page=args.page, dry_run=not args.live)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["download_status"])


if __name__ == "__main__":
    main()
