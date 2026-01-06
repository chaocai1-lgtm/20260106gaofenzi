"""
从 Neo4j 读取案例和知识图谱数据
"""

from modules.auth import get_neo4j_driver, check_neo4j_available

def get_all_cases():
    """从 Neo4j 获取所有案例"""
    if not check_neo4j_available():
        return []
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (c:gfz_Case)
                OPTIONAL MATCH (c)-[:RELATED_TO_CHAPTER]->(ch:gfz_Chapter)
                OPTIONAL MATCH (c)-[:RELATED_TO_KP]->(kp:gfz_KnowledgePoint)
                RETURN {
                    id: c.id,
                    title: c.title,
                    category: c.category,
                    difficulty: c.difficulty,
                    content: c.content,
                    related_chapters: collect(distinct ch.name),
                    related_kps: collect(distinct kp.id)
                } as case
                ORDER BY c.id
            """)
            
            cases = [dict(record['case']) for record in result]
        return cases
    except Exception as e:
        print(f"获取案例失败: {e}")
        return []

def get_case_by_id(case_id):
    """从 Neo4j 获取指定 ID 的案例"""
    if not check_neo4j_available():
        return None
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (c:gfz_Case {id: $case_id})
                OPTIONAL MATCH (c)-[:RELATED_TO_CHAPTER]->(ch:gfz_Chapter)
                OPTIONAL MATCH (c)-[:RELATED_TO_KP]->(kp:gfz_KnowledgePoint)
                RETURN {
                    id: c.id,
                    title: c.title,
                    category: c.category,
                    difficulty: c.difficulty,
                    content: c.content,
                    related_chapters: collect(distinct ch.name),
                    related_kps: collect(distinct kp.id)
                } as case
            """, case_id=case_id)
            
            record = result.single()
            if record:
                return dict(record['case'])
        return None
    except Exception as e:
        print(f"获取案例失败: {e}")
        return None

def get_knowledge_graph():
    """从 Neo4j 获取完整的知识图谱"""
    if not check_neo4j_available():
        return None
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            # 获取所有模块
            modules_result = session.run("""
                MATCH (m:gfz_Module)
                RETURN m.id as id, m.name as name, m.description as description
                ORDER BY m.id
            """)
            
            modules = []
            for module_record in modules_result:
                module = {
                    "id": module_record["id"],
                    "name": module_record["name"],
                    "description": module_record["description"],
                    "chapters": []
                }
                
                # 获取该模块的所有章节
                chapters_result = session.run("""
                    MATCH (m:gfz_Module {id: $module_id})-[:CONTAINS]->(c:gfz_Chapter)
                    RETURN c.id as id, c.name as name
                    ORDER BY c.id
                """, module_id=module["id"])
                
                for chapter_record in chapters_result:
                    chapter = {
                        "id": chapter_record["id"],
                        "name": chapter_record["name"],
                        "knowledge_points": []
                    }
                    
                    # 获取该章节的所有知识点
                    kps_result = session.run("""
                        MATCH (c:gfz_Chapter {id: $chapter_id})-[:CONTAINS]->(k:gfz_KnowledgePoint)
                        RETURN k.id as id, k.name as name, k.importance as importance
                        ORDER BY k.id
                    """, chapter_id=chapter["id"])
                    
                    for kp_record in kps_result:
                        chapter["knowledge_points"].append({
                            "id": kp_record["id"],
                            "name": kp_record["name"],
                            "importance": kp_record["importance"] or 3
                        })
                    
                    module["chapters"].append(chapter)
                
                modules.append(module)
            
            return {
                "modules": modules,
                "source": "neo4j"
            }
    except Exception as e:
        print(f"获取知识图谱失败: {e}")
        return None

def get_knowledge_modules():
    """获取知识模块列表（用于导航）"""
    if not check_neo4j_available():
        return []
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (m:gfz_Module)
                OPTIONAL MATCH (m)-[:CONTAINS]->(c:gfz_Chapter)
                OPTIONAL MATCH (c)-[:CONTAINS]->(k:gfz_KnowledgePoint)
                RETURN m.id as id, m.name as name, 
                       count(distinct c) as chapter_count,
                       count(distinct k) as kp_count
                ORDER BY m.id
            """)
            
            modules = [dict(record) for record in result]
        return modules
    except Exception as e:
        print(f"获取模块列表失败: {e}")
        return []

def search_knowledge_points(keyword):
    """搜索知识点"""
    if not check_neo4j_available():
        return []
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (k:gfz_KnowledgePoint)
                WHERE k.name CONTAINS $keyword
                OPTIONAL MATCH (c:gfz_Chapter)-[:CONTAINS]->(k)
                OPTIONAL MATCH (m:gfz_Module)-[:CONTAINS]->(c)
                RETURN {
                    id: k.id,
                    name: k.name,
                    importance: k.importance,
                    chapter_name: c.name,
                    module_name: m.name
                } as kp
                LIMIT 20
            """, keyword=keyword)
            
            kps = [dict(record['kp']) for record in result]
        return kps
    except Exception as e:
        print(f"搜索知识点失败: {e}")
        return []
