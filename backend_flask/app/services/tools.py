"""
LangGraph 工具函數
提供 7 個工具供 Agent 使用，明確指定工具名稱和描述以提升相容性
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
        description="最低酒精強度 (0-10)"
    )
    max_strength: Optional[int] = Field(
        default=None,
        description="最高酒精強度 (0-10)"
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


# ========== 工具定義（加上自定義 name 和 description）==========

@tool(
    "search_by_name",
    args_schema=SearchByNameInput,
    description="""Search for a cocktail by its exact NAME (not ingredient name) to get complete recipe, ingredients, steps, and ratings.

Use this when the user asks about a specific COCKTAIL (drink) like:
- 'How to make a Mojito?'
- 'Tell me about Margarita'
- 'What is a Negroni?'

IMPORTANT: Some words can be both cocktail names AND ingredient names (e.g., 'Campari', 'Maraschino').
If unsure whether the user means a cocktail or an ingredient, try this tool first. If no results are found,
the word might actually refer to an ingredient, not a cocktail name."""
)
def search_by_name(name: str) -> Dict[str, Any]:
    """根據調酒名稱搜尋完整配方和資訊。"""
    db = current_app.config['DB']
    
    cocktail = db.cocktails.find_one({
        'name': {'$regex': name, '$options': 'i'}
    })
    
    if not cocktail:
        return {'error': f'找不到名為 "{name}" 的調酒'}
    
    cocktail['_id'] = str(cocktail['_id'])
    return cocktail


@tool(
    "search_by_ingredients",
    args_schema=SearchByIngredientsInput,
    description="""Search for cocktails that CONTAIN specific ingredients (like vodka, gin, rum, Campari, Maraschino liqueur, lime juice, etc.).

Use this when the user wants to find cocktails that include these ingredients:
- 'I have vodka and lime juice, what can I make?'
- 'Show me gin cocktails'
- 'Cocktails with Campari'
- 'What can I make with rum?'
- 'Drinks that use Maraschino liqueur'

NOTE: This searches for cocktails CONTAINING the ingredient, not cocktails NAMED after the ingredient.
For example, searching 'Campari' here will find cocktails like Negroni (which contains Campari),
not a cocktail called 'Campari'."""
)
def search_by_ingredients(
    ingredients: List[str], 
    match_mode: str = "any"
) -> List[Dict[str, Any]]:
    """根據材料搜尋調酒。"""
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


@tool(
    "filter_by_attributes",
    args_schema=FilterByAttributesInput,
    description="Filter cocktails by multiple attributes like strength, sweetness, difficulty, calories, category, and rating. Use this when the user specifies preferences (e.g., 'easy cocktails', 'low calorie', 'high rated', 'strong drinks', 'sweet cocktails')."
)
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
    """根據多個屬性篩選調酒。"""
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


@tool(
    "search_by_taste_semantic",
    args_schema=SearchByTasteInput,
    description="Use AI semantic search to find cocktails based on taste descriptions. Use this when the user describes taste preferences with adjectives (e.g., 'refreshing and sour', 'strong and bitter', 'sweet and fruity', 'light and crisp'). Requires RAG service."
)
def search_by_taste_semantic(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """使用 AI 語義搜尋根據口味描述找調酒。"""
    try:
        from app.services.rag_service import rag_service

        if not rag_service.model:
            return [{'error': 'RAG 服務未初始化'}]

        # 調整 limit 並提高相似度閾值以提高準確度
        results = rag_service.search_by_taste(query, limit=limit, min_score=0.65)
        return results
        
    except Exception as e:
        return [{'error': f'語義搜尋失敗: {str(e)}'}]


@tool(
    "search_by_scenario_semantic",
    args_schema=SearchByScenarioInput,
    description="Use AI semantic search to find cocktails based on scenarios and occasions. Use this when the user mentions situations (e.g., 'celebration drinks', 'date night', 'party cocktails'), seasons (e.g., 'summer beach', 'winter warmth'), or contexts (e.g., 'after work drinks'). Requires RAG service."
)
def search_by_scenario_semantic(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """使用 AI 語義搜尋根據場景描述找調酒。"""
    try:
        from app.services.rag_service import rag_service

        if not rag_service.model:
            return [{'error': 'RAG 服務未初始化'}]

        # 調整 limit 並提高相似度閾值以提高準確度
        results = rag_service.search_by_scenario(query, limit=limit, min_score=0.65)
        return results
        
    except Exception as e:
        return [{'error': f'語義搜尋失敗: {str(e)}'}]


@tool(
    "search_by_category",
    args_schema=SearchByCategoryInput,
    description="Search for cocktails by their category or base spirit. Use this when the user asks about specific types (e.g., 'gin cocktails', 'vodka drinks', 'tequila based', 'whiskey cocktails', 'rum drinks')."
)
def search_by_category(category: str, limit: int = 5) -> List[Dict[str, Any]]:
    """根據分類搜尋調酒。"""
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


@tool(
    "get_random_cocktail",
    description="Get a random cocktail recommendation. Use this when the user says 'surprise me', 'random', 'anything', 'I don't care', or wants to explore without specific preferences."
)
def get_random_cocktail() -> Dict[str, Any]:
    """隨機推薦一款調酒。"""
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

