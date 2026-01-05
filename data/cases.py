"""
管理学经典案例库
精选企业管理实践案例 - 从cases.json加载
"""

import json
import os

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CASES_JSON_PATH = os.path.join(CURRENT_DIR, 'cases.json')

def _load_cases_from_json():
    """从cases.json文件加载案例"""
    try:
        # 尝试使用utf-8-sig编码（处理BOM）
        with open(CASES_JSON_PATH, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载cases.json失败: {e}")
        # 尝试备用编码
        try:
            with open(CASES_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

# 从JSON文件加载案例
CASES = _load_cases_from_json()

# 如果JSON加载失败，使用默认案例（保持向后兼容）
if not CASES:
    CASES = [
        {
            "id": "C001",
            "title": "科技初创企业战略管理案例",
            "category": "战略管理",
            "difficulty": "中等"
        }
    ]

def get_cases():
    """返回所有案例"""
    return CASES

def get_case_by_id(case_id):
    """根据ID获取案例"""
    for case in CASES:
        if case.get('id') == case_id or case.get('id') == str(case_id):
            return case
    return None

def get_cases_by_category(category):
    """根据类别获取案例"""
    return [case for case in CASES if case.get('category') == category]

def get_all_categories():
    """获取所有案例分类"""
    categories = set()
    for case in CASES:
        if 'category' in case:
            categories.add(case['category'])
    return sorted(list(categories))

def get_cases_by_difficulty(difficulty):
    """根据难度获取案例"""
    return [case for case in CASES if case.get('difficulty') == difficulty]
