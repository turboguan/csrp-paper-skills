from __future__ import annotations

import argparse
from pathlib import Path

from csrp_skills.adjudication import build_gold_from_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--family-id", required=True)
    args = parser.parse_args()

    records = build_gold_from_csv(args.input, args.family_id)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "\n".join(record.model_dump_json() for record in records) + "\n",
        encoding="utf-8",
    )
    print({
        "records": len(records),
        "adjudicated": sum(r.status.value == "adjudicated" for r in records),
        "double_reviewed_unresolved": sum(r.status.value == "double_reviewed" for r in records),
        "output": str(out),
    })


if __name__ == "__main__":
    main()
