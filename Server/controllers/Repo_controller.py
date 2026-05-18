import time
import uuid
from github import Github
from github import Auth
from sentence_transformers import SentenceTransformer
from controllers.Chat_controller import getRepoNameFromConversationId, fetch_all_conversations
from controllers.code_controller import extract_function_names, get_file_code, create_chunk, extract_ui_text
from config.config import GITHUB_TOKEN
import os
from qdrant import client
from qdrant_client.models import Document, VectorParams, Distance, PointStruct, PayloadSchemaType

auth = Auth.Token(GITHUB_TOKEN)


g = Github(auth=auth)

model = SentenceTransformer("all-MiniLM-L6-v2")


IGNORE_DIRS = {
    ".git",
    ".github",
    ".vscode",
    "node_modules",
    "venv",
    "__pycache__",
    ".idea",
    "dist",
    "build",
    ".next"
}

IGNORE_FILES = {
    ".DS_Store",
    ".gitignore",
    ".env",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock"
}

IGNORE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".pdf",
    ".zip",
    ".exe"
}


def normalize_repo_name(repo_url: str) -> str:
    return repo_url.split("github.com/")[-1].removesuffix(".git").rstrip("/")


def ensure_repo_chunks_collection():
    if not client.collection_exists(collection_name="repo_chunks"):
        client.create_collection(
            collection_name="repo_chunks",
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )

    collection_info = client.get_collection(collection_name="repo_chunks")
    repo_name_index = collection_info.payload_schema.get("repo_name")

    if not repo_name_index or repo_name_index.data_type != PayloadSchemaType.KEYWORD:
        client.create_payload_index(
            collection_name="repo_chunks",
            field_name="repo_name",
            field_schema=PayloadSchemaType.KEYWORD,
        )


def upsert_repo_chunks(points):
    try:
        client.upsert(
            collection_name="repo_chunks",
            points=points,
        )
    except Exception:
        ensure_repo_chunks_collection()
        client.upsert(
            collection_name="repo_chunks",
            points=points,
        )


def search_repos(query):
    try:
        repos = g.search_repositories(query=query)
        normalized_repos = []
        for repo in repos:
            normalized_repos.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "description": repo.description
            })  
        return normalized_repos
    except Exception as e:
        print(f"Error occurred while searching repositories: {e}")
        return []



def get_Readme(repo_url):
    try:
        repo_name = normalize_repo_name(repo_url)
        # print(f"Fetching README for repo: {repo_name}") #debugging log
        repo = g.get_repo(repo_name)
        readme = repo.get_readme()
        return {"readme": readme.decoded_content.decode("utf-8")}
    except Exception as e:
        print(f"Error occurred while fetching README: {e}")
        return {"error": str(e)}


def create_data_for_embedding(repo_url):
    try:
        repo_name = normalize_repo_name(repo_url)
        # print(f"Fetching file tree for repo: {repo_name}") #debugging log
        repo = g.get_repo(repo_name)
        contents = repo.get_contents("")
        file_tree = []
        total_usable_files = 0
        while contents:
            file_content = contents.pop(0)
            
            print(f"Processing file: {file_content}") #debugging log
            path_parts = file_content.path.split("/")
            filename = os.path.basename(file_content.path)

            # Ignore directories anywhere in path
            if any(part in IGNORE_DIRS for part in path_parts):
                continue

            # Ignore specific files
            if filename in IGNORE_FILES:
                continue

            # Ignore file extensions
            if any(filename.endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            if file_content.type == "file":
                code = get_file_code(repo,file_content.path)
            else:
                code = None
            file_tree.append({
                "code": code,
                "path": file_content.path,
                "type": file_content.type,
                "size": file_content.size,
            })

            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            total_usable_files+=1

        c = []

        for file_info in file_tree:
            print(f"Creating chunks for file: {file_info['path']} with size: {file_info['size']} bytes") #debugging log
            chunks = create_chunk(file_info)
            if not chunks:
                print(f"No chunks created for file: {file_info['path']}") #debugging log
                continue
            c.append({
                "path": file_info['path'],
                "chunks": chunks,
                "chunks_len": len(chunks)
            })
            print(f"Created {len(chunks)} chunks for file: {file_info['path']}") #debugging log

        
        return { "total_usable_files": total_usable_files, "chunk_data": c}
    except Exception as e:
        print(f"Error occurred while fetching file tree: {e}")
        return {"error": str(e)}




def upload_repo_on_qdrant(url):
    try:
        print(f"Starting upload for repo at {url}")
        repo_name = normalize_repo_name(url)

        ensure_repo_chunks_collection()

        chunk_data = create_data_for_embedding(url)
        points = []
        for file in chunk_data["chunk_data"]:
            path = file["path"]
            for i, chunk in enumerate(file["chunks"]):
                if path.split("/")[-1] == "README.md":
                    search_text = f"file: {path.split('/')[-1]} content: {chunk}"
                    vec = model.encode(search_text).tolist()
                    points.append(
                        PointStruct(
                            id=str(uuid.uuid4()),
                            vector=vec,
                            payload={
                                "repo_name": repo_name,
                                "file_path": path,
                                "file_name" : path.split("/")[-1],
                                "chunk_index": i,
                                "text": chunk
                            }

                        )

                    )
                    continue
                
                Functions_name = extract_function_names(chunk, language=path.split(".")[-1])
                UI_texts = extract_ui_text(chunk)
                search_text = f"""
                    file: {path.split("/")[-1]}
                    functions: {", ".join(Functions_name)}
                    ui_text: {UI_texts}
                """
                vec = model.encode(search_text).tolist()
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=vec,
                        payload={
                            "repo_name": repo_name,
                            "file_path": path,
                            "file_name" : path.split("/")[-1],
                            "chunk_index": i,
                            "text": chunk
                        }

                    )

                )
        upsert_repo_chunks(points)

        print(f"Upload completed for repo at {url}")
        
        return {"message": f"Repo at {url} uploaded successfully"}
    except Exception as e:
        print(f"Error occurred while uploading repo to Qdrant: {e}")
        return {"error": str(e)}
    

def search_in_repo(query, conversation_id, top_k=5):
    try:
        ensure_repo_chunks_collection()

        repo_name = getRepoNameFromConversationId(conversation_id)

        if not repo_name:
            raise ValueError(
                f"No conversation found with id: {conversation_id}"
            )

        search_text = f"repo: {repo_name}\n{query}"

        vec = model.encode(search_text).tolist()

        search_result = client.query_points(
            collection_name="repo_chunks",
            query=vec,
            limit=top_k,
            with_payload=True,
            query_filter={
                "must": [
                    {
                        "key": "repo_name",
                        "match": {
                            "value": repo_name
                        }
                    }
                ]
            }
        )

        return search_result

    except Exception as e:
        print(f"Error occurred while searching in repo: {e}")
        return {"error": str(e)}
    

def fetch_all_repos():
    try:
        converasations = fetch_all_conversations()
        return [{"conversation_id": conv.id, "repo_name": conv.repo_name} for conv in converasations]
    except Exception as e:
        print(f"Error occurred while fetching all repos: {e}")
        return {"error": str(e)}
