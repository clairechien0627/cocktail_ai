import json
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# 專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def main():
    load_dotenv()
    DATA_DIR = os.path.join(PROJECT_ROOT, "data", "diffordsguide_trans")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("MONGO_DB_NAME", "cocktail_ai")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col_zh = db.cocktails_zh

    print(f"📦 連線到 MongoDB: {MONGO_URI} / DB: {DB_NAME}")
    print(f"📂 資料目錄: {DATA_DIR}")

    if not os.path.exists(DATA_DIR):
        print(f"❌ 找不到資料目錄: {DATA_DIR}")
        sys.exit(1)

    # 每次執行前都詢問是否清空 cocktails_zh
    answer = input("🧹 要先清空 cocktails_zh 嗎？(y/N) ").strip().lower()

    if answer == "y":
        count_before = col_zh.count_documents({})
        col_zh.delete_many({})
        print(f"🧹 已清空 cocktails_zh，刪除 {count_before} 筆文件")
    else:
        print("🧹 保留原本 cocktails_zh 資料，不進行清空")


    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    total_files = len(json_files)
    print(f"🔎 找到 {total_files} 個 JSON 檔案（含中英文混合欄位）")

    inserted = 0
    skipped_no_slug = 0
    skipped_no_zh = 0

    for idx, filename in enumerate(sorted(json_files), start=1):
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        slug = data.get("slug")
        if not slug:
            skipped_no_slug += 1
            print(f"  ⚠️ [{idx}/{total_files}] {filename} 沒有 slug，略過")
            continue

        cocktail_id = slug

        raw_allergens = data.get("allergens") or []

        # 只留下中文＋你要的欄位
        zh_allergens = []
        for a in raw_allergens:
            # 完全沒中文就略過，避免塞一堆空資料
            if not a.get("item_zh") and not a.get("allergen_zh"):
                continue
            zh_allergens.append(
                {
                    "item_zh": a.get("item_zh"),
                    "allergen_zh": a.get("allergen_zh"),
                    # 如果你還是想保留原始連結就留下
                    "allergen_url": a.get("allergen_url"),
                }
            )


        zh_doc = {
            "cocktail_id": cocktail_id,
            "name_zh": data.get("name_zh"),
            "ingredients_zh": data.get("ingredients_zh"),
            "review_zh": data.get("review_zh"),
            "history_zh": data.get("history_zh"),
            "method_sections_zh": data.get("method_sections_zh"),
            "more_categories_zh": data.get("more_categories_zh"),
            "glass_zh": data.get("glass_zh"),
            "allergens_zh": zh_allergens

        }

        has_any_zh = any(
            bool(zh_doc[k])
            for k in [
                "name_zh",
                "ingredients_zh",
                "review_zh",
                "history_zh",
                "method_sections_zh",
                "more_categories_zh",
                "glass_zh",
                "allergens_zh",
            ]
        )

        if not has_any_zh:
            skipped_no_zh += 1
            print(f"  ➖ [{idx}/{total_files}] {filename} ({cocktail_id}) 沒有任何中文欄位，略過")
            continue

        col_zh.update_one(
            {"cocktail_id": cocktail_id},
            {"$set": zh_doc},
            upsert=True,
        )
        inserted += 1
        print(f"  ✅ [{idx}/{total_files}] 已寫入/更新: {cocktail_id}")

    print("\n📊 結果摘要")
    print(f"  ✅ 寫入 / 更新: {inserted} 筆")
    print(f"  ⚠️ 略過（無 slug）: {skipped_no_slug} 筆")
    print(f"  ➖ 略過（無中文欄位）: {skipped_no_zh} 筆")
    print("🎉 完成匯入 cocktails_zh")


if __name__ == "__main__":
    main()
