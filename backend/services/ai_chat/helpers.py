# -*- coding: utf-8 -*-
"""工具函数 — 无状态、不依赖服务类"""
from __future__ import annotations

import base64
import io
import json
import os
import re
import time

from backend.core.config import settings

AI_DATA_DIR = os.path.join(settings.BASE_DIR, "backend", "data", "ai")

TONE_LABELS = {
    "professional": "专业模式", "casual": "轻松模式",
    "encouraging": "鼓励模式", "analytical": "分析模式", "safety": "安全模式",
}


def is_unlocked(user_id: int) -> bool:
    try:
        with open(os.path.join(AI_DATA_DIR, "quota_override.json"), "r") as f:
            overrides = json.load(f)
        return overrides.get(str(user_id)) == time.strftime("%Y-%m-%d")
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def process_image(data_url: str) -> str:
    """识别图片内容 — VL 优先 → Tesseract → EasyOCR 三级降级。"""
    try:
        match = re.match(r"data:image/\w+;base64,(.+)", data_url)
        if not match:
            return ""
        img_b64 = match.group(1)
        img_bytes = base64.b64decode(img_b64)
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(img_bytes))
            w, h = img.size
            meta = f"[图片: {img.format or '?'}, {w}x{h}]"
        except Exception:
            meta = "[图片上传成功]"

        result = None

        # ── L1: VL 模型（需配置 VISION_API_KEY）──
        from backend.core.config import settings
        if settings.VISION_API_KEY and "你的" not in settings.VISION_API_KEY:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.VISION_API_KEY, base_url=settings.VISION_BASE_URL)
                resp = client.chat.completions.create(
                    model=settings.VISION_MODEL,
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "只描述这张图片本身的内容，不要与任何之前的图片对比。如果是文档/教案/板书/表格，提取其中所有文字并按原结构输出。如果是照片，描述场景和关键细节。用中文。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    ]}],
                    max_tokens=800,
                )
                result = resp.choices[0].message.content.strip()
            except Exception:
                pass

        # ── L2: Tesseract OCR ──
        if not result:
            try:
                import pytesseract
                if not pytesseract.pytesseract.tesseract_cmd or pytesseract.pytesseract.tesseract_cmd == "tesseract":
                    for path in [r"D:\Tool\QCR\tesseract.exe", r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                                 "/usr/bin/tesseract", "/usr/local/bin/tesseract"]:
                        if os.path.exists(path):
                            pytesseract.pytesseract.tesseract_cmd = path
                            break
                img_ocr = Image.open(io.BytesIO(img_bytes))
                for lang in ["chi_sim+eng", "eng"]:
                    try:
                        result = pytesseract.image_to_string(img_ocr, lang=lang).strip()
                        if result:
                            break
                    except Exception:
                        continue
            except Exception:
                pass

        # ── L3: EasyOCR ──
        if not result:
            try:
                import easyocr
                reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
                results = reader.readtext(img_bytes)
                result = " ".join(r[1] for r in results)
            except Exception:
                pass

        if result:
            return f"{meta}\n{result}"
        return f"{meta}\n[无文字内容]"
    except Exception as e:
        return f"[图片解析失败: {str(e)[:80]}]"


def tone_label(tone) -> str:
    return TONE_LABELS.get(tone.value if hasattr(tone, 'value') else tone, "未知")


def infer_delta(message: str) -> int:
    length = len(message)
    if length <= 3:
        return -3
    if length > 100:
        return 5
    if length > 20:
        return 3
    return 2


def build_history_summary(history: list, last_n: int = 3) -> str:
    recent = [m for m in history[-last_n * 2:]
              if m.get("role") in ("user", "assistant")]
    if not recent:
        return ""
    lines = []
    for m in recent:
        role_label = "教师" if m["role"] == "user" else "助手"
        content = (m.get("content") or "")[:100]
        lines.append(f"{role_label}: {content}")
    return "\n".join(lines)
