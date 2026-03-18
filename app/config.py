from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openrouter_api_key: str
    anthropic_api_key: str = ""
    llm_model: str = "z-ai/glm-4.5-air:free"
    database_url: str
    max_reflection_retries: int = 2

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
