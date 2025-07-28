"""FastAPI application entrypoint."""

from fastapi import FastAPI

from .auth import router as auth_router
from .routers.tenant import router as tenant_router
from .services.upload import router as upload_router
from .services.kb import router as kb_router

app = FastAPI(title="RAAN Platform")

app.include_router(auth_router)
app.include_router(tenant_router)
app.include_router(upload_router)
app.include_router(kb_router)
