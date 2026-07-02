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
    try:
        match = re.match(r"data:image/\w+;base64,(.+)", data_url)
        if not match:
            return ""
        img_bytes = base64.b64decode(match.group(1))
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(img_bytes))
            w, h = img.size
            meta = f"[图片: {img.format or '?'}, {w}x{h}]"
        except Exception:
            meta = "[图片上传成功]"
        ocr_text = ""
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
                    ocr_text = pytesseract.image_to_string(img_ocr, lang=lang).strip()
                    if ocr_text:
                        break
                except Exception:
                    continue
        except Exception:
            try:
                import easyocr
                reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
                results = reader.readtext(img_bytes)
                ocr_text = " ".join(r[1] for r in results)
            except Exception:
                pass
        if ocr_text:
            return f"{meta}\n识别文字：\n{ocr_text}"
        return meta
    except Exception:
        return "[图片解析失败]"


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
