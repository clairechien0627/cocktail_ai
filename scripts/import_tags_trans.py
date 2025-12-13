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

def import_tags_trans():
    """專門匯入 tags 翻譯到 MongoDB"""
    collection_name = "tags_trans"
    json_path = PROJECT_ROOT / "data/trans_tables/tags_translated.json"

    col = db[collection_name]

    print(f"\n📂 處理 tags_translated.json → collection: {collection_name}")

    if not json_path.exists():
        print(f"❌ 找不到檔案: {json_path}")
        return

    # 清空現有資料
    deleted = col.delete_many({}).deleted_count
    print(f"🧹 已刪除 {deleted} 筆舊資料")

    # 讀取翻譯檔案
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 建立文檔列表
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

    # 匯入資料
    col.insert_many(docs)
    print(f"✅ {collection_name} 匯入 {len(docs)} 筆")

    # 建立索引
    col.create_index("name_en")
    col.create_index("name_zh")
    print("🔎 已建立 name_en / name_zh 索引")

if __name__ == "__main__":
    print("🚀 開始匯入 Tags 翻譯...")
    import_tags_trans()
    print("\n🎉 Tags 翻譯匯入完成！")
