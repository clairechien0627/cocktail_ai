import os
import json
import time
from typing import Any, Dict, List

from dotenv import load_dotenv
from google.cloud import translate_v3 as translate  # Cloud Translation v3[web:91]

load_dotenv()

DIFFORDS_DIR = os.getenv("DIFFORDS_DIR", "./data/diffordsguide")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", DIFFORDS_DIR)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")  # 可從環境或寫死字串
LOCATION = "global"

client = translate.TranslationServiceClient()

BATCH_SIZE = 50
SLEEP_SEC = 1


def translate_text(text: str) -> str:
    """單句翻成繁中；空字串就直接回空。"""
    if not text:
        return ""
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",
            "source_language_code": "en",
            "target_language_code": "zh-TW",
        }
    )
    return response.translations[0].translated_text


def translate_list(lines: List[str]) -> List[str]:
    return [translate_text(x) for x in lines]


def build_zh_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    name = data.get("name", "")
    name_en = name

    # 1) 酒名：若已經有 name_zh，就用原本的，否則才翻
    name_zh = data.get("name_zh") or translate_text(name)

    # 2) 材料列表：若已經有 ingredients_zh，就沿用
    ingredients = data.get("ingredients", [])
    ingredients_zh = data.get("ingredients_zh") or translate_list(ingredients)

    # 3) review / history / more_categories 同樣邏輯
    review = data.get("review", [])
    history_paras = (data.get("history") or {}).get("paragraphs", [])
    more_categories = data.get("more_categories", [])

    review_zh = data.get("review_zh") or translate_list(review)
    history_zh = data.get("history_zh") or translate_list(history_paras)
    more_categories_zh = data.get("more_categories_zh") or translate_list(more_categories)

    # 4) method_sections：若已經有 method_sections_zh 就用舊的，沒有才用英文去翻
    method_sections_zh = data.get("method_sections_zh") or []
    if not method_sections_zh:
        method_sections_zh = []
        for sec in data.get("method_sections", []):
            title = sec.get("title", "")
            steps = sec.get("steps", [])
            method_sections_zh.append({
                "title_zh": translate_text(title),
                "steps_zh": translate_list(steps),
            })

    # 5) 杯具
    glass_zh = data.get("glass_zh")
    glass = data.get("glass")

    def extract_glass_name(glass_obj):
        if isinstance(glass_obj, dict):
            links = glass_obj.get("links") or []
            if links and isinstance(links, list) and links[0].get("text"):
                return links[0]["text"]
            return glass_obj.get("text", "")
        return glass_obj or ""

    # 沒有或空字串時才翻譯
    if not glass_zh:
        glass_raw_text = extract_glass_name(glass)
        glass_zh = translate_text(glass_raw_text) if glass_raw_text else ""

    # 6) 過敏原
    allergens = data.get("allergens") or []
    existing_allergens_zh = data.get("allergens_zh")

    # 6-1) 只有「完全沒有欄位」時才批次翻譯 item
    if existing_allergens_zh is None:
        item_texts = [a.get("item", "") for a in allergens if a.get("item")]
        allergens_zh = translate_list(item_texts) if item_texts else []
    else:
        allergens_zh = existing_allergens_zh

    # 6-2) 逐筆補 item_zh / allergen_zh（只補缺的）
    for idx, a in enumerate(allergens):
        if not a.get("item_zh"):
            if existing_allergens_zh is not None and idx < len(existing_allergens_zh):
                a["item_zh"] = existing_allergens_zh[idx]
            elif idx < len(allergens_zh):
                a["item_zh"] = allergens_zh[idx]
            elif a.get("item"):
                a["item_zh"] = translate_text(a["item"])

        if a.get("allergen") and not a.get("allergen_zh"):
            a["allergen_zh"] = translate_text(a["allergen"])

    return {
        "name_en": name_en,
        "name_zh": name_zh,
        "ingredients_zh": ingredients_zh,
        "review_zh": review_zh,
        "history_zh": history_zh,
        "method_sections_zh": method_sections_zh,
        "more_categories_zh": more_categories_zh,
        "glass_zh": glass_zh,
        "allergens_zh": allergens_zh,  # 保留原本簡單陣列
        "allergens": allergens,        # 內含 item_zh / allergen_zh
    }



def main():
    if not os.path.isdir(DIFFORDS_DIR):
        raise RuntimeError(f"找不到資料夾: {DIFFORDS_DIR}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(DIFFORDS_DIR) if f.endswith(".json")]
    files.sort()
    total = len(files)
    print(f"在 {DIFFORDS_DIR} 找到 {total} 個 JSON 檔案。輸出到 {OUTPUT_DIR}")

    processed = 0
    while processed < total:
        batch = files[processed: processed + BATCH_SIZE]
        print(f"\n本批處理 {len(batch)} 個檔案，進度 {processed}/{total}")
        for filename in batch:
            processed += 1
            src_path = os.path.join(DIFFORDS_DIR, filename)
            with open(src_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            name = data.get("name", filename)
            print(f"  -> 翻譯第 {processed}/{total} 筆：{name}")

            try:
                zh_fields = build_zh_fields(data)
            except Exception as e:
                print(f"     ❌ 翻譯失敗，先用空欄位：{e}")
                zh_fields = {
                    "name_zh": "",
                    "ingredients_zh": [],
                    "review_zh": [],
                    "history_zh": [],
                    "method_sections_zh": [],
                    "more_categories_zh": [],
                }

            merged = dict(data)
            merged.update(zh_fields)

            base, ext = os.path.splitext(filename)
            out_name = f"{base}{ext}"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, ensure_ascii=False, indent=2)
            print(f"     ✅ 已輸出 {out_name}")

        print(f"本批完成，休息 {SLEEP_SEC} 秒...\n")
        time.sleep(SLEEP_SEC)

    print("\n✅ 全部完成，資料夾裡會有對應的 xxx_zh.json 檔。")


if __name__ == "__main__":
    main()
