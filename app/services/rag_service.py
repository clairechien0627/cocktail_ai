"""
RAG 服務（只使用 Qdrant）
提供向量搜尋功能
"""

from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


class RAGService:
    """RAG 向量搜尋服務（Qdrant Only）"""
    
    def __init__(self):
        self.model = None
        self.qdrant = None
    
    def initialize(self, qdrant_host: str, qdrant_port: int, embedding_model: str):
        """
        初始化 RAG 服務
        
        Args:
            qdrant_host: Qdrant 主機位址
            qdrant_port: Qdrant 端口
            embedding_model: Embedding 模型名稱
        """
        # 載入 Embedding 模型
        self.model = SentenceTransformer(embedding_model)
        
        # 連接 Qdrant
        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        # 測試連線
        self.qdrant.get_collections()
        print(f"✓ RAG Service: 使用 Qdrant ({qdrant_host}:{qdrant_port})")
    
    def search_by_taste(
        self, 
        query: str, 
        limit: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """
        根據口味描述搜尋調酒（語義搜尋）
        
        Args:
            query: 口味描述（如："清爽酸甜的"）
            limit: 返回結果數量
            min_score: 最低相似度分數
            
        Returns:
            符合口味的調酒列表
        """
        # 生成查詢向量
        query_vector = self.model.encode(query).tolist()
        
        # 搜尋 Qdrant
        results = self.qdrant.search(
            collection_name="cocktails_taste",
            query_vector=query_vector,
            limit=limit,
            score_threshold=min_score
        )
        
        # 格式化結果
        cocktails = []
        for result in results:
            cocktail = result.payload.copy()
            cocktail['similarity_score'] = result.score
            cocktails.append(cocktail)
        
        return cocktails
    
    def search_by_scenario(
        self, 
        query: str, 
        limit: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """
        根據場景描述搜尋調酒（語義搜尋）
        
        Args:
            query: 場景描述（如："慶祝用的"、"約會時喝"）
            limit: 返回結果數量
            min_score: 最低相似度分數
            
        Returns:
            適合場景的調酒列表
        """
        # 生成查詢向量
        query_vector = self.model.encode(query).tolist()
        
        # 搜尋 Qdrant
        results = self.qdrant.search(
            collection_name="cocktails_scenario",
            query_vector=query_vector,
            limit=limit,
            score_threshold=min_score
        )
        
        # 格式化結果
        cocktails = []
        for result in results:
            cocktail = result.payload.copy()
            cocktail['similarity_score'] = result.score
            cocktails.append(cocktail)
        
        return cocktails
    
    def health_check(self) -> Dict[str, str]:
        """
        健康檢查
        
        Returns:
            服務狀態
        """
        try:
            # 檢查 Qdrant 連接
            collections = self.qdrant.get_collections()
            
            # 檢查集合是否存在
            collection_names = [c.name for c in collections.collections]
            
            taste_exists = "cocktails_taste" in collection_names
            scenario_exists = "cocktails_scenario" in collection_names
            
            if taste_exists and scenario_exists:
                # 檢查集合數量
                taste_count = self.qdrant.count("cocktails_taste").count
                scenario_count = self.qdrant.count("cocktails_scenario").count
                
                return {
                    'status': 'healthy',
                    'database': 'Qdrant',
                    'collections': {
                        'taste': taste_count,
                        'scenario': scenario_count
                    }
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Collections not found. Please run setup_rag.py'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

# ============== 建立全域實例 ==============
rag_service = RAGService()