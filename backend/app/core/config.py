from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    vector_store_path: str = "./data/vector_store"
    collection_name: str = "basic_electronics"
    embedding_model_name: str = "all-MiniLM-L6-v2"

    ollama_model: str = "llama3.1"

    top_k: int = 3

    yolo_model_path: str = "./data/yolo_model/best.pt"
    yolo_confidence: float = 0.25

    cors_origins: str = "http://localhost:8501"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
