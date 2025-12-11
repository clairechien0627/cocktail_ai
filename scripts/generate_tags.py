"""
調酒 Tag 自動生成器

功能：
- 為所有調酒自動生成易懂的 tags
- 四個維度：基酒類型、風味特徵、主要材料、風格/類型
- 面向調酒初學者，使用簡單易懂的詞彙
"""

import json
import os
import sys
from typing import List, Dict, Set
from collections import Counter

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CocktailTagGenerator:
    """調酒 Tag 自動生成器"""

    def __init__(self):
        """初始化 Tag 映射規則"""

        # 維度一：基酒類型映射
        self.BASE_SPIRIT_MAPPING = {
            'gin': {
                'keywords': ['gin'],
                'exclude_keywords': ['ginger', 'ginseng']
            },
            'vodka': {
                'keywords': ['vodka']
            },
            'rum': {
                'keywords': ['rum', 'rhum', 'ron'],
                'exclude_keywords': ['rumchata']  # 避免誤判 RumChata (cream liqueur)
            },
            'tequila': {
                'keywords': ['tequila']
            },
            'whiskey': {
                'keywords': ['whisky', 'whiskey', 'bourbon', 'rye whiskey', 'scotch', 'irish whiskey']
            },
            'brandy': {
                'keywords': ['brandy', 'cognac', 'armagnac', 'calvados', 'grappa']
            },
            'mezcal': {
                'keywords': ['mezcal']
            },
            'cachaca': {
                'keywords': ['cachaça', 'cachaca']
            },
            'pisco': {
                'keywords': ['pisco']
            },
            'genever': {
                'keywords': ['genever', 'oude genever', 'jonge genever']
            },
            'non-alcoholic': {
                'keywords': ['non-alcoholic', 'non alcoholic', 'alcohol-free', 'alcohol free']
            }
        }

        # 維度二：風味特徵映射
        self.FLAVOR_MAPPING = {
            'citrusy': {
                'required_ingredients': [
                    'lime juice', 'lemon juice', 'orange juice',
                    'grapefruit juice', 'citrus', 'yuzu', 'mandarin'
                ],
                'more_categories': ['Citrusy cocktails', 'Sours (citrus) cocktails']
            },
            'fruity': {
                'keywords': [
                    'fruit', 'berry', 'peach', 'mango', 'pineapple',
                    'passion fruit', 'strawberry', 'raspberry', 'blackberry',
                    'blueberry', 'watermelon', 'melon', 'apple', 'pear',
                    'banana', 'apricot', 'plum', 'cherry', 'kiwi'
                ],
                'more_categories': ['Fruity (e.g. Pornstar Martini) cocktails', 'Fruitini cocktails']
            },
            'bittersweet': {
                'required_ingredients': [
                    'campari', 'red bitter liqueur', 'aperol', 'amaro',
                    'cynar', 'fernet', 'ramazotti', 'averna', 'montenegro',
                    'bittersweet', 'bitter liqueur'
                ],
                'more_categories': ['Bittersweet (e.g. Negroni) cocktails']
            },
            'creamy': {
                'keywords': [
                    'cream', 'milk', 'coconut cream', 'irish cream',
                    'cream liqueur', 'half-and-half', 'evaporated milk',
                    'condensed milk', 'heavy cream'
                ],
                'more_categories': ['Creamy (e.g. Dirty banana) cocktails']
            },
            'herbal': {
                'keywords': [
                    'mint', 'basil', 'thyme', 'rosemary', 'absinthe',
                    'chartreuse', 'benedictine', 'bénédictine', 'herbal',
                    'sage', 'cilantro', 'coriander', 'dill', 'tarragon', 'herbal'
                ],
                'more_categories': ['Herbal cocktails']
            },
            'floral': {
                'keywords': [
                    'elderflower', 'rose', 'lavender', 'violet',
                    'hibiscus', 'chamomile', 'jasmine', 'orange blossom',
                    'cherry blossom'
                ],
                'more_categories': ['Floral (e.g. Elderflower spritz) cocktails']
            },
            'spicy': {
                'keywords': [
                    'ginger', 'cinnamon', 'chili', 'pepper', 'spice',
                    'allspice', 'cardamom', 'clove', 'nutmeg', 'jalapeño',
                    'habanero', 'cayenne', 'tabasco'
                ],
                'more_categories': ['Spicy (e.g. Spicy Fifty) cocktails']
            },
            'minty': {
                'keywords': [
                    'mint', 'peppermint', 'creme de menthe', 'mint leaves',
                    'spearmint'
                ]
            },
            'coffee': {
                'keywords': [
                    'coffee', 'espresso', 'coffee liqueur', 'kahlua',
                    'mr black', 'tia maria'
                ]
            },
            'chocolate': {
                'keywords': [
                    'chocolate', 'cacao', 'cocoa', 'chocolate liqueur',
                    'creme de cacao', 'dark chocolate', 'white chocolate'
                ]
            },
            'nutty': {
                'keywords': [
                    'amaretto', 'orgeat', 'hazelnut', 'almond',
                    'pistachio', 'walnut', 'pecan', 'peanut', 'nut',
                    'frangelico', 'nocino'
                ],
                'more_categories': ['Nutty cocktails']
            },
            'smoky': {
                'keywords': [
                    'peated', 'mezcal', 'smoked', 'lapsang', 'smoky',
                    'smoke', 'charred'
                ]
            },
            'tropical': {
                'keywords': [
                    'pineapple', 'coconut', 'mango', 'passion fruit',
                    'guava', 'papaya', 'banana', 'tropical'
                ],
                'more_categories': ['Tiki/tropical cocktails']
            },
            'berry': {
                'keywords': [
                    'raspberry', 'strawberry', 'blackberry', 'blueberry',
                    'cranberry', 'gooseberry', 'elderberry', 'boysenberry'
                ]
            },
            'peachy': {
                'keywords': [
                    'peach', 'apricot', 'nectarine', 'peach schnapps',
                    'apricot liqueur'
                ]
            },
            'vanilla': {
                'keywords': [
                    'vanilla', 'vanilla vodka', 'vanilla syrup', 'vanilla liqueur',
                    'vanilla extract', 'vanilia'
                ]
            },
            'savory': {
                'keywords': [
                    'tomato', 'celery', 'worcestershire', 'soy sauce',
                    'olive', 'pickle', 'savory', 'savoury', 'umami',
                    'bacon', 'cheese'
                ],
                'more_categories': ['Savoury (e.g. Bloody Mary) cocktails']
            }
        }

        # 維度三：主要材料 Tags 映射
        self.INGREDIENT_TAGS_MAPPING = {
            # 柑橘類
            'lemon': ['lemon juice', 'lemon', 'fresh lemon', 'lemonade'],
            'lime': ['lime juice', 'lime', 'fresh lime', 'lime (fresh)'],
            'orange': ['orange juice', 'orange', 'blood orange', 'fresh orange'],
            'grapefruit': ['grapefruit juice', 'pink grapefruit', 'grapefruit'],

            # 利口酒類
            'triple-sec': ['triple sec', 'cointreau', 'curaçao', 'curacao', 'grand marnier'],
            'campari': ['campari', 'red bitter liqueur'],
            'elderflower': ['elderflower liqueur', 'st-germain', 'st germain', 'elderflower'],
            'absinthe': ['absinthe', 'absinth'],
            'chartreuse': ['chartreuse green', 'chartreuse yellow', 'chartreuse'],
            'cherry-brandy': ['cherry brandy', 'cherry liqueur', 'maraschino', 'luxardo'],
            'amaretto': ['amaretto', 'disaronno'],
            'coffee-liqueur': ['coffee liqueur', 'kahlua', 'kahlúa', 'mr black', 'tia maria'],

            # 苦精類
            'aromatic-bitters': ['aromatic bitters', 'angostura bitters', 'angostura'],
            'orange-bitters': ['orange bitters'],

            # 鮮果/蔬菜
            'fresh-mint': ['mint leaves', 'fresh mint', 'mint sprig'],
            'basil': ['basil leaves', 'basil', 'fresh basil'],
            'raspberry': ['raspberry', 'raspberries', 'fresh raspberry'],

            # 糖漿
            'honey': ['honey', 'honey syrup', 'honey water'],
            'maple': ['maple syrup', 'maple'],
            'orgeat': ['orgeat', 'almond syrup'],
            'falernum': ['falernum', 'velvet falernum'],
            'grenadine': ['grenadine', 'pomegranate syrup'],

            # 其他
            'egg-white': ['egg white', 'pasteurised egg white', 'pasteurized egg white'],
            'soda-water': ['soda water', 'soda', 'club soda', 'sparkling water'],
            'tonic-water': ['tonic water', 'tonic'],
            'vermouth': ['vermouth', 'dry vermouth', 'sweet vermouth', 'rosso vermouth'],

            # 葡萄酒與啤酒
            'beer': ['beer', 'ale', 'lager', 'stout', 'porter', 'pilsner', 'bitter'],
            'white-wine': ['white wine', 'chardonnay', 'sauvignon blanc', 'riesling',
                          'pinot grigio', 'viognier', 'aligoté', 'grüner veltliner',
                          'soave', 'bourgogne'],
            'red-wine': ['red wine', 'claret', 'rioja', 'barolo', 'shiraz', 'merlot',
                        'cabernet', 'pinot noir', 'malbec', 'tempranillo'],
            'sparkling-wine': ['prosecco', 'cava', 'champagne', 'sparkling wine',
                              'rosé champagne', 'blanc de blancs', 'crémant'],
            'port': ['port', 'ruby port', 'tawny port', 'white port', 'porto'],

            # 特殊材料
            'ice-cream': ['ice cream', 'ice-cream', 'vanilla ice cream', 'gelato']
        }

        # 材料標籤的 more_categories 映射 (補充識別來源)
        self.INGREDIENT_MORE_CATEGORIES_MAPPING = {
            'champagne': ['Champagne cocktails'],
            'sparkling-wine': ['Champagne cocktails'],
            'beer': ['Beer Cocktails cocktails'],
            'ice-cream': ['Ice-cream cocktails cocktails']
        }

        # 維度四：風格/類型映射（基於 more_categories）
        self.STYLE_MAPPING = {
            # 經典系列
            'classic': ['Classic/vintage cocktails', 'classic'],
            'hall-of-fame': ['Hall of Fame & must know/try cocktails'],
            'contemporary': ['Contemporary classic cocktails'],

            # 調酒家族
            'martini': ['Martini-style cocktails'],
            'negroni': ['Bittersweet (e.g. Negroni) cocktails', 'Bittersweet cocktails'],
            'sour': ['Sours (citrus) cocktails'],
            'tiki': ['Tiki/tropical cocktails', 'Tiki cocktails'],
            'champagne': ['Champagne cocktails'],

            # 飲用時機
            'aperitif': ['Aperitivo/aperitif cocktails'],
            'digestif': ['After dinner/digestif cocktails', 'Digestif cocktails'],
            'nightcap': ['Nightcap/sipping cocktails'],
            'brunch': ['Breakfast/brunch cocktails'],
            'afternoon': ['Elevenses/afternoon cocktails'],
            'anytime': ['Anytime cocktails'],

            # 形式特徵
            'short-stirred': ['Short & stirred cocktails'],
            'long-drink': ['Long drinks & highballs cocktails', 'Highball cocktails'],
            'frozen': ['Frozen (blended) cocktails'],
            'hot-drink': ['Hot Drinks cocktails'],
            'layered': ['Layered cocktails'],
            'shot': ['Shot cocktails'],

            # 季節/節慶
            'summer': ['Summer cocktails'],
            'winter': ['Winter cocktails'],
            'autumn': ['Autumn/fall cocktails', 'Fall cocktails'],
            'spring': ['Spring cocktails'],
            'christmas': ['Christmas & Thanksgiving cocktails', 'Christmas cocktails'],
            'halloween': ['Halloween cocktails'],
            'valentines': ['Romantic & Valentine\'s Day cocktails', 'Valentine\'s Day cocktails'],

            # 其他風格
            'spirit-forward': ['Spirit-forward cocktails'],
            'party': ['Party cocktails'],
            'dessert': ['Dessert cocktails cocktails', 'Dessert cocktails']
        }

    def generate_tags(self, cocktail_data: Dict) -> Dict[str, List[str]]:
        """
        為單一調酒生成完整 tags

        Args:
            cocktail_data: 調酒資料字典

        Returns:
            {
                'base_spirits': ['gin', 'vodka'],
                'flavors': ['citrusy', 'herbal', 'dry'],
                'ingredients': ['lemon', 'elderflower', 'soda-water'],
                'styles': ['classic', 'aperitif', 'summer']
            }
        """
        tags = {
            'base_spirits': self._identify_base_spirits(cocktail_data),
            'flavors': self._identify_flavors(cocktail_data),
            'ingredients': self._identify_key_ingredients(cocktail_data),
            'styles': self._identify_styles(cocktail_data)
        }
        return tags

    def _identify_base_spirits(self, data: Dict) -> List[str]:
        """識別基酒類型"""
        spirits = set()

        # 從 ingredients 和 ingredients_detail 獲取資訊
        all_ingredients = []
        all_ingredients.extend(data.get('ingredients', []))
        for ing_detail in data.get('ingredients_detail', []):
            all_ingredients.append(ing_detail.get('ingredient', ''))

        ingredients_text = ' '.join(all_ingredients).lower()

        # 檢查每種基酒
        for spirit, config in self.BASE_SPIRIT_MAPPING.items():
            for keyword in config['keywords']:
                if keyword in ingredients_text:
                    # 排除關鍵字檢查
                    exclude = config.get('exclude_keywords', [])
                    if not any(ex in ingredients_text for ex in exclude):
                        spirits.add(spirit)
                        break

        return sorted(list(spirits))

    def _identify_flavors(self, data: Dict) -> List[str]:
        """識別風味特徵 (增強版: 結合材料關鍵字 + more_categories)"""
        flavors = set()

        # 準備成分文字
        all_ingredients = []
        all_ingredients.extend(data.get('ingredients', []))
        for ing_detail in data.get('ingredients_detail', []):
            all_ingredients.append(ing_detail.get('ingredient', ''))
        ingredients_text = ' '.join(all_ingredients).lower()

        # 取得 more_categories
        more_cats = data.get('more_categories', [])

        # 檢查每個風味
        for flavor, config in self.FLAVOR_MAPPING.items():
            matched = False

            if config.get('method') == 'check_taste':
                # 使用 strength_taste 資料
                if self._check_taste_condition(data, config):
                    matched = True
            else:
                # 方法1: 關鍵字匹配 (原有邏輯)
                keywords = config.get('keywords', [])
                required = config.get('required_ingredients', [])
                all_keywords = keywords + required

                for kw in all_keywords:
                    if kw in ingredients_text:
                        matched = True
                        break

                # 方法2: more_categories 匹配 (補充識別)
                if not matched:
                    category_patterns = config.get('more_categories', [])
                    for cat in more_cats:
                        if any(pattern in cat for pattern in category_patterns):
                            matched = True
                            break

            if matched:
                flavors.add(flavor)

        return sorted(list(flavors))

    def _identify_key_ingredients(self, data: Dict) -> List[str]:
        """識別關鍵材料 (增強版: 結合材料關鍵字 + more_categories)"""
        ingredient_tags = set()

        # 從 ingredients_detail 獲取精確資訊
        all_ingredients = []
        for ing_detail in data.get('ingredients_detail', []):
            all_ingredients.append(ing_detail.get('ingredient', ''))

        # 如果沒有 ingredients_detail，使用 ingredients
        if not all_ingredients:
            all_ingredients = data.get('ingredients', [])

        # 方法1: 檢查每個材料映射 (原有邏輯)
        for tag, patterns in self.INGREDIENT_TAGS_MAPPING.items():
            for ing in all_ingredients:
                ing_lower = ing.lower()
                if any(pattern in ing_lower for pattern in patterns):
                    ingredient_tags.add(tag)
                    break

        # 方法2: 從 more_categories 補充識別特殊材料
        more_cats = data.get('more_categories', [])
        for tag, category_patterns in self.INGREDIENT_MORE_CATEGORIES_MAPPING.items():
            for cat in more_cats:
                if any(pattern in cat for pattern in category_patterns):
                    ingredient_tags.add(tag)
                    break

        return sorted(list(ingredient_tags))

    def _identify_styles(self, data: Dict) -> List[str]:
        """識別風格類型（從 more_categories 映射）"""
        styles = set()
        more_cats = data.get('more_categories', [])

        # 從 more_categories 映射
        for style, category_patterns in self.STYLE_MAPPING.items():
            for cat in more_cats:
                if any(pattern in cat for pattern in category_patterns):
                    styles.add(style)
                    break

        # 額外：從調酒名稱推斷經典款
        name = data.get('name', '').lower()
        if any(keyword in name for keyword in ['martini', 'margarita', 'mojito', 'daiquiri', 'manhattan', 'old fashioned', 'negroni']):
            if 'classic' not in styles and 'contemporary' not in styles:
                # 如果還沒有經典標籤，從名稱判斷可能是經典變體
                pass  # 不自動加，避免誤判

        return sorted(list(styles))

    def _check_taste_condition(self, data: Dict, config: Dict) -> bool:
        """檢查 strength_taste 條件"""
        taste_data = data.get('strength_taste', {})
        field = config.get('field')  # 'strength' or 'sweetness'
        condition = config.get('condition')  # '>=' or '<='
        threshold = config.get('threshold')

        try:
            field_data = taste_data.get(field, {})
            value = field_data.get('value', None)

            if value is None:
                return False

            if condition == '>=':
                return value >= threshold
            elif condition == '<=':
                return value <= threshold
            elif condition == '>':
                return value > threshold
            elif condition == '<':
                return value < threshold
        except:
            return False

        return False


