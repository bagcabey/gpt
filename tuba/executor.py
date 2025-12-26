from typing import Dict, Any
import subprocess
import time

import pyautogui

from .ocr import find_text, select_best


def execute(decision: Dict[str, Any]) -> str:
    """
    Mock eylem yürütücüsü.

    Gerçek C# köprüsü yerine, hangi aksiyonun seçildiğini geri döndürür.
    """
    action = decision.get("action")
    if action == "open_app":
        app = decision["parameters"].get("app_name", "bilinmiyor")
        subprocess.Popen(app, shell=True)
        return f"Uygulama açılıyor: {app}."
    if action == "set_volume":
        level = decision["parameters"].get("level")
        _set_volume_via_hotkeys(level)
        return f"Ses {level} seviyesine ayarlandı."
    if action == "click_ocr":
        target = decision["parameters"].get("target", "hedef")
        results = find_text(target or "")
        best = select_best(results)
        if not best:
            return f"{target} bulunamadı."
        x = best.box[0] + best.box[2] // 2
        y = best.box[1] + best.box[3] // 2
        pyautogui.click(x, y)
        return f"{target} tıklandı."
    if action == "click_xy":
        x = decision["parameters"].get("x")
        y = decision["parameters"].get("y")
        pyautogui.click(x, y)
        return f"({x}, {y}) konumuna tıklandı."
    if action == "type_text":
        text = decision["parameters"].get("text", "")
        pyautogui.typewrite(text)
        return f"Yazıldı: {text}"
    if action == "chat_response":
        return decision.get("response", "Dinliyorum.")
    return f"Bilinmeyen eylem: {action}"


def _set_volume_via_hotkeys(level: int | None) -> None:
    """
    Yaklaşık bir ses seviyesi ayarı.
    Önce sesi minimuma çeker, ardından hedef seviyeye kadar yükseltir.
    """
    if level is None:
        return
    level = max(0, min(100, int(level)))
    # Sesi sıfıra çek
    for _ in range(50):
        pyautogui.press("volumedown")
    # Hedefe çık
    steps = level // 2  # 0-100 arası ~50 step varsayımı
    for _ in range(steps):
        pyautogui.press("volumeup")
