"""
导入本地数据到 Neo4j 数据库
将 cases.json 和 knowledge_graph 中的数据导入到 Neo4j
"""

import io
import sys

# 设置标准输出编码为 UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from data.cases_gfz import CASES_GFZ
from data.knowledge_graph_gfz import GFZ_KNOWLEDGE_GRAPH

class DataImporter:
    def __init__(self, uri, username, password):
        """初始化数据导入器"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def close(self):
        """关闭数据库连接"""
        self.driver.close()
    
    def clear_data(self):
        """清空所有数据（谨慎使用！）"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ 已清空所有数据")
    
    def import_cases(self):
        """导入案例数据"""
        print("\n📚 开始导入案例数据...")
        with self.driver.session() as session:
            for case in CASES_GFZ:
                try:
                    # 创建案例节点
                    session.run("""
                        MERGE (c:gfz_Case {id: $case_id})
                        SET c.title = $title,
                            c.category = $category,
                            c.difficulty = $difficulty,
                            c.content = $content,
                            c.timestamp = datetime()
                        RETURN c
                    """, {
                        "case_id": case.get("id"),
                        "title": case.get("title", ""),
                        "category": case.get("category", ""),
                        "difficulty": case.get("difficulty", 2),
                        "content": case.get("content", "")
                    })
                    
                    # 关联相关章节
                    if "related_chapters" in case:
                        for chapter_name in case["related_chapters"]:
                            session.run("""
                                MERGE (c:gfz_Case {id: $case_id})
                                MERGE (ch:gfz_Chapter {name: $chapter_name})
                                MERGE (c)-[:RELATED_TO_CHAPTER]->(ch)
                            """, {
                                "case_id": case.get("id"),
                                "chapter_name": chapter_name
                            })
                    
                    # 关联相关知识点
                    if "related_kps" in case:
                        for kp_id in case["related_kps"]:
                            session.run("""
                                MERGE (c:gfz_Case {id: $case_id})
                                MERGE (kp:gfz_KnowledgePoint {id: $kp_id})
                                MERGE (c)-[:RELATED_TO_KP]->(kp)
                            """, {
                                "case_id": case.get("id"),
                                "kp_id": kp_id
                            })
                    
                    print(f"  ✓ 导入案例: {case.get('title')}")
                except Exception as e:
                    print(f"  ✗ 导入失败 {case.get('id')}: {e}")
    
    def import_knowledge_graph(self):
        """导入知识图谱数据"""
        print("\n🧠 开始导入知识图谱...")
        
        def process_module(session, module):
            """处理知识模块"""
            try:
                module_id = module.get("id")
                session.run("""
                    MERGE (m:gfz_Module {id: $module_id})
                    SET m.name = $name,
                        m.description = $description,
                        m.timestamp = datetime()
                """, {
                    "module_id": module_id,
                    "name": module.get("name", ""),
                    "description": module.get("description", "")
                })
                
                print(f"  ✓ 创建模块: {module.get('name')}")
                
                # 处理章节
                if "chapters" in module:
                    for chapter in module["chapters"]:
                        process_chapter(session, module_id, chapter)
            except Exception as e:
                print(f"  ✗ 处理模块失败 {module.get('name')}: {e}")
        
        def process_chapter(session, module_id, chapter):
            """处理章节"""
            try:
                chapter_id = chapter.get("id")
                session.run("""
                    MERGE (c:gfz_Chapter {id: $chapter_id})
                    SET c.name = $name,
                        c.timestamp = datetime()
                """, {
                    "chapter_id": chapter_id,
                    "name": chapter.get("name", "")
                })
                
                # 创建与模块的关系
                session.run("""
                    MATCH (m:gfz_Module {id: $module_id})
                    MATCH (c:gfz_Chapter {id: $chapter_id})
                    MERGE (m)-[:CONTAINS]->(c)
                """, {
                    "module_id": module_id,
                    "chapter_id": chapter_id
                })
                
                # 处理知识点
                if "knowledge_points" in chapter:
                    for kp in chapter["knowledge_points"]:
                        process_knowledge_point(session, chapter_id, kp)
            except Exception as e:
                print(f"  ✗ 处理章节失败 {chapter.get('name')}: {e}")
        
        def process_knowledge_point(session, chapter_id, kp):
            """处理知识点"""
            try:
                kp_id = kp.get("id")
                session.run("""
                    MERGE (k:gfz_KnowledgePoint {id: $kp_id})
                    SET k.name = $name,
                        k.importance = $importance,
                        k.timestamp = datetime()
                """, {
                    "kp_id": kp_id,
                    "name": kp.get("name", ""),
                    "importance": kp.get("importance", 3)
                })
                
                # 创建与章节的关系
                session.run("""
                    MATCH (c:gfz_Chapter {id: $chapter_id})
                    MATCH (k:gfz_KnowledgePoint {id: $kp_id})
                    MERGE (c)-[:CONTAINS]->(k)
                """, {
                    "chapter_id": chapter_id,
                    "kp_id": kp_id
                })
            except Exception as e:
                print(f"  ✗ 处理知识点失败 {kp.get('name')}: {e}")
        
        with self.driver.session() as session:
            try:
                # 处理所有模块
                if "modules" in GFZ_KNOWLEDGE_GRAPH:
                    for module in GFZ_KNOWLEDGE_GRAPH["modules"]:
                        process_module(session, module)
                
                print(f"  ✓ 知识图谱导入完成")
            except Exception as e:
                print(f"  ✗ 知识图谱导入失败: {e}")
    
    def create_indexes(self):
        """创建数据库索引以提高查询性能"""
        print("\n⚡ 创建数据库索引...")
        with self.driver.session() as session:
            try:
                # 为案例创建索引
                session.run("CREATE INDEX IF NOT EXISTS FOR (c:gfz_Case) ON (c.id)")
                print("  ✓ 创建案例索引")
                
                # 为知识节点创建索引
                session.run("CREATE INDEX IF NOT EXISTS FOR (k:gfz_KnowledgeNode) ON (k.id)")
                print("  ✓ 创建知识节点索引")
                
                # 为学生创建索引
                session.run("CREATE INDEX IF NOT EXISTS FOR (s:gfz_Student) ON (s.student_id)")
                print("  ✓ 创建学生索引")
                
            except Exception as e:
                print(f"  ⚠ 索引创建失败（可能已存在）: {e}")
    
    def verify_import(self):
        """验证导入结果"""
        print("\n✅ 验证导入结果...")
        with self.driver.session() as session:
            # 统计案例数量
            case_count = session.run("MATCH (c:gfz_Case) RETURN count(c) as count").single()["count"]
            print(f"  📚 案例数量: {case_count}")
            
            # 统计知识节点数量
            node_count = session.run("MATCH (k:gfz_KnowledgeNode) RETURN count(k) as count").single()["count"]
            print(f"  🧠 知识节点数量: {node_count}")
            
            # 统计症状数量
            symptom_count = session.run("MATCH (s:gfz_Symptom) RETURN count(s) as count").single()["count"]
            print(f"  🔍 症状类型: {symptom_count}")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Neo4j 数据导入工具")
    print("=" * 60)
    
    # 检查配置
    if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
        print("❌ 错误：NEO4J 配置不完整")
        print("请在 .streamlit/secrets.toml 中配置以下内容:")
        print("  NEO4J_URI = 'bolt://...'")
        print("  NEO4J_USERNAME = 'neo4j'")
        print("  NEO4J_PASSWORD = '...'")
        return False
    
    print(f"\n连接信息:")
    print(f"  URI: {NEO4J_URI}")
    print(f"  Username: {NEO4J_USERNAME}")
    
    try:
        importer = DataImporter(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        
        # 导入数据
        importer.import_cases()
        importer.import_knowledge_graph()
        
        # 创建索引
        importer.create_indexes()
        
        # 验证结果
        importer.verify_import()
        
        # 关闭连接
        importer.close()
        
        print("\n" + "=" * 60)
        print("✅ 数据导入成功！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
