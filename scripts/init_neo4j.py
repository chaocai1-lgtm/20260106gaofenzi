"""
Neo4j数据库初始化脚本（管理学）
执行Cypher脚本，创建知识图谱、能力图谱和案例数据
所有标签使用 mfx_ 前缀
"""

import json
import os
from neo4j import GraphDatabase
from config.settings import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

def init_neo4j():
    """初始化Neo4j数据库"""
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    print("🚀 开始初始化Neo4j数据库（管理学）...")
    
    try:
        with driver.session() as session:
            # 1. 清空mfx标签的所有数据
            print("📌 清空旧数据...")
            session.run("""
                MATCH (n)
                WHERE any(label IN labels(n) WHERE label STARTS WITH 'mfx')
                DETACH DELETE n
            """)
            print("  ✓ 旧数据已清空")
            
            # 2. 读取并执行Cypher初始化脚本
            print("📌 创建知识图谱...")
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cypher_path = os.path.join(script_dir, 'data', 'neo4j_init.cypher')
            
            with open(cypher_path, 'r', encoding='utf-8') as f:
                cypher_script = f.read()
            
            # 按照分隔符分割语句（空行分隔）
            # 但需要处理多行CREATE语句
            lines = cypher_script.split('\n')
            statements = []
            current_statement = []
            
            for line in lines:
                stripped = line.strip()
                # 跳过注释和空行
                if stripped.startswith('//') or not stripped:
                    if current_statement:
                        statements.append('\n'.join(current_statement))
                        current_statement = []
                    continue
                current_statement.append(line)
            
            # 添加最后一个语句
            if current_statement:
                statements.append('\n'.join(current_statement))
            
            success_count = 0
            for i, statement in enumerate(statements):
                if statement.strip():
                    try:
                        session.run(statement)
                        success_count += 1
                    except Exception as e:
                        print(f"  ✗ 语句执行失败: {str(e)[:80]}")
            
            print(f"  ✓ 执行了 {success_count} 条语句")
            
            # 3. 创建案例节点
            print("📌 创建案例数据...")
            cases_path = os.path.join(script_dir, 'data', 'cases.json')
            
            with open(cases_path, 'r', encoding='utf-8') as f:
                cases = json.load(f)
            
            for case in cases:
                session.run("""
                    CREATE (c:mfx_Case {
                        id: $id,
                        title: $title,
                        chief_complaint: $chief_complaint,
                        patient_age: $patient_age,
                        patient_gender: $patient_gender,
                        diagnosis: $diagnosis,
                        difficulty: $difficulty,
                        symptoms: $symptoms,
                        treatment_plan: $treatment_plan
                    })
                """, 
                    id=case['id'],
                    title=case['title'],
                    chief_complaint=case['chief_complaint'],
                    patient_age=case['patient_info']['age'],
                    patient_gender=case['patient_info']['gender'],
                    diagnosis=case['diagnosis'],
                    difficulty=case['difficulty'],
                    symptoms=case['symptoms'],
                    treatment_plan=case['treatment_plan']
                )
                
                # 创建案例与知识点的关联
                for kp_id in case.get('related_knowledge', []):
                    session.run("""
                        MATCH (c:mfx_Case {id: $case_id})
                        MATCH (k:mfx_Knowledge {id: $kp_id})
                        CREATE (c)-[:RELATES_TO {weight: 0.8}]->(k)
                    """, case_id=case['id'], kp_id=kp_id)
            
            print(f"  ✓ 创建了 {len(cases)} 个案例")
            
            # 4. 验证数据
            print("\n📊 数据统计:")
            
            labels_to_check = [
                ('mfx_Module', '模块'),
                ('mfx_Chapter', '章节'),
                ('mfx_Knowledge', '知识点'),
                ('mfx_Case', '案例'),
                ('mfx_Ability', '能力')
            ]
            
            for label, name in labels_to_check:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = result.single()['count']
                print(f"  {name}数: {count}")
            
            result = session.run("MATCH ()-[r]->() WHERE type(r) IN ['CONTAINS', 'RELATES_TO', 'REQUIRES', 'PREREQUISITE', 'NEXT'] RETURN count(r) as count")
            print(f"  关系数: {result.single()['count']}")
            
        print("\n✅ Neo4j初始化完成！")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        raise
    finally:
        driver.close()

if __name__ == "__main__":
    init_neo4j()
