"""
RAG 向量化腳本（只使用 Qdrant，不使用 Chroma）
功能：將 MongoDB 中的調酒資料向量化，存入 Qdrant 向量資料庫

執行方式：
    python setup_rag_qdrant_only.py

前提條件：
    需要先啟動 Qdrant（Docker）：
    docker run -d -p 6333:6333 qdrant/qdrant

預計時間：5-10 分鐘（6,659 筆資料）
產生檔案：
    - qdrant_storage/ (約 50MB)
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
    """RAG 向量化設定器（只使用 Qdrant）"""
    
    def __init__(self):
        print("=" * 60)
        print("🍸 AI 調酒大師 - RAG 向量化設定")
        print("=" * 60)
        
        # 初始化 MongoDB
        print("\n[1/4] 連接 MongoDB...")
        self.mongo_client = MongoClient(MONGODB_URI)
        self.db = self.mongo_client[MONGODB_DB]
        
        cocktail_count = self.db.cocktails.count_documents({})
        print(f"✓ 找到 {cocktail_count} 筆調酒資料")
        
        if cocktail_count == 0:
            print("❌ 錯誤：找不到調酒資料")
            print("   請先執行: python import_diffordsguide.py")
            sys.exit(1)
        
        # 載入 Embedding 模型
        print(f"\n[2/4] 載入 Embedding 模型: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"✓ 模型載入完成（維度: {embedding_dim}）")
        
        # 初始化 Qdrant
        print(f"\n[3/4] 連接 Qdrant 向量資料庫...")
        try:
            self.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            # 測試連接
            self.qdrant.get_collections()
            print(f"✓ Qdrant 連接成功 ({QDRANT_HOST}:{QDRANT_PORT})")
        except Exception as e:
            print(f"❌ Qdrant 連接失敗: {e}")
            print("\n請先啟動 Qdrant：")
            print("   docker run -d -p 6333:6333 qdrant/qdrant")
            print("\n或安裝 Docker Desktop：")
            print("   https://www.docker.com/products/docker-desktop/")
            sys.exit(1)
        
        self.embedding_dim = embedding_dim
    
    def create_collections(self):
        """建立向量集合"""
        print("\n[4/4] 建立向量集合...")
        
        # Qdrant 集合
        collections = [
            "cocktails_taste",      # 口味向量
            "cocktails_scenario"    # 場景向量
        ]
        
        for collection_name in collections:
            # 刪除舊集合（如果存在）
            try:
                self.qdrant.delete_collection(collection_name)
                print(f"   - 刪除舊集合: {collection_name}")
            except:
                pass
            
            # 建立新集合
            self.qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            print(f"   ✓ 建立集合: {collection_name}")
    
    def prepare_taste_text(self, cocktail: dict) -> str:
        """準備口味向量的文本"""
        parts = []
        
        # 名稱
        parts.append(f"Name: {cocktail.get('name', '')}")
        
        # 評論（最重要的口味描述）
        reviews = cocktail.get('review', [])
        if reviews:
            parts.append(f"Review: {' '.join(reviews)}")
        
        # 風味檔案
        taste = cocktail.get('taste_profile', {})
        if taste:
            strength = taste.get('strength', 'N/A')
            sweetness = taste.get('sweetness', 'N/A')
            sour = taste.get('sour', 'N/A')
            bitter = taste.get('bitter', 'N/A')
            parts.append(f"Taste: strength={strength}, sweetness={sweetness}, sour={sour}, bitter={bitter}")
        
        # 主要材料
        ingredients = cocktail.get('ingredients', [])[:5]
        if ingredients:
            parts.append(f"Main ingredients: {', '.join(ingredients)}")
        
        return ' | '.join(parts)
    
    def prepare_scenario_text(self, cocktail: dict) -> str:
        """準備場景向量的文本"""
        parts = []
        
        # 名稱
        parts.append(f"Name: {cocktail.get('name', '')}")
        
        # 歷史/背景故事
        history = cocktail.get('history', [])
        if history:
            parts.append(f"History: {' '.join(history)}")
        
        # Cocktail of the day 描述
        cotd = cocktail.get('cotd', [])
        if cotd:
            parts.append(f"Description: {' '.join(cotd)}")
        
        # 評論（場景描述）
        reviews = cocktail.get('review', [])
        if reviews:
            parts.append(f"Review: {' '.join(reviews)}")
        
        # 分類
        category = cocktail.get('category', '')
        if category:
            parts.append(f"Category: {category}")
        
        # 標籤
        tags = cocktail.get('tags', [])
        if tags:
            parts.append(f"Tags: {', '.join(tags)}")
        
        return ' | '.join(parts)
    
    def vectorize_and_store(self):
        """向量化並存入資料庫"""
        print("\n" + "=" * 60)
        print("開始向量化...")
        print("=" * 60)
        
        # 取得所有調酒
        cocktails = list(self.db.cocktails.find({}))
        total = len(cocktails)
        print(f"\n處理 {total} 筆調酒資料...\n")
        
        # [步驟 1/3] 準備文本
        print("[步驟 1/3] 準備文本...")
        taste_texts = []
        scenario_texts = []
        metadata_list = []
        
        for cocktail in tqdm(cocktails, desc="準備文本"):
            # 口味文本
            taste_text = self.prepare_taste_text(cocktail)
            taste_texts.append(taste_text)
            
            # 場景文本
            scenario_text = self.prepare_scenario_text(cocktail)
            scenario_texts.append(scenario_text)
            
            # Metadata
            metadata = {
                'id': str(cocktail['_id']),
                'name': cocktail.get('name', ''),
                'category': cocktail.get('category', ''),
                'difficulty': cocktail.get('difficulty', ''),
                'rating_professional': cocktail.get('ratings', {}).get('professional', 0),
                'rating_public': cocktail.get('ratings', {}).get('public', 0),
            }
            
            # 風味檔案
            taste_profile = cocktail.get('taste_profile', {})
            if taste_profile:
                metadata['strength'] = taste_profile.get('strength', 0)
                metadata['sweetness'] = taste_profile.get('sweetness', 0)
            
            metadata_list.append(metadata)
        
        # [步驟 2/3] 生成向量
        print("\n[步驟 2/3] 生成向量...")
        
        print("   - 口味向量...")
        taste_embeddings = self.model.encode(
            taste_texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print("   - 場景向量...")
        scenario_embeddings = self.model.encode(
            scenario_texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # [步驟 3/3] 存入向量資料庫
        print("\n[步驟 3/3] 存入向量資料庫...")
        
        # 🔧 分批上傳（避免超過 Qdrant 的 payload 限制）
        batch_size = 100  # 每批 100 筆
        total_batches = (len(taste_embeddings) + batch_size - 1) // batch_size
        
        # 存入 Qdrant (口味)
        print(f"   - 存入 Qdrant (口味) - {total_batches} 批...")
        for i in tqdm(range(0, len(taste_embeddings), batch_size), desc="上傳口味向量"):
            batch_end = min(i + batch_size, len(taste_embeddings))
            
            points_taste = [
                PointStruct(
                    id=idx,
                    vector=taste_embeddings[idx].tolist(),
                    payload=metadata_list[idx]
                )
                for idx in range(i, batch_end)
            ]
            
            self.qdrant.upsert(
                collection_name="cocktails_taste",
                points=points_taste
            )
        
        # 存入 Qdrant (場景)
        print(f"   - 存入 Qdrant (場景) - {total_batches} 批...")
        for i in tqdm(range(0, len(scenario_embeddings), batch_size), desc="上傳場景向量"):
            batch_end = min(i + batch_size, len(scenario_embeddings))
            
            points_scenario = [
                PointStruct(
                    id=idx,
                    vector=scenario_embeddings[idx].tolist(),
                    payload=metadata_list[idx]
                )
                for idx in range(i, batch_end)
            ]
            
            self.qdrant.upsert(
                collection_name="cocktails_scenario",
                points=points_scenario
            )
        
        print("\n✓ 向量化完成！")
    
    def verify_setup(self):
        """驗證設定"""
        print("\n" + "=" * 60)
        print("驗證設定...")
        print("=" * 60)
        
        # 檢查 Qdrant
        taste_count = self.qdrant.count("cocktails_taste").count
        scenario_count = self.qdrant.count("cocktails_scenario").count
        
        print(f"\nQdrant:")
        print(f"  - cocktails_taste: {taste_count} 筆")
        print(f"  - cocktails_scenario: {scenario_count} 筆")
        
        # 測試查詢
        print("\n測試查詢...")
        query_text = "清爽酸甜的調酒"
        query_vector = self.model.encode(query_text).tolist()
        
        results = self.qdrant.search(
            collection_name="cocktails_taste",
            query_vector=query_vector,
            limit=3
        )
        
        print(f"\n查詢: '{query_text}'")
        print("結果:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.payload['name']} (相似度: {result.score:.3f})")
        
        print("\n✓ 驗證完成！")
    
    def cleanup(self):
        """清理資源"""
        self.mongo_client.close()


def main():
    try:
        # 初始化
        setup = RAGSetup()
        
        # 建立集合
        setup.create_collections()
        
        # 向量化並存入
        setup.vectorize_and_store()
        
        # 驗證
        setup.verify_setup()
        
        # 清理
        setup.cleanup()
        
        print("\n" + "=" * 60)
        print("🎉 RAG 設定完成！")
        print("=" * 60)
        
        print("\n下一步:")
        print("1. 啟動應用: python run.py")
        print("2. 測試新 API: POST /api/chat/message")
        
        print("\n" + "=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠ 使用者中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()