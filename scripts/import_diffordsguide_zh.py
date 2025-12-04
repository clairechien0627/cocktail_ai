# import_diffordsguide_trans.py
import json
import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "diffordsguide_trans"

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "cocktail_ai")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
col = db.cocktails_zh

def main():
    if not DATA_DIR.exists():
        print(f"❌ 資料夾不存在: {DATA_DIR}")
        return

    print(f"📂 讀取資料夾: {DATA_DIR}")
    answer = input("🧹 要清空 cocktails_zh 嗎？(y/N) ").strip().lower()
    if answer == "y":
        deleted = col.delete_many({}).deleted_count
        print(f"🧹 已刪除 {deleted} 筆")

    files = sorted([p for p in DATA_DIR.glob("*.json")])
    print(f"🔎 找到 {len(files)} 個 JSON 食譜檔")

    inserted = 0
    for idx, path in enumerate(files, 1):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        slug = data.get("slug")
        if not slug:
            print(f" ⚠️ [{idx}/{len(files)}] {path.name} 沒有 slug，略過")
            continue

        # 直接整包存進來，欄位維持檔案內原樣（含 name_en / name_zh / review_zh...）
        data["cocktail_id"] = slug  # 額外加一個 id，之後查詢好用

        col.update_one(
            {"cocktail_id": slug},
            {"$set": data},
            upsert=True,
        )
        print(f" ✅ [{idx}/{len(files)}] 寫入 {slug}")
        inserted += 1

    print(f"\n🎉 完成 diffordsguide_trans 匯入，共 {inserted} 筆")

if __name__ == "__main__":
    main()
