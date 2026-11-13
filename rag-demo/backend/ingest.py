# -*- coding: utf-8 -*-
"""重建知识库索引：python ingest.py"""
import json

import rag_core


if __name__ == "__main__":
    index = rag_core.build_index(force=True)
    summary = {
        "documents": len(index["documents"]),
        "chunks": len(index["chunks"]),
        "embedding_backend": index["embedding_backend"],
        "files": [
            {"filename": meta["filename"], "chunks": meta["chunks"], "chars": meta["chars"]}
            for meta in index["documents"].values()
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
