# import_translist.py
import json
import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "cocktail_ai")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# 檔名 -> collection 名稱
FILE_TO_COLLECTION = {
    "ingredients_translated.json": "ingredients_trans",
    "ingredients_detail_translated.json": "ingredients_detail_trans",
    "glass_translated.json": "glass_trans",
    "allergens_name_translated.json": "allergens_name_trans",
    "allergens_item_translated.json": "allergens_item_trans",
    "more_categories_translated.json": "more_categories_trans",
    "category_translated.json": "categories_trans",
}

def import_simple_trans_table(json_path: Path, collection_name: str):
    col = db[collection_name]

    print(f"\n📂 處理 {json_path.name} → collection: {collection_name}")

    if not json_path.exists():
        print(f"❌ 找不到檔案: {json_path}")
        return

    answer = input(f"🧹 要清空 {collection_name} 嗎？(y/N) ").strip().lower()
    if answer == "y":
        deleted = col.delete_many({}).deleted_count
        print(f"🧹 已刪除 {deleted} 筆")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for en, zh in data.items():
        en = (en or "").strip()
        zh = (zh or "").strip()
        if not en or not zh:
            continue
        docs.append({
            "name_en": en,
            "name_zh": zh,
        })

    if not docs:
        print(f"⚠️ {collection_name} 沒有可匯入資料")
        return

    col.insert_many(docs)
    print(f"✅ {collection_name} 匯入 {len(docs)} 筆")
    col.create_index("name_en")
    col.create_index("name_zh")
    print("🔎 已建立 name_en / name_zh 索引")

def main():
    # 依你的實際資料夾調整；這裡假設所有 *_translated.json 放在 data/trans_tables 下
    base_dir = PROJECT_ROOT / "data/trans_tables"
    print(f"📁 base_dir = {base_dir}")

    for filename, coll_name in FILE_TO_COLLECTION.items():
        json_path = base_dir / filename
        import_simple_trans_table(json_path, coll_name)

    print("\n🎉 所有 trans table 匯入完成")

if __name__ == "__main__":
    main()
