# 智慧党建 RAG Demo

一个晚上可跑通的党建知识库问答 Demo：**本地党建语料 + 向量检索 + BM25 混合召回 + 大模型带引用回答 + 现有 Vue 对话页**。

- 语料：11 篇公开权威文本（党章、党的二十大报告、支部工作条例、纪律处分条例、党内监督条例、问责条例、组织工作条例、党员教育管理条例、发展党员工作细则、党内政治生活准则、党徽党旗条例），共约 14 万字，切成约 408 个片段
- 检索：OpenAI 兼容向量模型（bge-m3 / qwen3.7-text-embedding 等）+ 字符二元组 BM25，可选重排
- 回答：严格基于检索片段，输出 `[1] [2]` 引用编号，前端展示原文出处
- 浏览：右侧“知识库文档”列出全部文档，点击可看全文与章节大纲；回答的引用卡片也能直接跳到对应章节
- 拒答：相关度不足时明确回答“现有资料未涵盖”，不硬编
- 兜底：没有 API Key 也能启动，进入“检索预览模式”，界面和引用照常演示

## 目录

```
rag-demo/
├─ backend/
│  ├─ app.py            FastAPI 接口
│  ├─ rag_core.py       切块、向量、BM25、检索、重排、回答
│  ├─ ingest.py         重建索引 CLI
│  ├─ config.py         读取 .env
│  ├─ corpus/           11 篇党建原文 + sources.json（来源 URL / 发布方）
│  ├─ data/index.json   生成的索引（不提交 Git）
│  ├─ .env              本地 Key 配置（不提交 Git）
│  └─ requirements.txt
├─ scripts/
│  └─ fetch_corpus.py   下载并抽取 11 篇公开文献（`--reuse` 可复用已存 HTML）
└─ start-demo.ps1       一键启动后端 + 前端
```

## 快速开始

### 1. 填 API Key

打开 `backend/.env`，填对话模型的 Key：

```ini
LLM_API_KEY=sk-你的Key
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
EMBED_MODEL=BAAI/bge-m3
```

> 默认按**硅基流动**配置。用其他厂商时按下表改 `LLM_*` / `EMBED_*` 四项。
> 如果对话模型和向量模型不是同一家，分别填 `LLM_API_KEY` 和 `EMBED_API_KEY`。

### 2. 安装依赖

```powershell
cd rag-demo\backend
pip install -r requirements.txt

cd ..\..\src-2\src-2
npm install
```

### 3. 建索引

```powershell
cd rag-demo\backend
python ingest.py
```

看到 `documents: 3, chunks: ~190` 即可。**修改 Key 或切换向量模型后需要重新执行一次**；不执行也可以，后端发现向量后端变化会自动重建。

### 4. 启动

```powershell
# 终端 A：后端
cd rag-demo\backend
python -m uvicorn app:app --host 127.0.0.1 --port 8000

# 终端 B：前端
cd src-2\src-2
npm run dev
```

浏览器打开 `http://localhost:5173/home`。

或者直接运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\rag-demo\start-demo.ps1
```

### 5. 验证

```powershell
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/knowledge/debug/retrieve?q=三会一课"
```

## 配置国内模型

`LLM_BASE_URL` / `EMBED_BASE_URL` 必须是 OpenAI 兼容接口（`/chat/completions`、`/embeddings`）。

| 供应商 | LLM_BASE_URL | LLM_MODEL | EMBED_MODEL |
|---|---|---|---|
| 硅基流动（默认） | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-7B-Instruct` | `BAAI/bge-m3` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-flash` | 不支持，见下 |
| 阿里百炼 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` | `text-embedding-v3` |
| 智谱 | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | `embedding-3` |
| 本地 Ollama | `http://127.0.0.1:11434/v1` | `qwen2.5:7b` | `bge-m3`（Key 随便填非空值） |

重排是可选项，默认关闭；硅基流动可填 `RERANK_MODEL=BAAI/bge-reranker-v2-m3`。

### 用 DeepSeek Flash 对话

DeepSeek 官方接口**没有 `/embeddings`**，所以向量模型必须单独解决。两种配法：

**A. DeepSeek 对话 + 千问AI平台向量（推荐，检索质量最好）**

```ini
LLM_API_KEY=sk-你的DeepSeekKey
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-flash
LLM_THINKING=disabled

EMBED_MODE=api
EMBED_API_KEY=sk-你的向量服务Key
EMBED_BASE_URL=https://maas.qianwenaiapi.com/compatible-mode/v1
EMBED_MODEL=qwen3.7-text-embedding
```

