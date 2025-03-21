import sqlite3
from dotenv import load_dotenv
import os
from qgis.core import QgsProject, QgsApplication

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SQLiteVec

load_dotenv()

# Config
DATABASE_PATH = os.getenv("DATABASE_PATH")
EMBEDDING_TABLE_NAME = os.getenv("EMBEDDING_TABLE_NAME")
FILTER_QGIS_LAYER = os.getenv("FILTER_QGIS_LAYER")
FROM_TABLE = os.getenv("FROM_TABLE")

qgs = QgsApplication([], False)
# Load providers
qgs.initQgis()


def add_score_column() -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        # get reasonable columns names
        cursor.execute(f"PRAGMA table_info({FILTER_QGIS_LAYER})")
        columns = [col[1] for col in cursor.fetchall()]
        print(columns)

        if "score" in columns:
            return
        conn.execute(f"""
            ALTER TABLE "{FILTER_QGIS_LAYER}"
            ADD COLUMN score FLOAT
        """)
        conn.commit()

def search(query: str) -> None:
    add_score_column()
    # Initialize the embedder
    embedder = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # Create vector store table
    vector_store = SQLiteVec(
        connection=SQLiteVec.create_connection(db_file=DATABASE_PATH),
        table=EMBEDDING_TABLE_NAME,
        embedding=embedder,
    )

    # Perform similarity search over embeddings table
    result = vector_store.similarity_search_with_score(query, k=100)
    scores = [(item[1], item[0].metadata['fid']) for item in result]

    # Update scores for matched records
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.executemany(
            f"UPDATE {FROM_TABLE} SET score = ? WHERE fid = ?",
            scores
        )
        conn.commit()

    return result


def filter(query: str) -> None:
    searched = search(query)
    joined_fids = ','.join(list(map(lambda i: str(i[0].metadata['fid']), searched)))
    expression = f"fid IN ({joined_fids})"
    project = QgsProject()
    project.read("project.qgz")

    for node in project.layerTreeRoot().findLayers():
        layer = node.layer()
        if layer.name() == FILTER_QGIS_LAYER:
            layer.setSubsetString(expression)
    
    project.write("project.qgz")


if __name__ == "__main__":
    filter("Where is Einstein?")
