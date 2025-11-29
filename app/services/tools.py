"""
LangGraph 工具函數（改進版）
提供 7 個工具供 Agent 使用，使用清晰的描述和 Pydantic schema
"""

from typing import List, Optional, Dict, Any
from langchain.tools import tool
from pydantic import BaseModel, Field
from flask import current_app


# ========== Pydantic Models ==========

class SearchByNameInput(BaseModel):
    """名稱搜尋輸入"""
    name: str = Field(description="調酒名稱，例如：Mojito、Margarita")


class SearchByIngredientsInput(BaseModel):
    """材料搜尋輸入"""
    ingredients: List[str] = Field(
        description="材料列表，例如：['vodka', 'lime juice']"
    )
    match_mode: str = Field(
        default="any",
        description="匹配模式：'all'=必須包含所有材料，'any'=包含任一材料即可"
    )


class FilterByAttributesInput(BaseModel):
    """屬性篩選輸入"""
    min_strength: Optional[int] = Field(
        default=None,
        description="最低酒精強度 (0-5)"
    )
    max_strength: Optional[int] = Field(
        default=None,
        description="最高酒精強度 (0-5)"
    )
    min_sweetness: Optional[int] = Field(
        default=None,
        description="最低甜度 (0-5)"
    )
    max_sweetness: Optional[int] = Field(
        default=None,
        description="最高甜度 (0-5)"
    )
    difficulty: Optional[str] = Field(
        default=None,
        description="難度：'easy'、'medium'、'hard'"
    )
    max_calories: Optional[int] = Field(
        default=None,
        description="最高卡路里"
    )
    category: Optional[str] = Field(
        default=None,
        description="分類，例如：'Gin Cocktails'、'Vodka Cocktails'"
    )
    min_rating: Optional[float] = Field(
        default=None,
        description="最低評分 (0-5)"
    )


class SearchByTasteInput(BaseModel):
    """口味語義搜尋輸入"""
    query: str = Field(
        description="口味描述，例如：'清爽酸甜的'、'濃烈的'、'甜甜的適合女生'"
    )
    limit: int = Field(
        default=5,
        description="返回結果數量"
    )


class SearchByScenarioInput(BaseModel):
    """場景語義搜尋輸入"""
    query: str = Field(
        description="場景描述，例如：'慶祝用的'、'約會時喝'、'適合夏天海邊'"
    )
    limit: int = Field(
        default=5,
        description="返回結果數量"
    )


class SearchByCategoryInput(BaseModel):
    """分類搜尋輸入"""
    category: str = Field(
        description="調酒分類，例如：'Gin Cocktails'、'Vodka Cocktails'、'Tequila Cocktails'"
    )
    limit: int = Field(
        default=5,
        description="返回結果數量"
    )


# ========== 工具定義 ==========

@tool(args_schema=SearchByNameInput)
def search_by_name(name: str) -> Dict[str, Any]:
    """
    根據調酒名稱搜尋完整配方和資訊。
    
    使用時機：
    - 用戶想知道特定調酒的做法，例如："Mojito 怎麼做？"
    - 用戶詢問特定調酒的資訊，例如："告訴我 Margarita 的配方"
    
    Returns:
        包含完整配方、材料、步驟、評分等資訊的調酒資料
    """
    db = current_app.config['DB']
    
    cocktail = db.cocktails.find_one({
        'name': {'$regex': name, '$options': 'i'}
    })
    
    if not cocktail:
        return {'error': f'找不到名為 "{name}" 的調酒'}
    
    cocktail['_id'] = str(cocktail['_id'])
    return cocktail


@tool(args_schema=SearchByIngredientsInput)
def search_by_ingredients(
    ingredients: List[str], 
    match_mode: str = "any"
) -> List[Dict[str, Any]]:
    """
    根據材料搜尋調酒。
    
    使用時機：
    - 用戶提到手上有某些材料，例如："我有伏特加和檸檬汁，可以做什麼？"
    - 用戶想要包含特定材料的調酒，例如："有什麼琴酒的調酒？"
    
    Returns:
        符合材料條件的調酒列表（最多5個，按評分排序）
    """
    db = current_app.config['DB']
    
    if match_mode == "all":
        query = {
            '$and': [
                {'ingredients': {'$regex': ing, '$options': 'i'}}
                for ing in ingredients
            ]
        }
    else:
        query = {
            '$or': [
                {'ingredients': {'$regex': ing, '$options': 'i'}}
                for ing in ingredients
            ]
        }
    
    cocktails = list(
        db.cocktails.find(query)
        .sort('ratings.professional', -1)
        .limit(5)
    )
    
    for cocktail in cocktails:
        cocktail['_id'] = str(cocktail['_id'])
    
    if not cocktails:
        return [{'message': f'找不到包含 {ingredients} 的調酒'}]
    
    return cocktails