**B. DeepSeek 对话 + 本地向量（只需一个 Key）**

```ini
LLM_API_KEY=sk-你的DeepSeekKey
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-flash
LLM_THINKING=disabled

EMBED_MODE=local
```

`EMBED_MODE=local` 时切块和索引不调用任何外部接口，离线也能跑；代价是召回不如 bge-m3。
不改 `EMBED_MODE` 也可以：代码发现 Base URL 是 DeepSeek 时会自动退回 local。

> 换向量模型（`local` ↔ `bge-m3`）后需要重建索引，后端启动时会自动检测并重建，也可以手动跑 `python ingest.py`。

## 演示问题

- 党员的义务有哪些？
- 入党需要经过哪些程序？
- 党支部如何落实三会一课？
- 中国式现代化的本质要求是什么？
- 党的纪律处分有哪几种？
- 今天天气怎么样？（演示拒答）

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 文档数、片段数、向量后端、LLM 是否配置 |
| POST | `/knowledge/ask` | `{question, session_id?}` → `{answer, sources, session_id}` |
| GET | `/knowledge/files` | 已入库文档列表 |
| GET | `/knowledge/documents/{doc_id}` | 文档全文、章节大纲、来源 URL |
| POST | `/knowledge/upload` | 上传 `.txt/.md/.docx/.pdf`，增量入库 |
| POST | `/knowledge/rebuild` | 全量重建索引 |
| GET | `/knowledge/debug/retrieve?q=` | 只检索不生成，调召回用 |

`/knowledge/ask` 的响应与前端原有 `qa.js` 的期望结构一致，并额外返回 `refused`、`degraded`。

## 实现要点

1. **切块**：按章节/`一、`级标题维护来源；`第X条……下列义务：`这类引导句会与后续分项留在同一片段，避免检索到“义务”却只拿到半句标题。
2. **混合召回**：`0.7 × 向量余弦 + 0.3 × BM25`，兼顾语义问题和“三会一课”这类精确术语。
3. **拒答**：API 向量余弦低于 `MIN_SCORE` 且 BM25 低于 8 时直接拒答，避免模型拿无关片段硬答。
4. **引用**：提示词要求每个结论标注 `[编号]`，前端把编号、文档名、章节、原文片段一起渲染。
5. **会话**：后端内存保存最近 3 轮对话，支持“那第二点呢”这类追问；重启即清空。
6. **上传**：文件落到 `corpus/uploads/`，按文件名生成 `doc_id`，重复上传会替换旧片段。
7. **文档浏览**：`GET /knowledge/documents/{doc_id}` 直接读取原文并抽取章节标题；前端右侧面板列文档，抽屉展示全文，引用卡片按 `doc_id + section` 定位到对应章节。

## 更新语料

```bash
cd rag-demo
python scripts/fetch_corpus.py          # 重新下载并抽取
python scripts/fetch_corpus.py --reuse  # 复用 corpus/ 下已保存的 HTML
```

原始 HTML 保存在 `rag-demo/corpus/`，抽取后的文本写入 `backend/corpus/`，来源 URL 记录在 `backend/corpus/sources.json`。之后调用 `POST /knowledge/rebuild` 或重启后端即可重建索引。

## 已知限制

- Demo 级实现：索引是 JSON 文件，百万级语料需换 FAISS/Milvus/pgvector。
- 多轮会话存内存，重启丢失；没有用户隔离。
- CORS 允许所有来源，接口无鉴权，**不要直接部署到公网**。
- 上传解析只覆盖纯文本、Markdown、docx、PDF；扫描版 PDF 无 OCR。
- “检索预览模式”的答案由片段拼接，不是真正的自然语言回答；配 Key 后才是完整 RAG。

## 合规提示

- 语料均来自中国政府网、共产党员网、中央纪委国家监委网站、中国机构编制网等公开文本，见 `backend/corpus/` 与 `scripts/fetch_corpus.py`；每篇来源 URL 记录在 `backend/corpus/sources.json`。
- 党内文件、未公开材料不要上传到公网 Demo，也不要发给境外模型 API；生产环境建议使用通过备案的国内模型或本地部署模型。
- API Key 只放在 `backend/.env`，不要写进前端代码或提交到 Git。
