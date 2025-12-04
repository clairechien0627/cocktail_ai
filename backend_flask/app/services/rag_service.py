"""
RAG 服務（只使用 Qdrant）
提供向量搜尋功能（新版 Qdrant API）
"""

from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

class RAGService:
    """RAG 向量搜尋服務（Qdrant Only, Updated API）"""

    def __init__(self):
        self.model = None
        self.qdrant = None

    def initialize(self, qdrant_host: str, qdrant_port: int, embedding_model: str):
        """
        初始化 RAG 服務
        """
        # Embedding
        self.model = SentenceTransformer(embedding_model)

        # Qdrant
        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)

        # Test connection
        self.qdrant.get_collections()
        print(f"✓ RAG Service: 使用 Qdrant ({qdrant_host}:{qdrant_port})")

    # --------------------------------------------------------
    # 搜尋：口味語義搜尋（Taste）
    # --------------------------------------------------------
    def search_by_taste(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """使用語義搜尋找口味相似的調酒"""

        query_vector = self.model.encode(query).tolist()

        # ❗ 改為新版 query_points()
        response = self.qdrant.query_points(
            collection_name="cocktails_taste",
            query=query_vector,
            limit=limit
        )

        cocktails = []
        for point in response.points:
            if point.score < min_score:
                continue
            item = point.payload.copy()
            item["similarity_score"] = point.score
            cocktails.append(item)

        return cocktails

    # --------------------------------------------------------
    # 搜尋：場景語義搜尋（Scenario）
    # --------------------------------------------------------
    def search_by_scenario(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """使用語義搜尋找適合情境的調酒"""

        query_vector = self.model.encode(query).tolist()

        response = self.qdrant.query_points(
            collection_name="cocktails_scenario",
            query=query_vector,
            limit=limit
        )

        cocktails = []
        for point in response.points:
            if point.score < min_score:
                continue
            item = point.payload.copy()
            item["similarity_score"] = point.score
            cocktails.append(item)

        return cocktails

    # --------------------------------------------------------
    # 健康檢查（新版 count API）
    # --------------------------------------------------------
    def health_check(self) -> Dict[str, str]:
        """檢查 Qdrant 是否正常運作"""
        try:
            collections = self.qdrant.get_collections()
            names = [c.name for c in collections.collections]

            if not ("cocktails_taste" in names and "cocktails_scenario" in names):
                return {"status": "error", "message": "Collections not found. Please run setup_rag.py"}

            # ❗ 新版 count API
            taste_count = self.qdrant.count(collection_name="cocktails_taste").count
            scenario_count = self.qdrant.count(collection_name="cocktails_scenario").count

            return {
                "status": "healthy",
                "database": "Qdrant",
                "collections": {
                    "taste": taste_count,
                    "scenario": scenario_count
                }
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}


# =============== 建立全域實例 ===============
rag_service = RAGService()