@tool(args_schema=FilterByAttributesInput)
def filter_by_attributes(
    min_strength: Optional[int] = None,
    max_strength: Optional[int] = None,
    min_sweetness: Optional[int] = None,
    max_sweetness: Optional[int] = None,
    difficulty: Optional[str] = None,
    max_calories: Optional[int] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    根據多個屬性篩選調酒（強度、甜度、難度、卡路里、評分等）。
    
    使用時機：
    - 用戶提到特定條件，例如："簡單的調酒"、"低卡路里的"、"高評分的"
    - 用戶想要特定強度或甜度，例如："濃一點的"、"甜一點的"
    
    Returns:
        符合篩選條件的調酒列表（最多10個，按評分排序）
    """
    db = current_app.config['DB']
    
    query = {}
    
    if min_strength is not None or max_strength is not None:
        query['taste_profile.strength'] = {}
        if min_strength is not None:
            query['taste_profile.strength']['$gte'] = min_strength
        if max_strength is not None:
            query['taste_profile.strength']['$lte'] = max_strength
    
    if min_sweetness is not None or max_sweetness is not None:
        query['taste_profile.sweetness'] = {}
        if min_sweetness is not None:
            query['taste_profile.sweetness']['$gte'] = min_sweetness
        if max_sweetness is not None:
            query['taste_profile.sweetness']['$lte'] = max_sweetness
    
    if difficulty:
        query['difficulty'] = difficulty
    
    if max_calories:
        query['nutritional_info.calories'] = {'$lte': max_calories}
    
    if category:
        query['category'] = {'$regex': category, '$options': 'i'}
    
    if min_rating:
        query['ratings.professional'] = {'$gte': min_rating}
    
    cocktails = list(
        db.cocktails.find(query)
        .sort('ratings.professional', -1)
        .limit(10)
    )
    
    for cocktail in cocktails:
        cocktail['_id'] = str(cocktail['_id'])
    
    if not cocktails:
        return [{'message': '找不到符合條件的調酒'}]
    
    return cocktails


@tool(args_schema=SearchByTasteInput)
def search_by_taste_semantic(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    使用 AI 語義搜尋根據口味描述找調酒（需要 RAG 功能）。
    
    使用時機：
    - 用戶描述口味感受，例如："清爽酸甜的"、"濃烈苦澀的"、"果香味重的"
    - 用戶用形容詞描述想要的味道，例如："refreshing"、"sweet and fruity"
    
    Returns:
        口味相似的調酒列表（按相似度排序）
    """
    try:
        from app.services.rag_service import rag_service
        
        if not rag_service.model:
            return [{'error': 'RAG 服務未初始化'}]
        
        results = rag_service.search_by_taste(query, limit=limit)
        return results
        
    except Exception as e:
        return [{'error': f'語義搜尋失敗: {str(e)}'}]


@tool(args_schema=SearchByScenarioInput)
def search_by_scenario_semantic(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    使用 AI 語義搜尋根據場景描述找調酒（需要 RAG 功能）。
    
    使用時機：
    - 用戶提到場景或情境，例如："慶祝用的"、"約會時喝"、"派對上的"
    - 用戶提到季節或環境，例如："夏天海邊"、"冬天溫暖"、"辦公室下班後"
    
    Returns:
        適合場景的調酒列表（按相似度排序）
    """
    try:
        from app.services.rag_service import rag_service
        
        if not rag_service.model:
            return [{'error': 'RAG 服務未初始化'}]
        
        results = rag_service.search_by_scenario(query, limit=limit)
        return results
        
    except Exception as e:
        return [{'error': f'語義搜尋失敗: {str(e)}'}]


@tool(args_schema=SearchByCategoryInput)
def search_by_category(category: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    根據分類搜尋調酒。
    
    使用時機：
    - 用戶提到基酒或分類，例如："琴酒調酒"、"伏特加的"、"龍舌蘭類的"
    - 用戶詢問某種類型，例如："有什麼 Gin Cocktails？"
    
    Returns:
        該分類的調酒列表（最多限制數量，按評分排序）
    """
    db = current_app.config['DB']
    
    cocktails = list(
        db.cocktails.find({
            'category': {'$regex': category, '$options': 'i'}
        })
        .sort('ratings.professional', -1)
        .limit(limit)
    )
    
    for cocktail in cocktails:
        cocktail['_id'] = str(cocktail['_id'])
    
    if not cocktails:
        return [{'message': f'找不到 "{category}" 分類的調酒'}]
    
    return cocktails


@tool
def get_random_cocktail() -> Dict[str, Any]:
    """
    隨機推薦一款調酒。
    
    使用時機：
    - 用戶說"隨便"、"驚喜我"、"給我推薦一個"
    - 用戶沒有特定偏好，想要探索新選項
    
    Returns:
        隨機選擇的一款調酒
    """
    db = current_app.config['DB']
    
    # 使用 MongoDB 的 aggregate 隨機取樣
    pipeline = [{'$sample': {'size': 1}}]
    cocktails = list(db.cocktails.aggregate(pipeline))
    
    if not cocktails:
        return {'error': '資料庫中沒有調酒'}
    
    cocktail = cocktails[0]
    cocktail['_id'] = str(cocktail['_id'])
    
    return cocktail


# ========== 匯出所有工具 ==========
ALL_TOOLS = [
    search_by_name,
    search_by_ingredients,
    filter_by_attributes,
    search_by_taste_semantic,
    search_by_scenario_semantic,
    search_by_category,
    get_random_cocktail
]