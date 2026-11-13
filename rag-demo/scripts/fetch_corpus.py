# -*- coding: utf-8 -*-
"""Fetch public party-building documents and turn them into plain text.

Usage (run from rag-demo/):
    python scripts/fetch_corpus.py

Raw HTML is archived under rag-demo/corpus/, extracted text goes to
backend/corpus/, and provenance is written to backend/corpus/sources.json.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "corpus"
OUT_DIR = ROOT / "backend" / "corpus"
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

JOBS = [
    {
        "slug": "jilvchufen_2023",
        "url": "https://www.scopsr.gov.cn/xwzx/szyw/202312/t20231228_388058.html",
        "out": "中国共产党纪律处分条例（2023年12月19日）.txt",
        "title": "中国共产党纪律处分条例\n（2023年12月19日中共中央发布）",
        "publisher": "中国机构编制网（转新华社）",
    },
    {
        "slug": "dangneijiandu_2016",
        "url": "https://news.12371.cn/2016/11/02/ARTI1478087905680175.shtml",
        "out": "中国共产党党内监督条例（2016年10月27日）.txt",
        "title": "中国共产党党内监督条例\n（2016年10月27日中国共产党第十八届中央委员会第六次全体会议通过）",
        "publisher": "共产党员网",
    },
    {
        "slug": "dangyuanjiaoyu_2019",
        "url": "https://www.ccdi.gov.cn/toutiao/201905/t20190521_194350.html",
        "out": "中国共产党党员教育管理工作条例（2019年5月）.txt",
        "title": "中国共产党党员教育管理工作条例\n（中共中央2019年5月印发）",
        "publisher": "中央纪委国家监委网站",
    },
    {
        "slug": "fazhandangyuan_2026",
        "url": "https://www.gov.cn/zhengce/202605/content_7069304.htm",
        "out": "中国共产党发展党员工作细则（2026年5月11日）.txt",
        "title": "中国共产党发展党员工作细则\n（2026年5月11日中共中央办公厅发布）",
        "publisher": "中国政府网",
    },
    {
        "slug": "wenze_2019",
        "url": "https://www.scopsr.gov.cn/xwzx/szyw/201909/t20190905_371421.html",
        "out": "中国共产党问责条例（2019年9月1日施行）.txt",
        "title": "中国共产党问责条例\n（2019年8月中共中央印发，自2019年9月1日起施行）",
        "publisher": "中国机构编制网（转新华社）",
    },
    {
        "slug": "zhengzhishenghuo_2016",
        "url": "https://www.ccdi.gov.cn/toutu/201611/t20161102_127892.html",
        "out": "关于新形势下党内政治生活的若干准则（2016年10月27日）.txt",
        "title": "关于新形势下党内政治生活的若干准则\n（2016年10月27日中国共产党第十八届中央委员会第六次全体会议通过）",
        "publisher": "中央纪委国家监委网站",
    },
    {
        "slug": "zuzhigongzuo_2021",
        "url": "https://www.12371.cn/2021/06/02/ARTI1622638294027912.shtml",
        "out": "中国共产党组织工作条例（2021年5月22日）.txt",
        "title": "中国共产党组织工作条例\n（2021年5月22日中共中央发布）",
        "publisher": "共产党员网",
    },
    {
        "slug": "danghuidangqi_2021",
        "url": "https://www.gov.cn/zhengce/2021-06/28/content_5621310.htm",
        "out": "中国共产党党徽党旗条例（2021年6月26日）.txt",
        "title": "中国共产党党徽党旗条例\n（2021年6月26日中共中央发布）",
        "publisher": "中国政府网",
    },
]

DROP_LINE_PATTERNS = [
    r"^发布时间\s*[:：]",
    r"^来源\s*[:：]",
    r"^分享",
    r"^扫一扫",
    r"^责任编辑\s*[:：]",
    r"^打印",
    r"^关闭$",
    r"^字号\s*[:：]?",
    r"^字体\s*[:：]?",
    r"^当前位置\s*[:：]?",
    r"^首页\s*>",
    r"^原标题\s*[:：]",
    r"^浏览次数\s*[:：]",
    r"^【?我要纠错】?$",
    r"^纠错$",
    r"^返回顶部$",
    r"^[【\[]?字号[】\]]?$",
    r"^[【\[]?打印[】\]]?$",
    r"^共产党员网$",
    r"^请先登录",
    r"^微信扫一扫",
    r"^收听本文$",
    r"^00:00/00:00$",
    r"^默认$",
    r"^大$",
    r"^超大$",
    r"^收藏$",
    r"^图表\s*[:：]",
]

TAIL_MARKERS = [
    "延伸阅读",
    "相关阅读",
    "相关链接",
    "相关新闻",
    "相关稿件",
    "上一篇",
    "下一篇",
    "返回列表",
    "网站地图",
    "版权声明",
    "主办单位",
    "扫一扫在手机打开当前页",
]

CONTAINER_SELECTORS = [
    "#font_area",
    "#UCAP-CONTENT",
    "#page_body",
    "#Zoom",
    "#content",
    ".TRS_Editor",
    ".article-content",
    ".article_content",
    ".content",
    ".article",
    "article",
]


def fetch(url: str) -> tuple[str, bytes]:
    last: Exception | None = None
    with httpx.Client(
        headers=HEADERS, follow_redirects=True, timeout=45.0, trust_env=True
    ) as client:
        for attempt in range(4):
            try:
                resp = client.get(url)
                resp.raise_for_status()
                return str(resp.url), resp.content
            except Exception as exc:  # noqa: BLE001
                last = exc
                time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"下载失败：{url}：{last}")


def decode(raw: bytes) -> str:
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def text_len(node) -> int:
    return len(re.findall(r"[一-鿿]", node.get_text(" ", strip=True)))


def extract_main(soup: BeautifulSoup):
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    # Prefer the first selector in priority order that holds enough body text.
    # Picking the *largest* block would grab outer wrappers that also contain
    # navigation, breadcrumbs and related-link panels.
    for selector in CONTAINER_SELECTORS:
        for node in soup.select(selector):
            if text_len(node) >= 500:
                return node

    # Fallback: largest text-bearing block, ignoring obvious page wrappers.
    best_node, best_len = None, 0
    for node in soup.find_all(["div", "section", "article", "td"]):
        length = text_len(node)
        if length > best_len:
            best_node, best_len = node, length
    return best_node


def clean(text: str) -> str:
    text = text.replace("　", " ").replace("\xa0", " ").replace("\r", "")
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw).strip()
        if not line:
            continue
        if any(re.match(pattern, line) for pattern in DROP_LINE_PATTERNS):
            continue
        lines.append(line)

    # Cut trailing related-link / site boilerplate.
    for i, line in enumerate(lines):
        if i < len(lines) * 0.6:
            continue
        if any(marker in line for marker in TAIL_MARKERS):
            lines = lines[:i]
            break
    return "\n".join(lines)


def main() -> int:
    reuse = "--reuse" in sys.argv[1:]
    sources: dict[str, dict[str, str]] = {}
    if (OUT_DIR / "sources.json").exists():
        sources = json.loads((OUT_DIR / "sources.json").read_text(encoding="utf-8"))

    failures = 0
    for job in JOBS:
        raw_path = RAW_DIR / f"{job['slug']}.html"
        try:
            if reuse and raw_path.exists():
                raw = raw_path.read_bytes()
                final_url = sources.get(job["out"], {}).get("url", job["url"])
            else:
                final_url, raw = fetch(job["url"])
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {job['out']}: {exc}")
            failures += 1
            continue

        raw_path.write_bytes(raw)

        soup = BeautifulSoup(decode(raw), "html.parser")
        node = extract_main(soup)
        if node is None:
            print(f"FAIL {job['out']}: 未找到正文容器")
            failures += 1
            continue

        body = clean(node.get_text("\n", strip=True))
        if len(body) < 500:
            print(f"FAIL {job['out']}: 正文过短（{len(body)} 字）")
            failures += 1
            continue

        # 部分站点把标题和成文日期也放在正文容器里，去掉避免与文件头重复。
        def norm(line: str) -> str:
            return re.sub(r"\s+", "", line).replace("(", "（").replace(")", "）")

        title_lines = {norm(ln) for ln in job["title"].splitlines() if ln.strip()}
        body_lines = body.splitlines()
        while body_lines and norm(body_lines[0]) in title_lines:
            body_lines.pop(0)
        body = "\n".join(body_lines).lstrip()

        text = f"{job['title']}\n\n{body}\n"
        (OUT_DIR / job["out"]).write_text(text, encoding="utf-8")
        sources[job["out"]] = {
            "url": final_url,
            "publisher": job["publisher"],
            "fetched_at": (
                sources.get(job["out"], {}).get("fetched_at")
                or time.strftime("%Y-%m-%d")
            ),
        }
        print(f"OK   {job['out']}: {len(text)} chars")
        print(f"     HEAD: {body[:60]}")
        print(f"     TAIL: {body[-60:]}")

    (OUT_DIR / "sources.json").write_text(
        json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
