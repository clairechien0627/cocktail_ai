"""
Tag 品質驗證腳本

功能：
- 隨機抽樣檢查 tags 準確性
- 統計覆蓋率和分布
- 識別潛在問題
- 生成可讀的驗證報告
"""

import json
import os
import sys
import random
from typing import List, Dict
from collections import Counter

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TagValidator:
    """Tag 品質驗證器"""

    def __init__(self, data_dir: str):
        """
        初始化驗證器

        Args:
            data_dir: 調酒 JSON 檔案目錄
        """
        self.data_dir = data_dir
        self.stats = {
            'total': 0,
            'with_tags': 0,
            'without_tags': [],
            'tag_distribution': {
                'base_spirits': Counter(),
                'flavors': Counter(),
                'ingredients': Counter(),
                'styles': Counter()
            },
            'tags_per_cocktail': [],
            'dimension_coverage': {
                'base_spirits': 0,
                'flavors': 0,
                'ingredients': 0,
                'styles': 0
            },
            'issues': []
        }

    def validate_all(self, sample_size: int = 20):
        """
        驗證所有調酒的 tags

        Args:
            sample_size: 隨機抽樣數量（用於人工檢查）
        """
        print("=" * 70)
        print("Tag 品質驗證")
        print("=" * 70)

        # 讀取所有調酒
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        total_files = len(json_files)

        print(f"\n找到 {total_files} 個調酒檔案")
        print("開始驗證...\n")

        cocktails = []
        batch_size = 100

        for i, filename in enumerate(json_files, 1):
            filepath = os.path.join(self.data_dir, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    cocktail = json.load(f)

                cocktails.append(cocktail)
                self._validate_single_cocktail(cocktail, filename)

                # 進度報告
                if i % batch_size == 0 or i == total_files:
                    print(f"進度: {i}/{total_files} ({i/total_files*100:.1f}%)")

            except Exception as e:
                self.stats['issues'].append({
                    'file': filename,
                    'error': f'讀取錯誤: {str(e)}'
                })

        # 計算維度覆蓋率
        self._calculate_dimension_coverage()

        # 隨機抽樣檢查
        print(f"\n隨機抽取 {sample_size} 款調酒供人工檢查...")
        samples = random.sample(cocktails, min(sample_size, len(cocktails)))
        self._generate_sample_report(samples)

        # 生成完整報告
        self._generate_report()

    def _validate_single_cocktail(self, cocktail: Dict, filename: str):
        """驗證單一調酒"""
        self.stats['total'] += 1

        tags = cocktail.get('tags', [])
        tags_categorized = cocktail.get('tags_categorized', {})

        # 檢查是否有 tags
        if len(tags) == 0:
            self.stats['without_tags'].append({
                'name': cocktail.get('name', 'Unknown'),
                'file': filename
            })
        else:
            self.stats['with_tags'] += 1

        # 統計 tags 數量
        self.stats['tags_per_cocktail'].append(len(tags))

        # 統計各維度 tags
        for category, tag_list in tags_categorized.items():
            if tag_list:  # 有該維度的 tags
                self.stats['dimension_coverage'][category] += 1

            for tag in tag_list:
                self.stats['tag_distribution'][category][tag] += 1

        # 檢查潛在問題
        self._check_issues(cocktail, filename)

    def _check_issues(self, cocktail: Dict, filename: str):
        """檢查潛在問題"""
        name = cocktail.get('name', 'Unknown')
        tags_categorized = cocktail.get('tags_categorized', {})
        ingredients = cocktail.get('ingredients', [])
        ingredients_text = ' '.join(ingredients).lower()

        # 問題 1: 有明顯基酒但沒有基酒 tag
        obvious_spirits = {
            'gin': 'gin',
            'vodka': 'vodka',
            'rum': 'rum',
            'tequila': 'tequila',
            'whisky': 'whiskey',
            'whiskey': 'whiskey',
            'bourbon': 'whiskey',
            'brandy': 'brandy',
            'cognac': 'brandy'
        }

        for spirit_keyword, spirit_tag in obvious_spirits.items():
            if spirit_keyword in ingredients_text and spirit_tag not in tags_categorized.get('base_spirits', []):
                self.stats['issues'].append({
                    'file': filename,
                    'name': name,
                    'type': 'missing_base_spirit',
                    'detail': f'成分含 "{spirit_keyword}" 但缺少 "{spirit_tag}" tag'
                })
                break

        # 問題 2: 有 lemon/lime juice 但沒有 citrusy flavor
        if ('lemon' in ingredients_text or 'lime' in ingredients_text) and \
           'citrusy' not in tags_categorized.get('flavors', []):
            self.stats['issues'].append({
                'file': filename,
                'name': name,
                'type': 'missing_citrusy',
                'detail': '有柑橘汁但缺少 "citrusy" flavor tag'
            })

        # 問題 3: Tags 數量異常少（< 3 個）
        if len(cocktail.get('tags', [])) < 3:
            self.stats['issues'].append({
                'file': filename,
                'name': name,
                'type': 'too_few_tags',
                'detail': f'只有 {len(cocktail.get("tags", []))} 個 tags'
            })

        # 問題 4: Tags 數量異常多（> 15 個）
        if len(cocktail.get('tags', [])) > 15:
            self.stats['issues'].append({
                'file': filename,
                'name': name,
                'type': 'too_many_tags',
                'detail': f'有 {len(cocktail.get("tags", []))} 個 tags'
            })

    def _calculate_dimension_coverage(self):
        """計算各維度覆蓋率"""
        if self.stats['total'] == 0:
            return

        for dimension in ['base_spirits', 'flavors', 'ingredients', 'styles']:
            coverage = self.stats['dimension_coverage'][dimension] / self.stats['total']
            self.stats['dimension_coverage'][dimension] = coverage

    def _generate_sample_report(self, samples: List[Dict]):
        """生成隨機抽樣報告供人工檢查"""
        output_path = os.path.join(
            os.path.dirname(self.data_dir),
            'scripts', 'analysis', 'tag_validation_samples.md'
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Tag 驗證 - 隨機抽樣檢查\n\n")
            f.write(f"**抽樣數量**: {len(samples)}\n\n")
            f.write("請人工檢查以下調酒的 tags 是否準確：\n\n")
            f.write("---\n\n")

            for i, cocktail in enumerate(samples, 1):
                f.write(f"## {i}. {cocktail.get('name', 'Unknown')}\n\n")
                f.write(f"**URL**: {cocktail.get('url', 'N/A')}\n\n")

                # 成分
                f.write("### 成分\n")
                for ing in cocktail.get('ingredients', []):
                    f.write(f"- {ing}\n")
                f.write("\n")

                # Tags（分類顯示）
                f.write("### 生成的 Tags\n\n")
                tags_cat = cocktail.get('tags_categorized', {})

                if tags_cat.get('base_spirits'):
                    f.write(f"**基酒**: {', '.join(tags_cat['base_spirits'])}\n\n")
                if tags_cat.get('flavors'):
                    f.write(f"**風味**: {', '.join(tags_cat['flavors'])}\n\n")
                if tags_cat.get('ingredients'):
                    f.write(f"**材料**: {', '.join(tags_cat['ingredients'])}\n\n")
                if tags_cat.get('styles'):
                    f.write(f"**風格**: {', '.join(tags_cat['styles'])}\n\n")

                # 原始分類
                if cocktail.get('more_categories'):
                    f.write("### 原始分類 (more_categories)\n")
                    for cat in cocktail['more_categories']:
                        f.write(f"- {cat}\n")
                    f.write("\n")

                # 口感資料
                if cocktail.get('strength_taste'):
                    st = cocktail['strength_taste']
                    f.write("### 口感資料\n")
                    if st.get('strength'):
                        f.write(f"- **Strength**: {st['strength'].get('value', 'N/A')}/10\n")
                    if st.get('sweetness'):
                        f.write(f"- **Sweetness**: {st['sweetness'].get('value', 'N/A')}/10\n")
                    f.write("\n")

                f.write("**✅ Tags 準確？**: [ ] Yes [ ] No\n\n")
                f.write("**💬 備註**: \n\n")
                f.write("---\n\n")

        print(f"✅ 隨機抽樣報告已儲存: {output_path}")

    def _generate_report(self):
        """生成完整驗證報告"""
        print("\n" + "=" * 70)
        print("驗證報告")
        print("=" * 70)

        # 基本統計
        print(f"\n【基本統計】")
        print(f"總調酒數: {self.stats['total']}")
        print(f"有 tags: {self.stats['with_tags']} ({self.stats['with_tags']/self.stats['total']*100:.1f}%)")
        print(f"無 tags: {len(self.stats['without_tags'])} ({len(self.stats['without_tags'])/self.stats['total']*100:.1f}%)")

        if self.stats['tags_per_cocktail']:
            avg_tags = sum(self.stats['tags_per_cocktail']) / len(self.stats['tags_per_cocktail'])
            print(f"\n【Tags 數量】")
            print(f"平均: {avg_tags:.1f} 個/款")
            print(f"範圍: {min(self.stats['tags_per_cocktail'])} - {max(self.stats['tags_per_cocktail'])} 個")

        # 維度覆蓋率
        print(f"\n【維度覆蓋率】")
        for dimension, coverage in self.stats['dimension_coverage'].items():
            print(f"{dimension:20s} {coverage*100:5.1f}% ({int(coverage*self.stats['total'])} 款)")

        # 潛在問題
        print(f"\n【潛在問題】")
        print(f"總問題數: {len(self.stats['issues'])}")

        if self.stats['issues']:
            issue_types = Counter(issue['type'] for issue in self.stats['issues'])
            print("\n問題分類:")
            for issue_type, count in issue_types.most_common():
                print(f"  {issue_type:25s} {count:4d} 個")

            # 顯示前 10 個問題
            print("\n前 10 個問題詳情:")
            for issue in self.stats['issues'][:10]:
                print(f"  [{issue['type']}] {issue['name']}: {issue['detail']}")

        # 無 tags 的調酒
        if self.stats['without_tags']:
            print(f"\n【無 Tags 的調酒】")
            for item in self.stats['without_tags'][:10]:
                print(f"  - {item['name']} ({item['file']})")
            if len(self.stats['without_tags']) > 10:
                print(f"  ... 還有 {len(self.stats['without_tags']) - 10} 款")

        # Top Tags
        print(f"\n【Top 10 Tags】")
        for category, counter in self.stats['tag_distribution'].items():
            print(f"\n{category}:")
            for tag, count in counter.most_common(10):
                percentage = count / self.stats['total'] * 100
                print(f"  {tag:30s} {count:5d} ({percentage:5.1f}%)")

        # 儲存 JSON 報告
        report_path = os.path.join(
            os.path.dirname(self.data_dir),
            'scripts', 'analysis', 'tag_validation_report.json'
        )
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        report_data = {
            'summary': {
                'total_cocktails': self.stats['total'],
                'with_tags': self.stats['with_tags'],
                'coverage_rate': self.stats['with_tags'] / self.stats['total'] if self.stats['total'] > 0 else 0,
                'avg_tags_per_cocktail': sum(self.stats['tags_per_cocktail']) / len(self.stats['tags_per_cocktail']) if self.stats['tags_per_cocktail'] else 0,
                'tags_range': {
                    'min': min(self.stats['tags_per_cocktail']) if self.stats['tags_per_cocktail'] else 0,
                    'max': max(self.stats['tags_per_cocktail']) if self.stats['tags_per_cocktail'] else 0
                }
            },
            'dimension_coverage': self.stats['dimension_coverage'],
            'issues_summary': {
                issue_type: count
                for issue_type, count in Counter(issue['type'] for issue in self.stats['issues']).items()
            },
            'tag_statistics': {
                category: dict(counter.most_common())
                for category, counter in self.stats['tag_distribution'].items()
            },
            'without_tags': self.stats['without_tags'],
            'issues': self.stats['issues']
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 詳細報告已儲存: {report_path}")

        print("\n" + "=" * 70)
        print("驗證完成！")
        print("=" * 70)

        # 總結評分
        self._print_quality_score()

    def _print_quality_score(self):
        """輸出品質評分"""
        print("\n" + "=" * 70)
        print("品質評分")
        print("=" * 70)

        score = 0
        max_score = 100

        # 1. 覆蓋率 (40 分)
        coverage_rate = self.stats['with_tags'] / self.stats['total'] if self.stats['total'] > 0 else 0
        coverage_score = coverage_rate * 40
        score += coverage_score
        print(f"\n✓ 覆蓋率: {coverage_rate*100:.1f}% → {coverage_score:.1f}/40 分")

        # 2. 平均 tags 數量 (20 分) - 理想 7-10 個
        if self.stats['tags_per_cocktail']:
            avg_tags = sum(self.stats['tags_per_cocktail']) / len(self.stats['tags_per_cocktail'])
            if 7 <= avg_tags <= 10:
                tags_score = 20
            elif 5 <= avg_tags < 7 or 10 < avg_tags <= 12:
                tags_score = 15
            else:
                tags_score = 10
            score += tags_score
            print(f"✓ 平均 tags 數量: {avg_tags:.1f} → {tags_score}/20 分")

        # 3. 維度覆蓋 (30 分) - 理想每維度 > 80%
        dim_coverage_avg = sum(self.stats['dimension_coverage'].values()) / 4
        dim_score = dim_coverage_avg * 30
        score += dim_score
        print(f"✓ 維度覆蓋率: {dim_coverage_avg*100:.1f}% → {dim_score:.1f}/30 分")

        # 4. 問題率 (10 分) - 越少越好
        issue_rate = len(self.stats['issues']) / self.stats['total'] if self.stats['total'] > 0 else 0
        if issue_rate < 0.05:  # < 5%
            issue_score = 10
        elif issue_rate < 0.10:  # < 10%
            issue_score = 7
        elif issue_rate < 0.20:  # < 20%
            issue_score = 4
        else:
            issue_score = 0
        score += issue_score
        print(f"✓ 問題率: {issue_rate*100:.1f}% → {issue_score}/10 分")

        print(f"\n" + "=" * 70)
        print(f"總分: {score:.1f}/{max_score} 分")
        print("=" * 70)

        if score >= 90:
            print("評級: ⭐⭐⭐⭐⭐ 優秀")
        elif score >= 80:
            print("評級: ⭐⭐⭐⭐ 良好")
        elif score >= 70:
            print("評級: ⭐⭐⭐ 合格")
        else:
            print("評級: ⭐⭐ 需要改進")


def main():
    """主函數"""
    # 配置
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'diffordsguide')

    # 驗證資料目錄
    if not os.path.exists(DATA_DIR):
        print(f"❌ 錯誤: 找不到資料目錄: {DATA_DIR}")
        sys.exit(1)

    # 詢問抽樣數量
    print(f"資料目錄: {DATA_DIR}\n")
    sample_input = input("隨機抽樣數量 (預設 20): ").strip()
    sample_size = int(sample_input) if sample_input.isdigit() else 20

    # 執行驗證
    validator = TagValidator(DATA_DIR)
    validator.validate_all(sample_size=sample_size)


if __name__ == '__main__':
    main()
