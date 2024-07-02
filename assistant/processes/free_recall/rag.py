# THIS WILL CREATE IN MEMORY INDEX.
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.vectorstores import FAISS

def split_and_create_chunks(docs_path):

    #load all .md files and append it in one string
    all_docs = ""
    
    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as file:
                    all_docs += file.read()
    
    
    # Create the text splitter
    text_splitter = CharacterTextSplitter(
        separator = "###",
        chunk_size = 1000,
        chunk_overlap  = 200, #striding over the text
        length_function = len,
    )

    texts = text_splitter.split_text(all_docs)
    print(len(texts))

    return texts

def create_vector_database(texts):
    
    #Setting up the QARetrieval Chain.
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores import FAISS

    # Download embeddings from OpenAI
    embeddings = OpenAIEmbeddings()

    db = FAISS.from_texts(texts, embeddings) #To see details: db.embedding_function
    retriever = db.as_retriever() #Creates the retriever
    
    return db, retriever

