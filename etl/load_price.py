from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.price import StdMarketPrice
from etl.extract import iter_jsonl
from etl.normalize import normalize_unit


def _parse_date(raw: Optional[str]):
    if not raw:
        return None

    return datetime.strptime(raw, "%Y%m%d").date()


def _parse_number(raw):
    if raw is None or raw == "":
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def load_price(
        session: Session,
        path: Path,
        alias_map: dict
) -> dict:
    inserted = 0
    skipped = 0
    for row in iter_jsonl(path):
        code = (row.get("qtyCalcCtyclcd") or "").strip() or None
        raw_unit = row.get("unit")
        values = {
            "item_code": code,
            "work_type_code": row.get("cnstwkDivCd"),
            "work_type_name": row.get("cnstwkDivCdNm"),
            "product_name": row.get("prdnm"),
            "spec": row.get("spec"),
            "raw_unit": raw_unit,
            "canonical_unit": normalize_unit(raw_unit, alias_map),
            "material_cost": _parse_number(row.get("mtrlcstUprc")),
            "labor_cost": _parse_number(row.get("lbrcstUprc")),
            "expense_cost": _parse_number(row.get("gnrexpnsUprc")),
            "published_date": _parse_date(row.get("pblctDate")),
            "price_condition_note": row.get("uprcAplCndtnCntnts"),
        }
        if values["published_date"] is None:
            skipped += 1
            continue
        stmt = insert(StdMarketPrice).values(**values)
        update_cols = {k: v for k, v in values.items() if k not in ("item_code", "published_date")}
        stmt = stmt.on_conflict_do_update(
            index_elements=["item_code", "published_date"], set_=update_cols
        )
        session.execute(stmt)
        inserted += 1
    session.commit()

    return {"inserted": inserted, "skipped": skipped}
