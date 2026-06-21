from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Publication


def list_publications(session: Session):
    stmt = select(Publication).order_by(Publication.published_date.desc())
    rows = session.execute(stmt).scalars().all()
    total = session.execute(select(func.count())).scalar_one()

    return total, rows가