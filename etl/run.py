from pathlib import Path

from app.core.db import SessionLocal
from etl.load_classification import load_classification
from etl.load_price import load_price
from etl.normalize import ensure_unit_aliases

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    session = SessionLocal()
    try:
        alias_map = ensure_unit_aliases(session)
        classification_result = load_classification(
            session, DATA_DIR / "construction_classification.jsonl", alias_map
        )
        price_result = load_price(session, DATA_DIR / "std_market_price.jsonl", alias_map)
        print(f"classification: {classification_result}")
        print(f"std_market_price: {price_result}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
