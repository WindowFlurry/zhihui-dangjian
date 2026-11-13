# -*- coding: utf-8 -*-
"""智慧党建 RAG Demo 后端（FastAPI）。

启动：python -m uvicorn app:app --reload --port 8000
"""
from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config as cfg
import rag_core as rag

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("app")

app = FastAPI(title="智慧党建 RAG Demo", version="0.1.0")

# Demo 阶段允许本地前端直接跨域访问；生产环境请收紧 allow_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


@app.get("/")
def root():
    return {
        "service": "智慧党建 RAG Demo",
        "docs": "/docs",
        "ask": "POST /knowledge/ask",
    }


@app.get("/health")
def health():
    try:
        stats = rag.index_stats()
        return {"status": "ok", **stats}
    except Exception as exc:  # noqa: BLE001
        log.exception("健康检查失败")
        return {
            "status": "error",
            "error": str(exc),
            "llm_configured": bool(cfg.LLM_API_KEY),
            "documents": 0,
            "chunks": 0,
        }


@app.post("/knowledge/ask")
def ask(req: AskRequest):
    session_id = req.session_id or uuid.uuid4().hex
    try:
        result = rag.answer(req.question, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        log.exception("问答失败")
        raise HTTPException(status_code=502, detail=f"问答服务异常：{exc}") from exc
    return {"success": True, "session_id": session_id, **result}


@app.get("/knowledge/files")
def files():
    try:
        items = rag.list_files()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"读取知识库失败：{exc}") from exc
    return {"success": True, "files": items, "count": len(items)}


@app.get("/knowledge/documents/{doc_id}")
def document_detail(doc_id: str):
    try:
        doc = rag.get_document(doc_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        log.exception("读取文档失败")
        raise HTTPException(status_code=500, detail=f"读取文档失败：{exc}") from exc
    return {"success": True, **doc}


@app.post("/knowledge/upload")
def upload(file: UploadFile = File(...)):
    content = file.file.read()
    try:
        result = rag.ingest_upload(file.filename or "upload.txt", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        log.exception("上传入库失败")
        raise HTTPException(status_code=500, detail=f"上传入库失败：{exc}") from exc
    return {
        "success": True,
        "message": f"已入库 {result['chunks']} 个片段",
        **result,
    }


@app.post("/knowledge/rebuild")
def rebuild():
    try:
        index = rag.build_index(force=True)
    except Exception as exc:  # noqa: BLE001
        log.exception("重建索引失败")
        raise HTTPException(status_code=500, detail=f"重建索引失败：{exc}") from exc
    return {
        "success": True,
        "documents": len(index["documents"]),
        "chunks": len(index["chunks"]),
        "embedding_backend": index["embedding_backend"],
    }


@app.get("/knowledge/debug/retrieve")
def debug_retrieve(q: str, top_k: int = 5):
    """调试用：只检索、不调用大模型，便于核对召回质量。"""
    try:
        hits = rag.retrieve(q, top_k=top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {
        "success": True,
        "query": q,
        "hits": [
            {
                "title": h["title"],
                "section": h["section"],
                "score": h["score"],
                "confidence": h["confidence"],
                "snippet": rag._snippet(h["text"], 200, q),  # noqa: SLF001
            }
            for h in hits
        ],
    }
