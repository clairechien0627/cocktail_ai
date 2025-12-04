"""
Difford's Guide 調酒資料匯入腳本（Docker + 本機兼容完整版）

基於原始版本重構（來源：:contentReference[oaicite:1]{index=1}）
新增：
- --yes：自動模式（Docker 專用）
- 自動偵測無 stdin（CI / Docker），自動啟用 --yes
- 修正環境變數：使用 MONGODB_URI / MONGODB_NAME
- 修正資料路徑：./data/diffordsguide/*.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# 加入專案根目錄（讓 app.models 可以被 import）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.models import Cocktail   # 來自原始檔案

# ------------------------
# CLI 參數
# ------------------------
parser = argparse.ArgumentParser(description="Import Diffordsguide cocktail data into MongoDB")
parser.add_argument("--yes", action="store_true",
                    help="Auto-clear DB and skip all prompts (Docker mode).")
args = parser.parse_args()


# ------------------------
# 檢查是否有 stdin（重要！）
# Docker 沒有 tty → isatty()=False → 不能使用 input()
# ------------------------
def can_prompt():
    return sys.stdin and sys.stdin.isatty()


# ------------------------
# 主匯入器
# ------------------------
class DiffordsGuideImporter:
    def __init__(self, data_dir, mongo_uri, db_name):
        self.data_dir = data_dir
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db.cocktails

        self.stats = {
            'total_files': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    # --------------------------------------------------
    # 舊程式裡的分類推斷（完全保留）
    # --------------------------------------------------
    def infer_category(self, data):
        name = data.get('name', '').lower()
        ingredients = ' '.join(data.get('ingredients', [])).lower()

        if 'martini' in name:
            return 'Martini'
        elif 'margarita' in name:
            return 'Margarita'
        elif 'mojito' in name:
            return 'Mojito'
        elif 'negroni' in name:
            return 'Negroni'
        elif 'sour' in name or 'fizz' in name or 'collins' in name:
            return 'Sour'
        elif 'tiki' in name or 'mai tai' in name or 'zombie' in name:
            return 'Tiki'
        elif 'punch' in name:
            return 'Punch'
        elif 'shot' in name:
            return 'Shot'
        elif 'coffee' in name or 'espresso' in name:
            return 'Coffee'
        elif 'frozen' in name or 'daiquiri' in name:
            return 'Frozen'

        if 'vodka' in ingredients:
            return 'Vodka-based'
        elif 'gin' in ingredients:
            return 'Gin-based'
        elif 'rum' in ingredients:
            return 'Rum-based'
        elif 'tequila' in ingredients:
            return 'Tequila-based'
        elif 'whisky' in ingredients or 'whiskey' in ingredients or 'bourbon' in ingredients:
            return 'Whisky-based'
        elif 'brandy' in ingredients or 'cognac' in ingredients:
            return 'Brandy-based'

        return 'Other'

    # --------------------------------------------------
    def infer_difficulty(self, data):
        ingredient_count = len(data.get('ingredients_detail', data.get('ingredients', [])))

        method_steps = 0
        if data.get('method_sections'):
            for section in data['method_sections']:
                method_steps += len(section.get('steps', []))
        else:
            method_steps = len(data.get('method', []))

        if ingredient_count <= 3 and method_steps <= 3:
            return 'easy'
        elif ingredient_count <= 5 and method_steps <= 6:
            return 'medium'
        else:
            return 'hard'

    # --------------------------------------------------
    def generate_tags(self, data):
        tags = []
        name = data.get('name', '').lower()
        ingredients = ' '.join(data.get('ingredients', [])).lower()

        if 'vodka' in ingredients:
            tags.append('vodka')
        if 'gin' in ingredients:
            tags.append('gin')
        if 'rum' in ingredients:
            tags.append('rum')
        if 'tequila' in ingredients:
            tags.append('tequila')
        if 'whisky' in ingredients or 'whiskey' in ingredients or 'bourbon' in ingredients:
            tags.append('whisky')
        if 'brandy' in ingredients or 'cognac' in ingredients:
            tags.append('brandy')

        if 'coffee' in name or 'espresso' in ingredients:
            tags.append('coffee')
        if 'chocolate' in ingredients:
            tags.append('chocolate')
        if 'fruit' in ingredients or 'juice' in ingredients:
            tags.append('fruity')
        if 'cream' in ingredients:
            tags.append('creamy')
        if 'mint' in ingredients:
            tags.append('minty')

        if 'classic' in name:
            tags.append('classic')
        if 'tiki' in name:
            tags.append('tiki')

        taste_profile = data.get('strength_taste')
        if taste_profile and isinstance(taste_profile, dict):
            strength_data = taste_profile.get('strength')
            if strength_data and isinstance(strength_data, dict):
                strength = strength_data.get('value')
                if strength and strength >= 8:
                    tags.append('strong')
                elif strength and strength <= 3:
                    tags.append('light')

        return tags

    # --------------------------------------------------
    def transform_cocktail(self, data):
        transformed = data.copy()
        transformed['category'] = self.infer_category(data)
        transformed['difficulty'] = self.infer_difficulty(data)
        transformed['tags'] = self.generate_tags(data)
        return transformed

    # --------------------------------------------------
    def import_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 檢查重複
            existing = None
            if data.get('slug'):
                existing = self.collection.find_one({'slug': data['slug']})
            if not existing and data.get('name'):
                existing = self.collection.find_one({'name': data['name']})

            if existing:
                self.stats['skipped'] += 1
                return False

            transformed_data = self.transform_cocktail(data)
            Cocktail.create(self.db, transformed_data)

            self.stats['success'] += 1
            return True

        except Exception as e:
            self.stats['failed'] += 1
            self.stats['errors'].append({'file': os.path.basename(filepath), 'error': str(e)})
            print(f"[ERROR] {filepath}: {e}")
            return False

    # --------------------------------------------------
    def import_all(self, clear_existing=False):
        print("\n開始匯入 Diffordsguide 調酒資料")
        print("=" * 60)

        if clear_existing:
            print("[!] 清空舊資料...")
            result = self.collection.delete_many({})
            print(f"[OK] 已刪除 {result.deleted_count} 筆\n")

        json_files = [f for f in os.listdir(self.data_dir) if f.endswith(".json")]
        self.stats["total_files"] = len(json_files)

        print(f"找到 {len(json_files)} 個 JSON 檔案\n")

        for filename in json_files:
            self.import_file(os.path.join(self.data_dir, filename))

        self.generate_report()

    # --------------------------------------------------
    def generate_report(self):
        print("\n匯入報告")
        print("=" * 60)
        print(f"總檔案: {self.stats['total_files']}")
        print(f"成功: {self.stats['success']}")
        print(f"略過: {self.stats['skipped']}")
        print(f"失敗: {self.stats['failed']}")

        if self.stats["errors"]:
            print("\n[ERROR] 前 10 筆錯誤：")
            for err in self.stats["errors"][:10]:
                print(f"- {err['file']}: {err['error']}")

        print("=" * 60)


# ------------------------
# 主程式入口
# ------------------------
def main():
    load_dotenv()

    # ✔ 統一環境變數
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, "data", "diffordsguide")

    MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/")
    DB_NAME = os.getenv("MONGODB_NAME", "cocktail_db")

    if not os.path.exists(DATA_DIR):
        print(f"找不到資料目錄: {DATA_DIR}")
        sys.exit(1)

    # 清空資料邏輯：三合一合併邏輯
    if args.yes:
        clear_existing = True
        print("(--yes) 自動模式：將清空現有資料。")
    else:
        if can_prompt():
            choice = input("是否清空現有調酒資料？(y/N): ").strip().lower()
            clear_existing = (choice == "y")
        else:
            # Docker / CI 自動模式
            print("無 stdin（Docker/CI 環境），自動清空資料...")
            clear_existing = True

    importer = DiffordsGuideImporter(DATA_DIR, MONGO_URI, DB_NAME)
    importer.import_all(clear_existing=clear_existing)


if __name__ == "__main__":
    main()
