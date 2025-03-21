import os
from dotenv import load_dotenv
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import torchvision
from langchain_community.vectorstores import SQLiteVec

from gpkg_convertor import GPKGConverter
from embedding_query import QUERY

load_dotenv()

# disable warnings
torchvision.disable_beta_transforms_warning()

# Config
DATABASE_PATH = os.getenv("DATABASE_PATH")
EMBEDDING_TABLE_NAME = os.getenv("EMBEDDING_TABLE_NAME")
FROM_TABLE = os.getenv("FROM_TABLE")


def main() -> None:
    """Here fun is called"""
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
    # Convert sql to strings ready to embedding
    converter = GPKGConverter(source=DATABASE_PATH)
    sentences = converter.convert(QUERY)

    # Add sentences to vector store
    texts = list(map(lambda i: i[0], sentences))
    metadatas = list(map(lambda i: {"fid": i[1].get("fid"), "table_name": FROM_TABLE }, sentences))
    vector_store.add_texts(texts=texts, metadatas=metadatas)

    print(f"Added {len(sentences)} records")

if __name__ == "__main__":
    main()