def process_all_cocktails(data_dir: str, output_dir: str = None):
    """
    批次處理所有調酒，生成 tags

    Args:
        data_dir: 調酒 JSON 檔案目錄
        output_dir: 輸出目錄（如果為 None，則覆蓋原檔案）
    """
    generator = CocktailTagGenerator()

    print("=" * 70)
    print("調酒 Tag 自動生成器")
    print("=" * 70)

    # 取得所有 JSON 檔案
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    total_files = len(json_files)

    print(f"\n找到 {total_files} 個調酒檔案")
    print(f"資料目錄: {data_dir}")
    if output_dir:
        print(f"輸出目錄: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    else:
        print("模式: 覆蓋原檔案")

    print("\n開始處理...\n")

    # 統計資料
    stats = {
        'total': 0,
        'with_tags': 0,
        'tag_counts': {
            'base_spirits': Counter(),
            'flavors': Counter(),
            'ingredients': Counter(),
            'styles': Counter()
        },
        'tags_per_cocktail': []
    }

    # 批次處理
    batch_size = 100
    for i, filename in enumerate(json_files, 1):
        filepath = os.path.join(data_dir, filename)

        try:
            # 讀取調酒資料
            with open(filepath, 'r', encoding='utf-8') as f:
                cocktail = json.load(f)

            # 生成 tags
            tags_dict = generator.generate_tags(cocktail)

            # 合併成單一 tags 列表
            all_tags = (
                tags_dict['base_spirits'] +
                tags_dict['flavors'] +
                tags_dict['ingredients'] +
                tags_dict['styles']
            )

            # 更新調酒資料
            cocktail['tags_categorized'] = tags_dict
            cocktail['tags'] = all_tags

            # 儲存
            output_path = os.path.join(output_dir, filename) if output_dir else filepath
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cocktail, f, ensure_ascii=False, indent=2)

            # 統計
            stats['total'] += 1
            if len(all_tags) > 0:
                stats['with_tags'] += 1

            stats['tags_per_cocktail'].append(len(all_tags))

            for category, tags in tags_dict.items():
                for tag in tags:
                    stats['tag_counts'][category][tag] += 1

            # 進度報告
            if i % batch_size == 0 or i == total_files:
                print(f"進度: {i}/{total_files} ({i/total_files*100:.1f}%) | "
                      f"有 tags: {stats['with_tags']} | "
                      f"平均 tags: {sum(stats['tags_per_cocktail'])/len(stats['tags_per_cocktail']):.1f}")

        except Exception as e:
            print(f"[ERROR] 處理 {filename} 時發生錯誤: {str(e)}")
            continue

    # 產生報告
    generate_report(stats, data_dir)


