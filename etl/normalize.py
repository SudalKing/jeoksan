from typing import Optional

from sqlalchemy.orm import Session

from app.models.unit_alias import UnitAlias


SEED_UNIT_ALIASES = {
    "m": "m",
    "M": "m",
    "㎡": "㎡",
    "M2": "㎡",
    "m2": "㎡",
    "㎥": "㎥",
    "M3": "㎥",
    "m3": "㎥",
    "개": "개",
    "EA": "개",
    "ea": "개",
}


def ensure_unit_aliases(session: Session) -> dict:
    existing = {row.raw_unit: row.canonical_unit for row in session.query(UnitAlias).all()}
    missing = {raw: canon for raw, canon in SEED_UNIT_ALIASES.items() if raw not in existing}
    for raw, canon in missing.items():
        session.add(UnitAlias(raw_unit=raw, canonical_unit=canon))
    if missing:
        session.commit()
        existing.update(missing)

    return existing


def normalize_unit(
        raw_unit: str,
        alias_map: dict
) -> Optional[str]:
    if raw_unit is None:
        return None
    trimmed = raw_unit.strip()

    return alias_map.get(trimmed, trimmed)
