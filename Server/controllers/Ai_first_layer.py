SYSTEM_PROMPT = """
You are a retrieval query optimizer for a GitHub repository AI assistant.

Your task is to improve semantic search retrieval while preserving the user's original intent.

Rules:
- Keep the original meaning intact.
- Keep important nouns and intent words from the original query.
- Only add helpful technical keywords and related concepts.
- Do NOT generalize the query too much.
- Do NOT answer the question.
- Do NOT remove core entities from the user query.
- Return a concise enhanced search query.

Examples:

User:
Which routes require authentication?

Output:
routes requiring authentication protected routes JWT middleware requireAuth upload routes bearer token

User:
Where is mockPapers used?

Output:
mockPapers usage imports references React components frontend data flow

User:
How does upload work?

Output:
upload flow file upload multipart form-data cloudinary upload API protected upload route
"""

from openrouter import OpenRouter
from config.config import OPENROUTER_API_KEY


def get_query_enhanced(query: str):
    with OpenRouter(api_key=OPENROUTER_API_KEY) as client:
        response = client.chat.send(
            model="baidu/cobuddy:free",
            messages=[
                {
                    "role": "user",
                    "content": f"{SYSTEM_PROMPT}\n\nUser Question: {query}\nOptimized Retrieval Query:"
                }
            ],
        )

    print(response.choices[0].message.content)
    enhanced_query = response.choices[0].message.content
    return f"{ query } { enhanced_query}"




def final_ai_response(context: str, query: str):
    SYSTEM_PROMPT = """
You are an expert repository assistant.

Your task:
- Answer ONLY using the provided repository context.
- Be precise and technical.
- Mention file names and relevant functionality when possible.
- Do not hallucinate features, files, or APIs.
- If the answer is not clearly present in the context, say:
  "I could not find enough information in the repository context."

Guidelines:
- Prefer concise but complete answers.
- Explain where functionality is implemented.
- Mention important files and routes.
- For authentication/security questions, mention middleware, protected routes, JWT usage, etc.
- For frontend questions, mention components/pages/hooks involved.
- For backend questions, mention routes/services/middleware/models involved.
- If multiple files contribute to the feature, summarize their roles.

Response style:
- Clear
- Developer-focused
- Structured
- No unnecessary fluff
"""

    USER_PROMPT = f"""
# USER QUESTION
{query}

# REPOSITORY CONTEXT
{context}

# INSTRUCTIONS
Answer the user question strictly from the repository context.
"""

    with OpenRouter(api_key=OPENROUTER_API_KEY) as client:
        response = client.chat.send(
            model="openai/gpt-oss-120b:free",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": USER_PROMPT
                }
            ],
            temperature=0.2,
            max_tokens=500,
        )
    print(response.choices[0])
    return response.choices[0].message.content