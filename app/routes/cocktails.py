from flask import Blueprint, request, jsonify
from flask_cors import CORS
from bson.objectid import ObjectId
from app.models import Cocktail

cocktails_bp = Blueprint("cocktails", __name__, url_prefix="/api/cocktails")

# 讓這個 blueprint 支援跨域
CORS(
    cocktails_bp,
    resources={r"/api/*": {"origins": ["http://localhost:5173"]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)


def merge_cocktail_with_zh(db, doc):
    """doc 來自 db.cocktails，只合併 cocktails_zh 的段落型中文欄位"""
    cocktail = dict(doc)
    cocktail["_id"] = str(cocktail["_id"])
    cocktail["image_url"] = cocktail.get("image_url") or cocktail.get("image")

    cocktail_id = cocktail.get("cocktail_id") or cocktail.get("slug")
    if not cocktail_id:
        return cocktail

    zh = db.cocktails_zh.find_one({"cocktail_id": cocktail_id})
    if not zh:
        return cocktail

    zh = dict(zh)
    cocktail.update({
        "name_en": zh.get("name_en") or cocktail.get("name"),
        "name_zh": zh.get("name_zh"),
        "review_zh": zh.get("review_zh"),
        "history_zh": zh.get("history_zh"),
        "method_sections_zh": zh.get("method_sections_zh"),
    })
    return cocktail

def enrich_with_trans_tables(db, cocktail):
    """
    根據英文欄位，動態查各個 *_trans collection 產生 *_zh 欄位。
    不改變資料庫，只改變這次回傳的 dict。
    """
    c = dict(cocktail)

    # 1) 杯具 glass -> glass_zh
    glass_en = c.get("glass")
    if glass_en:
        trans = db.glass_trans.find_one({"name_en": glass_en})
        if trans and trans.get("name_zh"):
            c["glass_zh"] = trans["name_zh"]

    # 2) more_categories -> more_categories_zh[]
    if c.get("more_categories"):
        zh_list = []
        for cat in c["more_categories"]:
            tr = db.more_categories_trans.find_one({"name_en": cat})
            zh_list.append(tr["name_zh"] if tr and tr.get("name_zh") else cat)
        c["more_categories_zh"] = zh_list

    # 3) 材料 ingredients_detail / ingredients -> ingredients_zh[]
    zh_ings: list[str | None] = []

    # 先處理 ingredients_detail，保證和 detail 一一對應
    details = c.get("ingredients_detail") or []
    if isinstance(details, list) and details:
        for detail in details:
            ing_en = (detail or {}).get("ingredient")
            if not ing_en:
                zh_ings.append(None)
                continue

            tr = db.ingredients_trans.find_one({"name_en": ing_en})
            zh_ings.append(tr.get("name_zh") if tr and tr.get("name_zh") else None)

    # 再處理 ingredients 陣列：如果有多出來的項目，也給它翻譯
    ings = c.get("ingredients") or []
    if isinstance(ings, list) and ings:
        # 若 zh_ings 比 ingredients 少，就依序補上
        for idx, ing_en in enumerate(ings):
            if not isinstance(ing_en, str):
                continue

            # 若對應位置已經有翻譯，就跳過
            if idx < len(zh_ings) and zh_ings[idx] is not None:
                continue

            tr = db.ingredients_trans.find_one({"name_en": ing_en})
            zh_name = tr.get("name_zh") if tr and tr.get("name_zh") else None

            if idx < len(zh_ings):
                # 覆寫 / 補上這一格
                if zh_name is not None:
                    zh_ings[idx] = zh_name
            else:
                # ingredients 比 ingredients_detail 還多，往後 append
                zh_ings.append(zh_name)

    if zh_ings:
        c["ingredients_zh"] = zh_ings


    # 4) 過敏原 allergens -> 動態加 item_zh / allergen_zh
    if c.get("allergens"):
        enriched_allergens = []
        for a in c["allergens"]:
            a = dict(a)
            item_en = a.get("item")
            allergen_en = a.get("allergen")

            if item_en:
                tr_item = db.allergens_item_trans.find_one({"name_en": item_en})
                if tr_item and tr_item.get("name_zh"):
                    a["item_zh"] = tr_item["name_zh"]

            if allergen_en:
                tr_name = db.allergens_name_trans.find_one({"name_en": allergen_en})
                if tr_name and tr_name.get("name_zh"):
                    a["allergen_zh"] = tr_name["name_zh"]

            enriched_allergens.append(a)

        c["allergens"] = enriched_allergens

    # category -> category_zh
    cat = c.get("category")
    if cat:
        tr = db.categories_trans.find_one({"name_en": cat})
        if tr and tr.get("name_zh"):
            c["category_zh"] = tr["name_zh"]


    return c



# 專門給瀏覽器預檢用的 OPTIONS 路由：注意是 cktail_id>
@cocktails_bp.route("/cktail_id>", methods=["OPTIONS"])
def preflight_cocktail(cocktail_id):
    return "", 200


@cocktails_bp.route("/", methods=["GET"])
def get_all_cocktails():
    try:
        from flask import current_app
        db = current_app.config["DB"]

        lang = request.args.get("lang", "en")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        skip = (page - 1) * limit

        docs = list(db.cocktails.find().skip(skip).limit(limit))

        cocktails = []
        for doc in docs:
            base = merge_cocktail_with_zh(db, doc)  # 先合併段落中文
            enriched = enrich_with_trans_tables(db, base)  # 再查對照表產生 *_zh
            cocktails.append(enriched)

        total = db.cocktails.count_documents({})

        return jsonify({
            "cocktails": cocktails,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# 詳情 API：注意路由一定要是 "/cktail_id>"
@cocktails_bp.route("/cktail_id>", methods=["GET", "OPTIONS"])
def get_cocktail(cocktail_id):
    if request.method == "OPTIONS":
        return "", 200

    try:
        from flask import current_app
        db = current_app.config["DB"]

        doc = db.cocktails.find_one({"_id": ObjectId(cocktail_id)})
        if not doc:
            return jsonify({"error": "調酒不存在"}), 404

        base = merge_cocktail_with_zh(db, doc)
        cocktail = enrich_with_trans_tables(db, base)

        return jsonify({"cocktail": cocktail}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@cocktails_bp.route("/category/ategory>", methods=["GET"])
def get_cocktails_by_category(category):
    """根據分類取得調酒"""
    try:
        from flask import current_app

        db = current_app.config["DB"]

        cocktails = Cocktail.find_by_category(db, category)

        # 轉換 ObjectId 為字串
        for cocktail in cocktails:
            cocktail["_id"] = str(cocktail["_id"])

        return (
            jsonify(
                {
                    "cocktails": cocktails,
                    "category": category,
                    "count": len(cocktails),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocktails_bp.route("/categories", methods=["GET"])
def get_categories():
    """取得所有分類"""
    try:
        from flask import current_app

        db = current_app.config["DB"]

        categories = db.cocktails.distinct("category")
        return jsonify({"categories": categories}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocktails_bp.route("/more-categories", methods=["GET"])
def get_more_categories():
    """取得所有 more_categories"""
    try:
        from flask import current_app

        db = current_app.config["DB"]

        pipeline = [
            {"$unwind": "$more_categories"},
            {"$group": {"_id": "$more_categories"}},
            {"$sort": {"_id": 1}},
        ]

        result = list(db.cocktails.aggregate(pipeline))
        more_categories = [item["_id"] for item in result if item.get("_id")]

        return jsonify({"more_categories": more_categories}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocktails_bp.route("/random", methods=["GET"])
def get_random_cocktail():
    """隨機取得一個調酒"""
    try:
        from flask import current_app

        db = current_app.config["DB"]

        cocktails = list(db.cocktails.aggregate([{"$sample": {"size": 1}}]))

        if not cocktails:
            return jsonify({"error": "沒有調酒資料"}), 404

        cocktail = cocktails[0]
        cocktail["_id"] = str(cocktail["_id"])

        return jsonify({"cocktail": cocktail}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocktails_bp.route("/filter", methods=["GET"])
def filter_cocktails():
    """進階篩選調酒"""
    try:
        from flask import current_app

        db = current_app.config["DB"]

        filters = {}

        # 評分篩選
        if request.args.get("min_rating"):
            filters["min_rating"] = request.args.get("min_rating")
        if request.args.get("max_rating"):
            filters["max_rating"] = request.args.get("max_rating")

        # 風味篩選
        if request.args.get("min_strength"):
            filters["min_strength"] = request.args.get("min_strength")
        if request.args.get("max_strength"):
            filters["max_strength"] = request.args.get("max_strength")
        if request.args.get("min_sweetness"):
            filters["min_sweetness"] = request.args.get("min_sweetness")
        if request.args.get("max_sweetness"):
            filters["max_sweetness"] = request.args.get("max_sweetness")

        # 其他篩選
        if request.args.get("max_calories"):
            filters["max_calories"] = request.args.get("max_calories")
        if request.args.get("difficulty"):
            filters["difficulty"] = request.args.get("difficulty")
        if request.args.get("category"):
            filters["category"] = request.args.get("category")
        if request.args.get("more_category"):
            filters["more_category"] = request.args.get("more_category")
        if request.args.get("has_history") == "true":
            filters["has_history"] = True

        # Tag 篩選（新增）
        if request.args.get('tags'):
            # 支援逗號分隔的多個 tags
            filters['tags'] = request.args.get('tags').split(',')
        if request.args.get('base_spirit'):
            filters['base_spirit'] = request.args.get('base_spirit')
        if request.args.get('flavor'):
            # 支援逗號分隔的多個 flavors
            flavor_str = request.args.get('flavor')
            filters['flavor'] = flavor_str.split(',') if ',' in flavor_str else flavor_str
        if request.args.get('ingredient_tag'):
            filters['ingredient_tag'] = request.args.get('ingredient_tag')
        if request.args.get('style'):
            # 支援逗號分隔的多個 styles
            style_str = request.args.get('style')
            filters['style'] = style_str.split(',') if ',' in style_str else style_str

        # 分頁參數
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        skip = (page - 1) * limit

        # 排序方式
        sort_by = request.args.get("sort_by", "name")

        cocktails, total_count = Cocktail.filter_cocktails(
            db, filters, skip, limit, sort_by
        )

        # 在這裡把每一筆跟中文 collection merge 起來
        cocktails = [enrich_with_trans_tables(db, merge_cocktail_with_zh(db, c)) for c in cocktails]

        return (
            jsonify(
                {
                    "cocktails": cocktails,
                    "count": total_count,
                    "page": page,
                    "limit": limit,
                    "total_pages": (total_count + limit - 1) // limit,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocktails_bp.route("/stats", methods=["GET"])
def get_statistics():
    """取得調酒統計資訊"""
    try:
        from flask import current_app

        db = current_app.config["DB"]

        stats = Cocktail.get_statistics(db)

        return (
            jsonify(
                {
                    "total_cocktails": stats.get("total", 0),
                    "average_rating": round(stats.get("avg_rating", 0), 2)
                    if stats.get("avg_rating")
                    else 0,
                    "categories": stats.get("categories", []),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocktails_bp.route("/search", methods=["GET"])
def search_cocktails():
    """搜尋調酒（依名稱或材料）"""
    try:
        from flask import current_app
        db = current_app.config["DB"]

        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"cocktails": [], "count": 0}), 200

        # 建立搜尋條件（不區分大小寫）
        search_pattern = {"$regex": query, "$options": "i"}
        filter_query = {
            "$or": [
                {"name": search_pattern},
                {"ingredients": search_pattern},
                {"category": search_pattern},
            ]
        }

        # 執行搜尋
        cocktails = list(db.cocktails.find(filter_query).limit(100))

        # 合併中文資料
        cocktails = [enrich_with_trans_tables(db, merge_cocktail_with_zh(db, c)) for c in cocktails]


        return jsonify({"cocktails": cocktails, "count": len(cocktails)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocktails_bp.route("/tags", methods=["GET"])
def get_all_tags():
    """取得所有可用的 tags（分類顯示）

    返回四個維度的所有 tags：
    - base_spirits: 基酒類型
    - flavors: 風味特徵
    - ingredients: 主要材料
    - styles: 風格/類型
    """
    try:
        from flask import current_app
        db = current_app.config["DB"]

        # 收集所有 tags
        all_tags = {
            "base_spirits": set(),
            "flavors": set(),
            "ingredients": set(),
            "styles": set()
        }

        # 遍歷所有調酒收集 tags
        cocktails = db.cocktails.find({}, {"tags_categorized": 1})
        for cocktail in cocktails:
            tags_cat = cocktail.get("tags_categorized", {})
            for category, tags in tags_cat.items():
                if isinstance(tags, list):
                    all_tags[category].update(tags)

        # 轉換為排序列表
        result = {k: sorted(list(v)) for k, v in all_tags.items()}

        # 統計每個 tag 的數量
        tag_counts = {}
        for category in ["base_spirits", "flavors", "ingredients", "styles"]:
            tag_counts[category] = {}
            for tag in result[category]:
                count = db.cocktails.count_documents({f"tags_categorized.{category}": tag})
                tag_counts[category][tag] = count

        return jsonify({
            "tags": result,
            "counts": tag_counts
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
