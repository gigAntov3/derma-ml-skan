from pydantic import BaseModel


class DatabaseSettings(BaseModel):
    """Database settings"""

    driver: str = "postgresql+asyncpg"

    host: str = "postgres-db"
    port: int = 5432
    name: str = "derma_ml_db"
    user: str = "derma_user"
    password: str = "strong_password_123"

    sqlite_path: str = "./base.db"

    echo: bool = False

    @property
    def url(self) -> str:
        """Build database URL"""

        if "sqlite" in self.driver:
            return f"{self.driver}:///{self.sqlite_path}"

        return (
            f"{self.driver}://"
            f"{self.user}:{self.password}"
            f"@{self.host}:{self.port}"
            f"/{self.name}"
        )