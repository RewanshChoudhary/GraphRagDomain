import logging

from graphrag_entertainment.ingestion.db_conn import (
    get_neo4j_driver,
    get_postgres_connection,
)
from graphrag_entertainment.ingestion.models import Chunk
from graphrag_entertainment.model_interface import get_agent
from psycopg.rows import class_row

logger = logging.getLogger(__name__)

conn = get_postgres_connection()
conn_neo = get_neo4j_driver()
def create_graph():
            
    try :
        with conn.cursor(row_factory=class_row(Chunk)) as cur:
         cur.execute("""Select *  from  chunk  LIMIT 1000""")
         data:list[Chunk]=cur.fetchall()

         process_chunks(data)





    except Exception :
       logger.exception("Error creating the graph  create_graph() ")
       conn.rollback()
       raise
    finally:
       conn.close()
       conn_neo.close()



def process_chunks(data:list[Chunk]):
    conn_neo=get_neo4j_driver()
    agent=get_agent()

    
    for chunk in data:
       

       
       
       
