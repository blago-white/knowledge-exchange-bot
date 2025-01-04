from dotenv import load_dotenv

load_dotenv()

import os

from sqlalchemy import create_engine


engine = create_engine("postgresql+psycopg2://"
                       f"{os.environ.get('POSTGRES_USER')}:"
                       f"{os.environ.get('POSTGRES_PASSWORD')}@"
                       f"knowledgedb/"
                       f"{os.environ.get('POSTGRES_DB')}")

print(engine.echo)
