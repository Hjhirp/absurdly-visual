from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Environment
    ENV: str = Field(default="development", env="ENV")
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, env="PORT")  # Railway sets PORT env var
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET: str = "videos"
    SUPABASE_WINNING_BUCKET: str = "winning-videos"
    
    
    # AI Services (Gemini API used for images, videos, and text)
    GEMINI_API_KEY: str = ""
    VIDEO_FETCH_TIMEOUT: int = 90  # Time to wait for video to be ready in Supabase
    USE_VEO3_FAST: bool = True
    VIDEO_DURATION: int = 4  # Duration in seconds (4-8)
    VIDEO_PLACEHOLDER_URL: str = "https://via.placeholder.com/640x480/FF6B6B/FFFFFF?text=Video+Generation+Failed"
    
    # Game Configuration
    MAX_PLAYERS: int = 8
    MIN_PLAYERS: int = 3
    CARDS_PER_HAND: int = 5
    POINTS_TO_WIN: int = 7
    ROUND_TIMEOUT: int = 120  # seconds
    
    # CORS - Allow Railway frontend and localhost
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        env="CORS_ORIGINS"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
