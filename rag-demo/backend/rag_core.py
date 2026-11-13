# -*- coding: utf-8 -*-
"""最小可用的党建知识库 RAG 核心：切块、向量化、检索、重排、带引用回答。"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import threading
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Any

import httpx
import numpy as np

import config as cfg

log = logging.getLogger("rag")

_LOCK = threading.RLock()
_INDEX: dict[str, Any] | None = None
_SESSIONS: dict[str, list[dict[str, str]]] = {}

ALLOWED_SUFFIXES = {".txt", ".md", ".docx", ".pdf"}

CHAPTER_RE = re.compile(r"^第[一二三四五六七八九十百]+[章编]\s*\S.{0,30}$")
CN_HEADING_RE = re.compile(r"^[一二三四五六七八九十]+、(.{2,30})$")


def _is_heading(line: str) -> bool:
    """只把章标题和「一、」级标题当章节。

    党章中的「（一）认真学习…」「（八）向党的上级组织…」是条文条目，
    不是章节标题，不能在这里切段，否则会把党员义务/权利切碎。
    """
    s = line.strip()
    if CHAPTER_RE.match(s) and "。" not in s:
        return True
    match = CN_HEADING_RE.match(s)
    if match and not re.search(r"[，；。：]", match.group(1).rstrip("。")):
        return True
    return False


def _is_outline_line(line: str) -> bool:
    """用于文档阅读器的大纲：比切块判定更宽松。

    二十大报告的一级标题含逗号（如「四、加快构建新发展格局，着力推动
    高质量发展」），切块时保守跳过，但作为阅读大纲应当展示。
    """
    s = line.strip()
    if not s or "。" in s:
        return False
    return bool(CHAPTER_RE.match(s) or CN_HEADING_RE.match(s))

SMALLTALK = {"你好", "您好", "在吗", "你是谁", "介绍一下你自己", "谢谢", "感谢", "hello", "hi"}


# --------------------------------------------------------------------------
# 本地兜底向量：字符 n-gram 哈希。没有 API Key 时也能跑通检索闭环。
# --------------------------------------------------------------------------
def _clean_for_ngram(text: str) -> str:
    return re.sub(r"[^一-鿿a-zA-Z0-9]", "", text).lower()


def local_embed(texts: list[str], dim: int | None = None) -> np.ndarray:
    dim = dim or cfg.LOCAL_EMBED_DIM
    out = np.zeros((len(texts), dim), dtype=np.float32)
    for row, text in enumerate(texts):
        s = _clean_for_ngram(text)
        grams: list[str] = []
        for n in (2, 3, 4):
            grams.extend(s[i:i + n] for i in range(max(0, len(s) - n + 1)))
        grams.extend(re.findall(r"[a-z0-9]{2,}", s))
        for gram in grams:
            digest = hashlib.md5(gram.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "little") % dim
            sign = 1.0 if digest[4] & 1 else -1.0
            out[row, idx] += sign
    norms = np.linalg.norm(out, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return out / norms


def _current_backend() -> str:
    return f"api:{cfg.EMBED_MODEL}" if cfg.EMBED_API_KEY else "local-hash"


def _api_embed(texts: list[str], batch_size: int = 16) -> np.ndarray:
    if not cfg.EMBED_API_KEY:
        raise RuntimeError("未配置 EMBED_API_KEY / LLM_API_KEY，无法调用向量模型")
    headers = {
        "Authorization": f"Bearer {cfg.EMBED_API_KEY}",
        "Content-Type": "application/json",
    }
    vectors: list[list[float]] = []
    with httpx.Client(timeout=90.0) as client:
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            payload = {"model": cfg.EMBED_MODEL, "input": batch}
            last_err: Exception | None = None
            for attempt in range(3):
                try:
                    resp = client.post(
                        f"{cfg.EMBED_BASE_URL}/embeddings", json=payload, headers=headers
                    )
                    resp.raise_for_status()
                    data = resp.json()["data"]
                    data = sorted(data, key=lambda item: item.get("index", 0))
                    vectors.extend(item["embedding"] for item in data)
                    last_err = None
                    break
                except Exception as exc:  # noqa: BLE001 - 需要把供应商错误原样带给前端
                    last_err = exc
                    if attempt < 2:
                        time.sleep(1.5 * (attempt + 1))
            if last_err is not None:
                raise RuntimeError(f"向量模型调用失败：{last_err}") from last_err
    arr = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms


def embed_texts(texts: list[str], backend: str | None = None) -> np.ndarray:
    backend = backend or _current_backend()
    if backend.startswith("api:"):
        return _api_embed(texts)
    return local_embed(texts)


# --------------------------------------------------------------------------
# 文档解析与切块
# --------------------------------------------------------------------------
def read_text_file(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def parse_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return read_text_file(path)
    if suffix == ".docx":
        from docx import Document  # 延迟导入，未上传 docx 时不影响启动

        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    raise ValueError(f"不支持的文件类型：{path.suffix}（支持 .txt/.md/.docx/.pdf）")


def _document_title(text: str, fallback: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return fallback
    return lines[0][:120]


def _split_long(paragraph: str, size: int) -> list[str]:
    if len(paragraph) <= size:
        return [paragraph]
    pieces, buf = [], ""
    for sent in re.split(r"(?<=[。！？；])", paragraph):
        if len(buf) + len(sent) <= size:
            buf += sent
        else:
            if buf:
                pieces.append(buf)
            buf = sent
    if buf:
        pieces.append(buf)
    return pieces


def chunk_document(text: str, title: str, doc_id: str) -> list[dict[str, Any]]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines and lines[0] == title.split("（")[0].strip():
        lines = lines[1:]
    if lines and lines[0][:1] in ("（", "—"):
        lines = lines[1:]

    chunks: list[dict[str, Any]] = []
    section = title
    buf: list[str] = []
    buf_len = 0
    chunk_index = 0
    list_mode = False

    def flush() -> None:
        nonlocal buf, buf_len, chunk_index
        body = "\n".join(buf).strip()
        if not body or (chunks and len(body) <= cfg.CHUNK_OVERLAP):
            buf, buf_len = [], 0
            return
        chunks.append({
            "id": f"{doc_id}-{chunk_index:04d}",
            "doc_id": doc_id,
            "title": title,
            "section": section,
            "text": body,
            "chunk_index": chunk_index,
        })
        chunk_index += 1
        tail = body[-cfg.CHUNK_OVERLAP:] if cfg.CHUNK_OVERLAP > 0 else ""
        buf = [tail] if tail else []
        buf_len = len(tail)

    for line in lines:
        heading = line if _is_heading(line) else None
        if heading:
            flush()
            buf, buf_len = [], 0
            section = heading
            list_mode = False
            continue

        # 新的「第X条」开始，结束上一条的列举模式
        is_new_article = bool(re.match(r"^第[一二三四五六七八九十百]+条", line))
        if is_new_article and list_mode:
            flush()
            list_mode = False

        for para in _split_long(line, cfg.CHUNK_SIZE):
            # 「……下列义务：」这类引导句要和后面的分项留在同一片段里，
            # 否则检索到「义务」时只拿到一句空标题。
            limit = cfg.CHUNK_SIZE * 3 if list_mode else cfg.CHUNK_SIZE
            if buf_len + len(para) + 1 > limit and buf:
                flush()
            buf.append(para)
            buf_len += len(para) + 1
            if para.rstrip().endswith(("：", ":")) or re.search(r"(如下|下列)[：:]?$", para):
                list_mode = True
    flush()
    return chunks


def discover_documents() -> list[Path]:
    files: list[Path] = []
    for folder in (cfg.CORPUS_DIR, cfg.UPLOAD_DIR):
        if not folder.exists():
            continue
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix.lower() in ALLOWED_SUFFIXES:
                files.append(path)
    return files


def _doc_id_for(path: Path) -> str:
    try:
        rel = path.relative_to(cfg.CORPUS_DIR).as_posix()
    except ValueError:
        rel = path.name
    return hashlib.sha1(rel.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------
# 索引读写
# --------------------------------------------------------------------------
def _save_index(index: dict[str, Any]) -> None:
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = cfg.INDEX_PATH.with_suffix(".tmp")
    # _matrix 是运行时缓存，不能写进 JSON
    payload = {k: v for k, v in index.items() if not k.startswith("_")}
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    os.replace(tmp, cfg.INDEX_PATH)


def _load_index() -> dict[str, Any]:
    with open(cfg.INDEX_PATH, encoding="utf-8") as fh:
        index = json.load(fh)
    index.setdefault("documents", {})
    index.setdefault("chunks", [])
    _attach_matrix(index)
    return index


def _attach_matrix(index: dict[str, Any]) -> None:
    vectors = [c["vector"] for c in index["chunks"] if c.get("vector")]
    if vectors:
        mat = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        index["_matrix"] = mat / norms
    else:
        index["_matrix"] = np.zeros((0, cfg.LOCAL_EMBED_DIM), dtype=np.float32)


def build_index(force: bool = True) -> dict[str, Any]:
    global _INDEX
    with _LOCK:
        files = discover_documents()
        backend = _current_backend()
        chunks: list[dict[str, Any]] = []
        documents: dict[str, Any] = {}

        for path in files:
            try:
                text = parse_document(path)
            except Exception as exc:  # noqa: BLE001
                log.warning("跳过 %s：%s", path.name, exc)
                continue
            if not text.strip():
                continue
            doc_id = _doc_id_for(path)
            title = _document_title(text, path.stem)
            doc_chunks = chunk_document(text, title, doc_id)
            if not doc_chunks:
                continue
            chunks.extend(doc_chunks)
            documents[doc_id] = {
                "filename": path.name,
                "title": title,
                "chars": len(text),
                "chunks": len(doc_chunks),
                "uploaded": path.parent == cfg.UPLOAD_DIR,
            }

        vectors = (
            embed_texts([
                f"《{c['title']}》\n{c['section']}\n{c['text']}" for c in chunks
            ], backend=backend)
            if chunks else np.zeros((0, cfg.LOCAL_EMBED_DIM), dtype=np.float32)
        )
        for chunk, vector in zip(chunks, vectors):
            chunk["vector"] = [round(float(x), 6) for x in vector]

        index = {
            "version": 1,
            "embedding_backend": backend,
            "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "documents": documents,
            "chunks": chunks,
        }
        _save_index(index)
        _attach_matrix(index)
        _INDEX = index
        log.info("索引构建完成：%s 篇文档，%s 个片段，向量后端 %s",
                 len(documents), len(chunks), backend)
        return index


def ensure_index() -> dict[str, Any]:
    global _INDEX
    with _LOCK:
        if _INDEX is not None:
            return _INDEX
        if cfg.INDEX_PATH.exists():
            try:
                loaded = _load_index()
                current = _current_backend()
                stored = loaded.get("embedding_backend")
                # 用户刚填入 API Key 时，旧索引是本地哈希向量，自动重建为语义向量
                if stored != current and not (
                    str(stored).startswith("api:") and not cfg.EMBED_API_KEY
                ):
                    log.info("向量后端由 %s 变为 %s，自动重建索引", stored, current)
                    return build_index(force=True)
                _INDEX = loaded
                return _INDEX
            except Exception as exc:  # noqa: BLE001
                log.warning("索引读取失败，将重建：%s", exc)
        return build_index(force=True)


def index_stats() -> dict[str, Any]:
    index = ensure_index()
    return {
        "documents": len(index.get("documents", {})),
        "chunks": len(index.get("chunks", [])),
        "embedding_backend": index.get("embedding_backend", "unknown"),
        "built_at": index.get("built_at"),
        "llm_configured": bool(cfg.LLM_API_KEY),
        "llm_model": cfg.LLM_MODEL,
        "rerank_model": cfg.RERANK_MODEL or None,
    }


def list_files() -> list[dict[str, Any]]:
    index = ensure_index()
    return sorted(
        ({"doc_id": doc_id, **meta} for doc_id, meta in index["documents"].items()),
        key=lambda item: item["filename"],
    )


def _source_meta(filename: str) -> dict[str, str] | None:
    """来源信息由 scripts/fetch_corpus.py 写入 corpus/sources.json。"""
    path = cfg.CORPUS_DIR / "sources.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    item = data.get(filename)
    return item if isinstance(item, dict) else None


def get_document(doc_id: str) -> dict[str, Any]:
    """返回一篇知识库文档的正文、章节大纲与来源信息。"""
    index = ensure_index()
    meta = index.get("documents", {}).get(doc_id)
    if not meta:
        raise ValueError("文档不存在")

    path = next((p for p in discover_documents() if _doc_id_for(p) == doc_id), None)
    if path is None:
        raise ValueError("文档文件已不存在，请重建索引")

    text = parse_document(path)
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    outline = [
        {"title": line.strip(), "line": i}
        for i, line in enumerate(lines)
        if line.strip() and _is_outline_line(line.strip())
    ]
    return {
        "doc_id": doc_id,
        **meta,
        "content": text,
        "outline": outline,
        "source": _source_meta(meta["filename"]),
    }


# --------------------------------------------------------------------------
# 检索
# --------------------------------------------------------------------------
def _ngrams(text: str) -> set[str]:
    s = _clean_for_ngram(text)
    grams = {s[i:i + n] for n in (2, 3) for i in range(max(0, len(s) - n + 1))}
    grams.update(re.findall(r"[a-z0-9]{2,}", s))
    return {g for g in grams if g.strip()}


def _keyword_score(query_grams: set[str], text: str) -> float:
    if not query_grams:
        return 0.0
    text_grams = _ngrams(text)
    return len(query_grams & text_grams) / len(query_grams)


def _tokenize(text: str) -> list[str]:
    s = _clean_for_ngram(text)
    tokens = [s[i:i + 2] for i in range(max(0, len(s) - 1))]
    tokens.extend(re.findall(r"[a-z0-9]{2,}", s))
    return tokens


def _bm25_scores(question: str, chunks: list[dict[str, Any]]) -> np.ndarray:
    """字符二元组 BM25，补足向量检索对「三会一课」这类精确术语的召回。"""
    q_terms = set(_tokenize(question))
    if not q_terms or not chunks:
        return np.zeros(len(chunks), dtype=np.float32)

    k1, b = 1.5, 0.75
    tfs: list[Counter[str]] = []
    df: Counter[str] = Counter()
    for chunk in chunks:
        tf = Counter(_tokenize(chunk["text"]))
        tfs.append(tf)
        df.update(tf.keys())

    n = len(chunks)
    avgdl = sum(sum(tf.values()) for tf in tfs) / max(1, n)
    idf = {
        term: math.log(1 + (n - df.get(term, 0) + 0.5) / (df.get(term, 0) + 0.5))
        for term in q_terms
    }

    scores = np.zeros(n, dtype=np.float32)
    for i, tf in enumerate(tfs):
        dl = sum(tf.values()) or 1
        for term in q_terms:
            freq = tf.get(term, 0)
            if freq:
                scores[i] += idf[term] * freq * (k1 + 1) / (
                    freq + k1 * (1 - b + b * dl / avgdl)
                )
    return scores


def _rerank(query: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not cfg.RERANK_MODEL or not candidates:
        return candidates
    payload = {
        "model": cfg.RERANK_MODEL,
        "query": query,
        "documents": [c["text"] for c in candidates],
        "top_n": len(candidates),
    }
    headers = {
        "Authorization": f"Bearer {cfg.RERANK_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{cfg.RERANK_BASE_URL}/rerank", json=payload, headers=headers
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
        if not results:
            return candidates
        reranked = []
        for item in results:
            cand = candidates[int(item["index"])]
            cand["rerank_score"] = float(item.get("relevance_score", 0.0))
            reranked.append(cand)
        reranked.sort(key=lambda c: c.get("rerank_score", 0.0), reverse=True)
        return reranked
    except Exception as exc:  # noqa: BLE001 - 重排失败不应阻断问答
        log.warning("重排调用失败，退回向量排序：%s", exc)
        return candidates


def retrieve(question: str, top_k: int | None = None) -> list[dict[str, Any]]:
    index = ensure_index()
    chunks = index["chunks"]
    if not chunks:
        return []

    backend = index.get("embedding_backend", _current_backend())
    qvec = embed_texts([question], backend=backend)[0]
    cosines = index["_matrix"] @ qvec

    bm25 = _bm25_scores(question, chunks)
    bm25_norm = bm25 / bm25.max() if bm25.size and bm25.max() > 0 else bm25
    # 向量为主、BM25 为辅；本地兜底向量质量较弱时 BM25 能兜住精确术语
    scores = 0.7 * cosines + 0.3 * bm25_norm
    order = np.argsort(-scores)[: cfg.CANDIDATE_K]

    candidates = []
    for i in order:
        chunk = chunks[int(i)]
        candidates.append({
            "id": chunk["id"],
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "section": chunk["section"],
            "text": chunk["text"],
            "score": round(float(scores[int(i)]), 4),
            "confidence": round(float(cosines[int(i)]), 4),
            "bm25": round(float(bm25[int(i)]), 4),
        })

    candidates = _rerank(question, candidates)
    return candidates[: (top_k or cfg.TOP_K)]


def _is_smalltalk(question: str) -> bool:
    q = re.sub(r"[\s，。！？!?、]", "", question).lower()
    return q in SMALLTALK or len(q) <= 2


def _snippet(text: str, limit: int = 260, query: str = "") -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    if query:
        q = re.sub(r"\s+", "", query)
        best_key: tuple[int, int] | None = None
        pos = -1
        # 取能命中的最长片段；同长度时优先在原文中出现次数少的词，避免“党员”这类泛词
        for n in range(6, 1, -1):
            found_any = False
            for i in range(len(q) - n + 1):
                gram = q[i:i + n]
                found = text.find(gram)
                if found == -1:
                    continue
                found_any = True
                key = (n, -text.count(gram))
                if best_key is None or key > best_key:
                    best_key = key
                    pos = found
            if found_any:
                break
        if pos != -1:
            start = max(0, pos - limit // 4)
            end = min(len(text), start + limit)
            start = max(0, end - limit)
            return (
                ("…" if start > 0 else "")
                + text[start:end]
                + ("…" if end < len(text) else "")
            )
    return text[:limit] + "…"


def _build_prompt(question: str, sources: list[dict[str, Any]]) -> list[dict[str, str]]:
    blocks = []
    for i, src in enumerate(sources, 1):
        blocks.append(f"【资料{i}】《{src['title']}》·{src['section']}\n{src['text']}")
    material = "\n\n".join(blocks)
    system = (
        "你是“智慧党建”知识库问答助手，服务对象是党员和党务工作者。\n"
        "你必须严格依据【参考资料】回答问题，不得使用资料之外的知识，不得编造条文、数字或出处。\n"
        "要求：\n"
        "1. 先给出直接、准确的回答；需要分点时使用“1. 2. 3.”。\n"
        "2. 每个关键结论后用 [编号] 标注依据，例如 [1]、[2]，编号必须来自参考资料。\n"
        "3. 如果参考资料不足以回答，明确说明“现有资料未涵盖该问题”，并建议补充哪类文件，不要猜测。\n"
        "4. 语言规范、简洁，避免空话套话；不要重复问题，不要写“根据资料”四个字。\n\n"
        f"【参考资料】\n{material}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]


def _chat(messages: list[dict[str, str]]) -> str:
    if not cfg.LLM_API_KEY:
        raise RuntimeError("未配置 LLM_API_KEY")
    headers = {
        "Authorization": f"Bearer {cfg.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": cfg.LLM_MODEL,
        "messages": messages,
        "temperature": cfg.LLM_TEMPERATURE,
        "max_tokens": cfg.LLM_MAX_TOKENS,
        "stream": False,
    }
    if cfg.LLM_THINKING in ("enabled", "disabled"):
        payload["thinking"] = {"type": cfg.LLM_THINKING}

    last_err: Exception | None = None
    data: dict[str, Any] = {}
    with httpx.Client(timeout=120.0) as client:
        for attempt in range(3):
            try:
                resp = client.post(
                    f"{cfg.LLM_BASE_URL}/chat/completions", json=payload, headers=headers
                )
                resp.raise_for_status()
                data = resp.json()
                last_err = None
                break
            except Exception as exc:  # noqa: BLE001 - 网络抖动重试
                last_err = exc
                if attempt < 2:
                    time.sleep(2.0 * (attempt + 1))
    if last_err is not None:
        raise last_err

    choice = data["choices"][0]
    content = (choice["message"].get("content") or "").strip()
    if not content:
        reason = choice.get("finish_reason")
        if reason == "length":
            raise RuntimeError(
                "模型输出被 max_tokens 截断（思考 token 占满了配额），"
                "可调大 LLM_MAX_TOKENS 或设置 LLM_THINKING=disabled"
            )
        raise RuntimeError(f"模型返回空内容（finish_reason={reason}）")
    return content


def _fallback_answer(question: str, sources: list[dict[str, Any]], reason: str) -> str:
    lines = [
        f"（{reason}，当前为检索预览模式）",
        "",
        f"针对“{question}”，知识库中相关度最高的依据如下：",
    ]
    for i, src in enumerate(sources, 1):
        lines.append(
            f"{i}. 《{src['title']}》·{src['section']}：{_snippet(src['text'], 160, question)}"
        )
    lines += ["", "在 backend/.env 中配置 LLM_API_KEY 后，系统会把以上依据交给大模型生成带引用的回答。"]
    return "\n".join(lines)


def _public_sources(
    sources: list[dict[str, Any]], limit: int = 180, query: str = ""
) -> list[dict[str, Any]]:
    return [
        {
            "index": i,
            "doc_id": src["doc_id"],
            "title": src["title"],
            "section": src["section"],
            "snippet": _snippet(src["text"], limit, query),
            "text": src["text"][:1200],
            "score": src.get("rerank_score", src.get("score", 0.0)),
            "confidence": src.get("confidence", 0.0),
        }
        for i, src in enumerate(sources, 1)
    ]


def answer(question: str, session_id: str) -> dict[str, Any]:
    question = question.strip()
    if not question:
        raise ValueError("问题不能为空")

    if _is_smalltalk(question):
        return {
            "answer": "你好，我是智慧党建知识库助手。你可以问我党章条文、党支部工作、党员义务与权利、二十大报告等问题，我会给出答案并标注依据出处。",
            "sources": [],
            "refused": False,
            "degraded": False,
        }

    sources = retrieve(question)
    backend = ensure_index().get("embedding_backend", "local-hash")
    min_cosine = cfg.MIN_SCORE if str(backend).startswith("api:") else 0.10
    min_bm25 = 8.0
    best_semantic = max((s["confidence"] for s in sources), default=0.0)
    best_lexical = max((s.get("bm25", 0.0) for s in sources), default=0.0)

    if not sources or (best_semantic < min_cosine and best_lexical < min_bm25):
        return {
            "answer": "现有资料未涵盖该问题。请尝试换一种问法，或上传相关制度文件后再试。",
            "sources": [],
            "refused": True,
            "degraded": False,
        }

    public_sources = _public_sources(sources, query=question)
    if not cfg.LLM_API_KEY:
        return {
            "answer": _fallback_answer(question, sources, "未配置大模型 API Key"),
            "sources": public_sources,
            "refused": False,
            "degraded": True,
        }

    messages = _build_prompt(question, sources)
    history = _SESSIONS.get(session_id, [])
    if history:
        messages = [messages[0], *history[-cfg.HISTORY_TURNS * 2:], messages[1]]
    try:
        reply = _chat(messages)
        degraded = False
    except Exception as exc:  # noqa: BLE001
        log.warning("大模型调用失败：%s", exc)
        reply = _fallback_answer(question, sources, f"大模型调用失败：{exc}")
        degraded = True

    if not reply:
        reply = "大模型未返回有效内容，请稍后重试。"
        degraded = True

    _SESSIONS.setdefault(session_id, []).extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": reply},
    ])
    if len(_SESSIONS[session_id]) > cfg.HISTORY_TURNS * 6:
        _SESSIONS[session_id] = _SESSIONS[session_id][-cfg.HISTORY_TURNS * 6:]

    return {
        "answer": reply,
        "sources": public_sources,
        "refused": False,
        "degraded": degraded,
    }


# --------------------------------------------------------------------------
# 上传增量入库
# --------------------------------------------------------------------------
def safe_filename(name: str) -> str:
    name = Path(name or "upload.txt").name
    name = re.sub(r"[^\w一-鿿.\-（）() ]", "_", name)
    return name[:120] or f"upload-{uuid.uuid4().hex[:8]}.txt"


def ingest_upload(filename: str, content: bytes) -> dict[str, Any]:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError(f"不支持的文件类型：{suffix or '未知'}（支持 .txt/.md/.docx/.pdf）")
    if len(content) > 15 * 1024 * 1024:
        raise ValueError("文件超过 15MB，请拆分后再上传")

    cfg.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = cfg.UPLOAD_DIR / safe_filename(filename)
    path.write_bytes(content)

    text = parse_document(path)
    if not text.strip():
        path.unlink(missing_ok=True)
        raise ValueError("未能从文件中解析出文本")

    with _LOCK:
        index = ensure_index()
        backend = index.get("embedding_backend", _current_backend())
        doc_id = _doc_id_for(path)
        title = _document_title(text, path.stem)
        new_chunks = chunk_document(text, title, doc_id)
        if not new_chunks:
            raise ValueError("文件内容过短，未能切分出有效片段")

        vectors = embed_texts(
            [f"《{c['title']}》\n{c['section']}\n{c['text']}" for c in new_chunks],
            backend=backend,
        )
        for chunk, vector in zip(new_chunks, vectors):
            chunk["vector"] = [round(float(x), 6) for x in vector]

        index["chunks"] = [c for c in index["chunks"] if c["doc_id"] != doc_id]
        index["chunks"].extend(new_chunks)
        index["documents"][doc_id] = {
            "filename": path.name,
            "title": title,
            "chars": len(text),
            "chunks": len(new_chunks),
            "uploaded": True,
        }
        index["built_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        _save_index(index)
        _attach_matrix(index)
        return {
            "filename": path.name,
            "title": title,
            "chunks": len(new_chunks),
            "chars": len(text),
            "documents": len(index["documents"]),
            "total_chunks": len(index["chunks"]),
        }
