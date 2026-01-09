from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    secret_key: str = os.getenv('SECRET_KEY')
    ip_address: str = os.getenv('IP_ADDRESS')
    pinecone_key: str = os.getenv('PINECONE')
    openai_key: str = os.getenv('OPENAI')
    index_name: str = os.getenv('INDEX_NAME')
    pinecone_index_name: str = os.getenv('PINECONE_INDEX_NAME')
    claude_key: str = os.getenv('CLAUDE')

settings = Settings()