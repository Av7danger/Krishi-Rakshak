from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from .config import settings
from .db import engine
from .api import auth as auth_router
from .logging_conf import configure_logging
from .api import upload as upload_router
from .api import reports as reports_router
from .api import feedback as feedback_router
from .api.webhooks import telegram as telegram_router
from .api.webhooks import whatsapp as whatsapp_router
from .api import websocket as websocket_router

app = FastAPI(title="KrishiRakshak Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    configure_logging()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

app.include_router(auth_router.router, prefix=settings.API_PREFIX)
app.include_router(upload_router.router, prefix=settings.API_PREFIX)
app.include_router(reports_router.router, prefix=settings.API_PREFIX)
app.include_router(feedback_router.router, prefix=settings.API_PREFIX)
app.include_router(telegram_router.router, prefix=settings.API_PREFIX)
app.include_router(whatsapp_router.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"ok": True}


# Allow cookie-based JWT if present
@app.middleware("http")
async def cookie_bearer_passthrough(request: Request, call_next):
    if "authorization" not in request.headers and (tok := request.cookies.get("krishi_token")):
        request.headers.__dict__["_list"].append((b"authorization", f"Bearer {tok}".encode()))
    return await call_next(request)
