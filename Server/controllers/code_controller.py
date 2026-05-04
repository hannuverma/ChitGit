from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
import os

LANGUAGE_MAP = {
    "python": Language.PYTHON,
    "js": Language.JS,
    "ts": Language.TS,
    "java": Language.JAVA,
    "cpp": Language.CPP,
    "c": Language.C,
    "csharp": Language.CSHARP,
    "go": Language.GO,
    "rust": Language.RUST,
    "ruby": Language.RUBY,
    "php": Language.PHP,
    "kotlin": Language.KOTLIN,
    "swift": Language.SWIFT,
    "scala": Language.SCALA,
    "lua": Language.LUA,
    "perl": Language.PERL,
    "haskell": Language.HASKELL,
    "elixir": Language.ELIXIR,
    "powershell": Language.POWERSHELL,
    "visualbasic6": Language.VISUALBASIC6,
    "html": Language.HTML,
    "markdown": Language.MARKDOWN,
    "rst": Language.RST,
    "latex": Language.LATEX,
    "proto": Language.PROTO,
    "sol": Language.SOL,
}

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "js",
    ".ts": "ts",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".kt": "kotlin",
    ".swift": "swift",
    ".scala": "scala",
    ".lua": "lua",
    ".pl": "perl",
    ".hs": "haskell",
    ".ex": "elixir",
    ".ps1": "powershell",
    ".vb": "visualbasic6",
    ".html": "html",
    ".md": "markdown",
    ".rst": "rst",
    ".tex": "latex",
    ".proto": "proto",
    ".sol": "sol"
}

class file_info:
    code: str
    path: str
    type: str
    size: int





def create_chunk(file_info):
    Code = file_info.get('code')

    # 🔴 Fix 1: Handle None properly
    if not Code:
        print(f"Skipping {file_info['path']} (no code)")
        return []

    # 🔴 Fix 2: Small file → skip splitting
    if len(Code) < 300:
        print(f"Skipping chunking for small file: {file_info['path']}")
        return [Code]

    # 🔴 Fix 3: Correct extension
    ext = os.path.splitext(file_info['path'])[1]  # ".py"

    # 🔴 Fix 4: Correct language lookup
    language = EXTENSION_TO_LANGUAGE.get(ext)

    print(f"Detected language: {language} for file: {file_info['path']}")

    # 🔴 Fix 5: Safe fallback
    if language and language in LANGUAGE_MAP:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=LANGUAGE_MAP[language],
            chunk_size=1500,
            chunk_overlap=150
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=150
        )

    # 🔴 Fix 6: Always pass valid string
    docs = splitter.create_documents([Code])

    chunks = [doc.page_content for doc in docs]

    # for i, chunk in enumerate(chunks):
    #     print(f"\n---- chunk {i} ----\n")
    #     print(chunk[:200])

    return chunks

def get_file_code(repo, path):
    try:
        file_obj = repo.get_contents(path)

        # ❌ Skip if no encoding (important fix)
        if file_obj.encoding is None:
            print(f"Skipping (no encoding): {path}")
            return None

        content = file_obj.decoded_content

        # ❌ Skip binary
        if b'\x00' in content:
            print(f"Skipping (binary): {path}")
            return None

        return content.decode("utf-8", errors="ignore")

    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

import re

def extract_function_names(chunk, language):
    functions = []

    if language == "js" or language == "ts" or language == "jsx" or language == "tsx":
        # Covers:
        # function myFunc()
        # const myFunc = () =>
        # const myFunc = function()
        # myFunc: function() {}
        
        patterns = [
            r"function\s+(\w+)\s*\(",                # function myFunc(
            r"(\w+)\s*=\s*\(?.*\)?\s*=>",           # myFunc = () =>
            r"(\w+)\s*=\s*function\s*\(",           # myFunc = function(
            r"(\w+)\s*:\s*function\s*\("            # myFunc: function(
        ]

        for pattern in patterns:
            matches = re.findall(pattern, chunk)
            functions.extend(matches)

    elif language == "python":
        # Covers:
        # def my_func(
        pattern = r"def\s+(\w+)\s*\("
        functions = re.findall(pattern, chunk)

    return list(set(functions))  # remove duplicates



def extract_ui_text(chunk):
    texts = []

    # 1. Text between tags >TEXT<
    matches = re.findall(r">([^<>]+)<", chunk)
    for m in matches:
        clean = m.strip()
        if clean:
            texts.append(clean)

    # 2. Option values (important for dropdowns)
    option_values = re.findall(r"value=['\"]([^'\"]+)['\"]", chunk)
    texts.extend(option_values)

    # 3. Placeholder / labels
    placeholders = re.findall(r"placeholder=['\"]([^'\"]+)['\"]", chunk)
    texts.extend(placeholders)

    # 4. Remove duplicates
    texts = list(set(texts))

    return " ".join(texts)
# create_chunk(file_info(path="example.py", type="file", size=2000))