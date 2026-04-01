import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:" \
         f"{os.getenv('POSTGRES_PASSWORD')}@" \
         f"{os.getenv('POSTGRES_HOST')}:" \
         f"{os.getenv('POSTGRES_PORT')}/" \
         f"{os.getenv('POSTGRES_DB')}"

engine = create_engine(DB_URI)