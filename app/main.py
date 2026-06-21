from fastapi import FastAPI

from app.api.routes import classification, quantity_item

app = FastAPI(title="공종 단가 조회 시스템")

app.include_router(classification.router)
app.include_router(quantity_item.router)


@app.get("/health")
def health():
    return {"status": "success"}
