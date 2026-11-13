# -*- coding: utf-8 -*-
"""RAG demo configuration. All values can be overridden in backend/.env."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# 优先读取 backend/.env；不存在时使用下面的默认值（默认走硅基流动）
load_dotenv(BASE_DIR / ".env", encoding="utf-8")

CORPUS_DIR = BASE_DIR / "corpus"
UPLOAD_DIR = CORPUS_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
INDEX_PATH = DATA_DIR / "index.json"

# ---- 对话模型（OpenAI 兼容接口）----
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct").strip()
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "900"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
# 仅 DeepSeek Flash/V4 系列使用：enabled / disabled，留空则不发送该参数
LLM_THINKING = os.getenv("LLM_THINKING", "").strip().lower()

# ---- 向量模型（可与对话模型不同供应商）----
# EMBED_MODE=api    调用 /embeddings（默认，复用 LLM 的 Key 和 Base URL）
# EMBED_MODE=local  使用本地字符 n-gram 哈希向量，不调用任何接口
# 留空则自动判断：DeepSeek 官方接口没有 /embeddings，会自动退回 local
EMBED_MODE = os.getenv("EMBED_MODE", "").strip().lower()
_embed_api_key = os.getenv("EMBED_API_KEY", "").strip()
_embed_base_url = os.getenv("EMBED_BASE_URL", "").strip()

if EMBED_MODE == "local":
    EMBED_API_KEY = ""
elif _embed_api_key:
    EMBED_API_KEY = _embed_api_key
elif EMBED_MODE == "api" or _embed_base_url:
    EMBED_API_KEY = LLM_API_KEY
elif "api.deepseek.com" in LLM_BASE_URL:
    EMBED_API_KEY = ""  # DeepSeek 不提供向量接口
else:
    EMBED_API_KEY = LLM_API_KEY

EMBED_BASE_URL = (_embed_base_url or LLM_BASE_URL).rstrip("/")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3").strip()

# ---- 可选：检索重排（留空则跳过）----
RERANK_MODEL = os.getenv("RERANK_MODEL", "").strip()
RERANK_BASE_URL = (os.getenv("RERANK_BASE_URL", "").strip() or EMBED_BASE_URL).rstrip("/")
RERANK_API_KEY = os.getenv("RERANK_API_KEY", "").strip() or EMBED_API_KEY

# ---- 检索参数 ----
TOP_K = int(os.getenv("TOP_K", "5"))
CANDIDATE_K = int(os.getenv("CANDIDATE_K", "20"))
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.40"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "480"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "80"))
LOCAL_EMBED_DIM = int(os.getenv("LOCAL_EMBED_DIM", "1024"))
HISTORY_TURNS = int(os.getenv("HISTORY_TURNS", "3"))

# ---- 服务 ----
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
