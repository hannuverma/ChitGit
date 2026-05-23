from qdrant import client
from fastapi import FastAPI, HTTPException
from qdrant_client.models import Document, VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
from upload_worker import enqueue_upload_repo, get_job_status
from pydanticModels import repoUrl, sendChatRequest, Message as MessageSchema
from controllers.Chat_controller import fetch_all_messages_for_conversation, upload_chat_to_DB, create_conversation
from controllers.Repo_controller import search_in_repo, ensure_repo_chunks_collection, fetch_all_repos
from controllers.Ai_first_layer import get_query_enhanced,final_ai_response
from fastapi.middleware.cors import CORSMiddleware
from config.config import ENV
import os
import uvicorn
origins = {
    "http://localhost:5173", "https://chit-git.vercel.app"
}
IS_PRODUCTION = (ENV == "production")

app = FastAPI(
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defer heavy model loading to controllers which will lazy-load when needed


@app.on_event("startup")
def prepare_qdrant_indexes():
    ensure_repo_chunks_collection()


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
    conversation = create_conversation(req.url)
    return {"message": "Repo upload job enqueued successfully", "job_id": jobid, "conversation_id": conversation.id}

@app.delete('/repo')
def delete_repo(url: repoUrl):
    pass

@app.get('/all-repos')
def get_all_repos():
    return fetch_all_repos()


### JOB STATUS ###
@app.get('/job/{job_id}')
def job_status(job_id:str):
    status = get_job_status(job_id)
    return {"job_id": job_id, "status": status, "completed": status.get("status") == "finished"}

### CHAT ROUTES ###
@app.get('/chat/{conversation_id}')
def fetch_chat(conversation_id: int):
    return fetch_all_messages_for_conversation(conversation_id)


@app.post('/chat')
def post_chat(req: MessageSchema):
    try:
        enhanced_user_query = get_query_enhanced(req.content)
        search_result = search_in_repo(enhanced_user_query, req.conversation_id, top_k = 10)
        string_search_result = ""
        for res in search_result:
            string_search_result += f"{res}\n"
        
        Final_ai = final_ai_response(string_search_result, req.content)

        AiResponse = MessageSchema(
        conversation_id=req.conversation_id,
        role="assistant",
        content=Final_ai
        )
    except Exception as e:
        print(f"Error occurred while processing chat message: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the chat message.")

    db_message = upload_chat_to_DB(req)
    db_message_2 = upload_chat_to_DB(AiResponse)
    return {"message": "Chat message uploaded successfully", "enhanced_query": enhanced_user_query, "db_message": db_message, "search_result": search_result, "final_ai_answer": Final_ai, "db_message_2": db_message_2}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )


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