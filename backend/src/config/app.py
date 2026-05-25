from pydantic import BaseModel


class AppSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = True

    title: str = "Auth Service API"
    description: str = "Multi-tenant authentication service"
    version: str = "1.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    root_path: str = "/api"