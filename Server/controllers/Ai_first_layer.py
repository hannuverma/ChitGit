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
    return response.choices[0].message.content
