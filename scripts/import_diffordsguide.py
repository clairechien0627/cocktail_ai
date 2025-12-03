"""
Difford's Guide 調酒資料匯入腳本

功能：
- 讀取 data/diffordsguide/ 目錄中的所有 JSON 檔案
- 轉換資料格式以符合 MongoDB schema
- 自動推斷分類、難度、標籤
- 批次匯入到 MongoDB
- 產生匯入報告
"""

import json
import os
import sys
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Cocktail


class DiffordsGuideImporter:
    """Difford's Guide 資料匯入器"""

    def __init__(self, data_dir, mongo_uri, db_name):
        """
        初始化匯入器

        Args:
            data_dir: Difford's Guide JSON 檔案目錄
            mongo_uri: MongoDB 連接字串
            db_name: 資料庫名稱
        """
        self.data_dir = data_dir
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.stats = {
            'total_files': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    def infer_category(self, data):
        """
        從調酒資料推斷分類

        分類邏輯：
        - 基於調酒名稱中的關鍵字
        - 基於主要基酒類型
        """
        name = data.get('name', '').lower()
        ingredients = ' '.join(data.get('ingredients', [])).lower()

        # 基於名稱的分類
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

        # 基於材料的分類
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

    def infer_difficulty(self, data):
        """
        從調酒複雜度計算難度

        難度判斷：
        - easy: 3種以下材料，3步以下步驟
        - medium: 5種以下材料，6步以下步驟
        - hard: 其他
        """
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

    def generate_tags(self, data):
        """
        從調酒資料生成標籤

        標籤來源：
        - 主要基酒
        - 風味特徵
        - 場合/時間
        """
        tags = []
        name = data.get('name', '').lower()
        ingredients = ' '.join(data.get('ingredients', [])).lower()

        # 基酒標籤
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

        # 風味標籤
        if 'coffee' in name or 'coffee' in ingredients or 'espresso' in ingredients:
            tags.append('coffee')
        if 'chocolate' in ingredients or 'cacao' in ingredients:
            tags.append('chocolate')
        if 'fruit' in ingredients or 'juice' in ingredients:
            tags.append('fruity')
        if 'cream' in ingredients:
            tags.append('creamy')
        if 'mint' in ingredients:
            tags.append('minty')

        # 風格標籤
        if 'classic' in name:
            tags.append('classic')
        if 'tiki' in name:
            tags.append('tiki')

        # 場合標籤
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

    def transform_cocktail(self, data):
        """轉換單一調酒資料以符合 schema"""
        transformed = data.copy()

        # 推斷分類、難度、標籤
        transformed['category'] = self.infer_category(data)
        transformed['difficulty'] = self.infer_difficulty(data)
        transformed['tags'] = self.generate_tags(data)

        return transformed

    def import_file(self, filepath):
        """匯入單一 JSON 檔案"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 檢查是否已存在（基於 slug 或 name）
            existing = None
            if data.get('slug'):
                existing = self.db.cocktails.find_one({'slug': data['slug']})
            if not existing and data.get('name'):
                existing = self.db.cocktails.find_one({'name': data['name']})

            if existing:
                self.stats['skipped'] += 1
                return False

            # 轉換資料
            transformed_data = self.transform_cocktail(data)

            # 使用 Cocktail 模型建立
            Cocktail.create(self.db, transformed_data)

            self.stats['success'] += 1
            return True

        except Exception as e:
            self.stats['failed'] += 1
            self.stats['errors'].append({
                'file': os.path.basename(filepath),
                'error': str(e)
            })
            self.safe_print(f"[ERROR] {os.path.basename(filepath)} - {str(e)}")
            return False

    def safe_print(self, text):
        """安全地輸出文字（處理 Windows 編碼問題）"""
        try:
            print(text)
        except UnicodeEncodeError:
            # 移除 emoji 和特殊字符
            safe_text = text.encode('ascii', 'ignore').decode('ascii')
            print(safe_text)

    def import_all(self, clear_existing=False):
        """
        匯入所有調酒

        Args:
            clear_existing: 是否清空現有資料（預設 False）
        """
        self.safe_print("=" * 60)
        self.safe_print("Difford's Guide 調酒資料匯入")
        self.safe_print("=" * 60)

        # 清空現有資料（可選）
        if clear_existing:
            self.safe_print("\n[!] 清空現有調酒資料...")
            result = self.db.cocktails.delete_many({})
            self.safe_print(f"[OK] 已刪除 {result.deleted_count} 筆資料")

        # 取得所有 JSON 檔案
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        self.stats['total_files'] = len(json_files)

        self.safe_print(f"\n找到 {len(json_files)} 個 JSON 檔案")
        self.safe_print(f"資料目錄: {self.data_dir}")
        self.safe_print("\n開始匯入...\n")

        # 批次處理
        batch_size = 100
        for i, filename in enumerate(json_files, 1):
            filepath = os.path.join(self.data_dir, filename)
            self.import_file(filepath)

            # 進度報告
            if i % batch_size == 0 or i == len(json_files):
                print(f"進度: {i}/{len(json_files)} ({i/len(json_files)*100:.1f}%) | "
                      f"成功: {self.stats['success']} | "
                      f"略過: {self.stats['skipped']} | "
                      f"失敗: {self.stats['failed']}")

        # 產生報告
        self.generate_report()

    def generate_report(self):
        """產生匯入報告"""
        self.safe_print("\n" + "=" * 60)
        self.safe_print("匯入報告")
        self.safe_print("=" * 60)
        self.safe_print(f"總檔案數: {self.stats['total_files']}")
        self.safe_print(f"[OK] 成功匯入: {self.stats['success']}")
        self.safe_print(f"[SKIP] 略過（重複）: {self.stats['skipped']}")
        self.safe_print(f"[FAIL] 失敗: {self.stats['failed']}")

        if self.stats['errors']:
            self.safe_print(f"\n[ERROR] 錯誤詳情（前 10 筆）:")
            for error in self.stats['errors'][:10]:
                self.safe_print(f"  - {error['file']}: {error['error']}")

        # 資料庫統計
        total_in_db = self.db.cocktails.count_documents({})
        self.safe_print(f"\n資料庫調酒總數: {total_in_db}")

        # 分類統計
        categories = self.db.cocktails.aggregate([
            {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ])
        self.safe_print(f"\n分類統計（Top 10）:")
        for cat in categories:
            self.safe_print(f"  - {cat['_id']}: {cat['count']} 款")

        self.safe_print("\n" + "=" * 60)
        self.safe_print("[DONE] 匯入完成！")
        self.safe_print("=" * 60)


def main():
    """主函數"""
    # 載入環境變數
    load_dotenv()

    # 配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'diffordsguide')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('MONGO_DB_NAME', 'cocktail_ai')

    # 驗證資料目錄
    if not os.path.exists(DATA_DIR):
        print(f"❌ 錯誤: 找不到資料目錄: {DATA_DIR}")
        sys.exit(1)

    # 詢問是否清空現有資料
    print(f"\n資料目錄: {DATA_DIR}")
    print(f"資料庫: {DB_NAME}")
    clear = input("\n是否清空現有調酒資料？(y/N): ").strip().lower()
    clear_existing = (clear == 'y')

    # 建立匯入器並執行
    importer = DiffordsGuideImporter(DATA_DIR, MONGO_URI, DB_NAME)
    importer.import_all(clear_existing=clear_existing)


if __name__ == '__main__':
    main()