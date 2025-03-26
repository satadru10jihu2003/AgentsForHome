from openai import OpenAI

__all__ = ['public_function']

client = OpenAI()

def read_file(file_path):
    with open(file_path, "r") as file_content:
        return file_content.read()

def open_file(file_path):
    with open(file_path, "rb") as file_content:
                result = client.files.create(
                    file=file_content,
                    purpose="user_data"
                )
    print(result.id)
    return result.id

def create_vector_store():
    vector_store = client.vector_stores.create(
        name="knowledge_base"
    )
    print(vector_store.id)
    return vector_store

def add_file_to_vector_store(vector_store, file_id):
    client.vector_stores.files.create(
        vector_store_id=vector_store.id,
        file_id=file_id
    )

def check_status(vector_store):
    result = client.vector_stores.files.list(
        vector_store_id=vector_store.id
    )
    print(result.data)
     