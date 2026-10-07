import json
from pathlib import Path

from csrp_skills.models import PaperSkill


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "schemas" / "paper_skill.generated.schema.json"
    out.write_text(json.dumps(PaperSkill.model_json_schema(), indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
