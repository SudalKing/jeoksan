from pathlib import Path

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.classification import Classification
from etl.extract import iter_jsonl
from etl.normalize import normalize_unit

LEVEL_FIELDS = range(1, 6)


def _row_to_values(
        row: dict,
        alias_map: dict
) -> dict:
    raw_unit = row.get("unit")
    values = {
        "item_code": row["qtyCalcCtyclcd"].strip(),
        "work_type_code": row.get("cnstwkDivCd"),
        "work_type_name": row.get("cnstwkDivNm"),
        "item_name": row.get("qtyCalcCtyclNm"),
        "spec": row.get("spec"),
        "raw_unit": raw_unit,
        "canonical_unit": normalize_unit(raw_unit, alias_map),
    }
    for n in LEVEL_FIELDS:
        values[f"level{n}_code"] = row.get(f"LvlqtyCalcCtyclCd{n}")
        values[f"level{n}_name"] = row.get(f"LvlqtyCalcCtyclNm{n}")
        values[f"level{n}_description"] = row.get(f"LvlqtyCalcCtyclDscrpt{n}")

    return values


def load_classification(
        session: Session,
        path: Path,
        alias_map: dict
) -> dict:
    inserted = 0
    skipped = 0
    for row in iter_jsonl(path):
        code = (row.get("qtyCalcCtyclcd") or "").strip()
        if not code:
            skipped += 1
            continue
        values = _row_to_values(row, alias_map)
        stmt = insert(Classification).values(**values)
        update_cols = {k: v for k, v in values.items() if k != "item_code"}
        stmt = stmt.on_conflict_do_update(index_elements=["item_code"], set_=update_cols)
        session.execute(stmt)
        inserted += 1
    session.commit()

    return {"inserted": inserted, "skipped": skipped}