def generate_report(stats: Dict, data_dir: str):
    """產生統計報告"""
    print("\n" + "=" * 70)
    print("處理報告")
    print("=" * 70)

    print(f"\n總調酒數: {stats['total']}")
    print(f"有 tags 的調酒: {stats['with_tags']} ({stats['with_tags']/stats['total']*100:.1f}%)")

    if stats['tags_per_cocktail']:
        avg_tags = sum(stats['tags_per_cocktail']) / len(stats['tags_per_cocktail'])
        print(f"平均每款調酒的 tags 數量: {avg_tags:.1f}")
        print(f"Tags 數量範圍: {min(stats['tags_per_cocktail'])} - {max(stats['tags_per_cocktail'])}")

    # 各維度 Top Tags
    print("\n" + "-" * 70)
    print("各維度 Top 10 Tags")
    print("-" * 70)

    for category, counter in stats['tag_counts'].items():
        print(f"\n【{category}】")
        for tag, count in counter.most_common(10):
            percentage = count / stats['total'] * 100
            print(f"  {tag:30s} {count:5d} 款 ({percentage:5.1f}%)")

    # 儲存詳細報告
    report_path = os.path.join(os.path.dirname(data_dir), 'scripts', 'analysis', 'tag_generation_report.json')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    report_data = {
        'summary': {
            'total_cocktails': stats['total'],
            'with_tags': stats['with_tags'],
            'coverage_rate': stats['with_tags'] / stats['total'] if stats['total'] > 0 else 0,
            'avg_tags_per_cocktail': sum(stats['tags_per_cocktail']) / len(stats['tags_per_cocktail']) if stats['tags_per_cocktail'] else 0
        },
        'tag_statistics': {
            category: dict(counter.most_common())
            for category, counter in stats['tag_counts'].items()
        }
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"\n詳細報告已儲存: {report_path}")

    print("\n" + "=" * 70)
    print("處理完成！")
    print("=" * 70)


def main():
    """主函數"""
    # 配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'diffordsguide')

    # 驗證資料目錄
    if not os.path.exists(DATA_DIR):
        print(f"❌ 錯誤: 找不到資料目錄: {DATA_DIR}")
        sys.exit(1)

    # 詢問是否覆蓋原檔案
    print(f"\n資料目錄: {DATA_DIR}")
    choice = input("\n是否直接覆蓋原始檔案？(y/N): ").strip().lower()

    if choice == 'y':
        output_dir = None
    else:
        output_dir = os.path.join(PROJECT_ROOT, 'data', 'diffordsguide_with_tags')
        print(f"將輸出到新目錄: {output_dir}")

    # 執行處理
    process_all_cocktails(DATA_DIR, output_dir)


if __name__ == '__main__':
    main()
