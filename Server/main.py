from qdrant import client
from fastapi import FastAPI
from qdrant_client.models import Document, VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
from upload_worker import enqueue_upload_repo
from pydanticModels import repoUrl, sendChatRequest
from controllers.Chat_controller import upload_chat_to_DB
from controllers.Repo_controller import get_Readme, search_repos, create_data_for_embedding, upload_repo_on_qdrant


app = FastAPI();
model = SentenceTransformer("all-MiniLM-L6-v2")


# client.delete_collection(collection_name="repo_chunks")

# client.create_collection(
#     collection_name="repo_chunks",
#     vectors_config=VectorParams(
#         size=384,
#         distance=Distance.COSINE
#     )
# )

# @app.post("/upload/repo")
# def upload_repo(url: repoUrl):
#     enqueue_upload_repo(url.url)
#     return {"message": "Repo uploaded successfully"}


# @app.get("/search/repo")
# def searchRepo(query: str):
#     return search_repos(query=query)



# @app.get("/repo/readme")
# def getReadme(repo_url: str):
#     return get_Readme(repo_url=repo_url)


# @app.get("/repo/tree")
# def getTree(repo_url: str):
#     return get_Tree(repo_url=repo_url)


### REPO ROUTES ###
@app.post('/repo')
def upload_repo(req: repoUrl):
    jobid = enqueue_upload_repo(req.url)
    return {"message": "Repo upload job enqueued successfully", "job_id": jobid}

@app.delete('/repo')
def delete_repo(url: repoUrl):
    pass



### CHAT ROUTES ###
@app.get('/chat')
def fetch_chat(url : repoUrl):
    pass


@app.post('/chat')
def post_chat(req: sendChatRequest):
    message = {
        "role" : req.role,
        "content" : req.query,
        "conversation_id" : req.conversation_id
    }
    db_message = upload_chat_to_DB(message)

    return {"message": "Chat message uploaded successfully", "db_message": db_message}


# points = []

# for i, text in enumerate(texts):
#     vec = model.encode(text).tolist()
#     points.append(
#         PointStruct(
#             id=i+1,
#             vector=vec,
#             payload={"text": text}
#         )
#     )
# client.upsert(
#     collection_name="repo_chunks",
#     points=points
# )


# generate query embedding
# client.delete_collection(collection_name="repo_chunks")

# vec = model.encode("how auth works").tolist()
# result =  client.query_points(
#     collection_name="repo_chunks",
#     query=vec,
#     limit=5
# )

# print("result :" , result)