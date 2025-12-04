"""
RAG 向量化腳本（使用 Qdrant）
功能：將 MongoDB 調酒資料向量化，存入 Qdrant 向量資料庫
執行方式：python setup_rag.py
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm

# 載入環境變數
load_dotenv()

# 配置
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'cocktail_ai')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-mpnet-base-v2')
QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', '6333'))

class RAGSetup:
    """RAG 向量化設定器（Qdrant 版）"""

    def __init__(self):
        print("=" * 60)
        print("AI 調酒大師 - RAG 向量化設定")
        print("=" * 60)

        # MongoDB
        print("\n[1/4] 連接 MongoDB...")
        self.mongo_client = MongoClient(MONGODB_URI)
        self.db = self.mongo_client[MONGODB_DB]

        cocktail_count = self.db.cocktails.count_documents({})
        print(f"✓ 找到 {cocktail_count} 筆調酒資料")

        if cocktail_count == 0:
            print("❌ 找不到調酒資料，請先執行 import_diffordsguide.py")
            sys.exit(1)

        # Embedding 模型
        print(f"\n[2/4] 載入 Embedding 模型: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"✓ 模型載入完成（維度: {self.embedding_dim}）")

        # Qdrant
        print(f"\n[3/4] 連接 Qdrant 向量資料庫...")
        try:
            self.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            self.qdrant.get_collections()
            print(f"✓ Qdrant 連接成功 ({QDRANT_HOST}:{QDRANT_PORT})")
        except Exception as e:
            print(f"❌ Qdrant 連接失敗: {e}")
            sys.exit(1)

    def create_collections(self):
        """建立向量集合"""
        print("\n[4/4] 建立向量集合...")

        collections = [
            "cocktails_taste",
            "cocktails_scenario"
        ]

        for name in collections:
            try:
                self.qdrant.delete_collection(name)
                print(f" - 刪除舊集合: {name}")
            except:
                pass

            self.qdrant.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            print(f" ✓ 建立集合: {name}")

    def prepare_taste_text(self, cocktail: dict) -> str:
        """準備口味向量文本"""
        parts = []
        parts.append(f"Name: {cocktail.get('name', '')}")

        reviews = cocktail.get('review', [])
        if reviews:
            parts.append("Review: " + " ".join(reviews))

        taste = cocktail.get('taste_profile', {})
        if taste:
            parts.append(
                f"Taste: strength={taste.get('strength')}, sweetness={taste.get('sweetness')}, sour={taste.get('sour')}, bitter={taste.get('bitter')}"
            )

        ingredients = cocktail.get('ingredients', [])[:5]
        if ingredients:
            parts.append("Ingredients: " + ", ".join(ingredients))

        return " | ".join(parts)

    def prepare_scenario_text(self, cocktail: dict) -> str:
        """準備場景向量文本"""
        parts = []
        parts.append(f"Name: {cocktail.get('name', '')}")

        history = cocktail.get('history', [])
        if history:
            parts.append("History: " + " ".join(history))

        cotd = cocktail.get('cotd', [])
        if cotd:
            parts.append("Description: " + " ".join(cotd))

        reviews = cocktail.get('review', [])
        if reviews:
            parts.append("Review: " + " ".join(reviews))

        category = cocktail.get('category', '')
        if category:
            parts.append(f"Category: {category}")

        tags = cocktail.get('tags', [])
        if tags:
            parts.append("Tags: " + ", ".join(tags))

        return " | ".join(parts)

    def vectorize_and_store(self):
        """向量化並存入 Qdrant"""
        print("\n" + "=" * 60)
        print("開始向量化...")
        print("=" * 60)

        cocktails = list(self.db.cocktails.find({}))
        total = len(cocktails)
        print(f"\n處理 {total} 筆調酒資料...\n")

        # Step 1: 準備文本
        print("[1/3] 準備文本...")
        taste_texts, scenario_texts, metadata_list = [], [], []

        for cocktail in tqdm(cocktails, desc="準備文本"):
            taste_texts.append(self.prepare_taste_text(cocktail))
            scenario_texts.append(self.prepare_scenario_text(cocktail))

            metadata_list.append({
                'id': str(cocktail['_id']),
                'name': cocktail.get('name', ''),
                'category': cocktail.get('category', ''),
                'difficulty': cocktail.get('difficulty', ''),
                'strength': cocktail.get('taste_profile', {}).get('strength', 0),
                'sweetness': cocktail.get('taste_profile', {}).get('sweetness', 0)
            })

        # Step 2: 生成向量
        print("\n[2/3] 生成向量...")
        taste_embeddings = self.model.encode(taste_texts, batch_size=32, show_progress_bar=True)
        scenario_embeddings = self.model.encode(scenario_texts, batch_size=32, show_progress_bar=True)

        # Step 3: 存入 Qdrant
        print("\n[3/3] 存入向量資料庫...")
        batch_size = 100

        # 口味
        for i in tqdm(range(0, len(taste_embeddings), batch_size), desc="上傳口味向量"):
            end = min(i + batch_size, len(taste_embeddings))
            points = [
                PointStruct(
                    id=idx,
                    vector=taste_embeddings[idx].tolist(),
                    payload=metadata_list[idx]
                )
                for idx in range(i, end)
            ]
            self.qdrant.upsert("cocktails_taste", points)

        # 場景
        for i in tqdm(range(0, len(scenario_embeddings), batch_size), desc="上傳場景向量"):
            end = min(i + batch_size, len(scenario_embeddings))
            points = [
                PointStruct(
                    id=idx,
                    vector=scenario_embeddings[idx].tolist(),
                    payload=metadata_list[idx]
                )
                for idx in range(i, end)
            ]
            self.qdrant.upsert("cocktails_scenario", points)

        print("\n✓ 向量化完成！")

    def verify_setup(self):
        """驗證 RAG 設定"""
        print("\n" + "=" * 60)
        print("驗證設定")
        print("=" * 60)

        # count API（新版）
        taste_count = self.qdrant.count(collection_name="cocktails_taste").count
        scenario_count = self.qdrant.count(collection_name="cocktails_scenario").count

        print(f"\nQdrant:")
        print(f" - cocktails_taste: {taste_count} 筆")
        print(f" - cocktails_scenario: {scenario_count} 筆")

        # 測試查詢
        print("\n測試查詢: '清爽酸甜的調酒'")
        query_text = "清爽酸甜的調酒"
        query_vec = self.model.encode(query_text).tolist()

        # 新版 query_points()
        response = self.qdrant.query_points(
            collection_name="cocktails_taste",
            query=query_vec,
            limit=3
        )

        print("\n查詢結果:")
        for idx, result in enumerate(response.points, 1):
            print(f"{idx}. {result.payload.get('name')} - score={result.score:.4f}")

        print("\n✓ 驗證完成！")

    def cleanup(self):
        self.mongo_client.close()

def main():
        setup = RAGSetup()
        setup.create_collections()
        setup.vectorize_and_store()
        setup.verify_setup()
        setup.cleanup()

        print("\n" + "=" * 60)
        print("RAG 設定完成！")
        print("=" * 60)

if __name__ == "__main__":
    main()
