from dataclasses import dataclass
from typing import List, Optional

import pyautogui
import pytesseract
from PIL import Image

from .config import OCR_MAX_RESULTS


@dataclass
class OCRResult:
    text: str
    box: tuple[int, int, int, int]  # left, top, width, height


def capture_screenshot() -> Image.Image:
    return pyautogui.screenshot()


def find_text(target: str) -> List[OCRResult]:
    img = capture_screenshot()
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang="tur")
    results: List[OCRResult] = []
    for i, text in enumerate(data["text"]):
        if not text:
            continue
        normalized = text.lower()
        if target.lower() in normalized:
            box = (
                int(data["left"][i]),
                int(data["top"][i]),
                int(data["width"][i]),
                int(data["height"][i]),
            )
            results.append(OCRResult(text=text, box=box))
            if len(results) >= OCR_MAX_RESULTS:
                break
    return results


def select_best(result_list: List[OCRResult]) -> Optional[OCRResult]:
    if not result_list:
        return None
    # En büyük kutuyu seç (basit görünürlük sezgisi)
    return max(result_list, key=lambda r: r.box[2] * r.box[3])
