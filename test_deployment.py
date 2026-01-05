"""
部署前测试脚本 - 检查 Streamlit Cloud 部署兼容性
"""

import sys
import importlib

def test_imports():
    """测试所有必需的包是否可以导入"""
    required_packages = [
        'streamlit',
        'openai', 
        'httpx',
        'pandas',
        'numpy',
        'plotly',
        'pyvis',
        'neo4j',
    ]
    
    print("=" * 50)
    print("测试包导入...")
    print("=" * 50)
    
    failed = []
    for package in required_packages:
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✓ {package:20s} version: {version}")
        except ImportError as e:
            print(f"✗ {package:20s} 导入失败: {e}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ {len(failed)} 个包导入失败: {', '.join(failed)}")
        return False
    else:
        print(f"\n✓ 所有必需包都已成功导入")
        return True

def test_config():
    """测试配置文件"""
    print("\n" + "=" * 50)
    print("测试配置文件...")
    print("=" * 50)
    
    try:
        from config import settings
        
        # 检查关键配置
        configs = {
            'NEO4J_URI': settings.NEO4J_URI,
            'NEO4J_USERNAME': settings.NEO4J_USERNAME,
            'DEEPSEEK_API_KEY': settings.DEEPSEEK_API_KEY,
        }
        
        for key, value in configs.items():
            if value:
                masked_value = value[:10] + '...' if len(value) > 10 else value
                print(f"✓ {key:20s} = {masked_value}")
            else:
                print(f"✗ {key:20s} 未设置")
        
        print("\n✓ 配置文件加载成功")
        return True
    except Exception as e:
        print(f"\n❌ 配置文件加载失败: {e}")
        return False

def test_data_files():
    """测试数据文件是否存在"""
    print("\n" + "=" * 50)
    print("测试数据文件...")
    print("=" * 50)
    
    import os
    
    required_files = [
        'data/cases.json',
        'data/cases.py',
        'data/abilities.py',
        'data/knowledge_graph.py',
    ]
    
    failed = []
    for filepath in required_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filepath:30s} ({size} bytes)")
        else:
            print(f"✗ {filepath:30s} 文件不存在")
            failed.append(filepath)
    
    if failed:
        print(f"\n❌ {len(failed)} 个文件缺失")
        return False
    else:
        print(f"\n✓ 所有数据文件都存在")
        return True

def test_neo4j_connection():
    """测试 Neo4j 连接"""
    print("\n" + "=" * 50)
    print("测试 Neo4j 连接...")
    print("=" * 50)
    
    try:
        from neo4j import GraphDatabase
        from config import settings
        
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        
        # 测试连接
        with driver.session() as session:
            result = session.run("RETURN 1 as num")
            record = result.single()
            if record and record["num"] == 1:
                print("✓ Neo4j 连接成功")
                
                # 检查节点数量
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()["count"]
                print(f"✓ 数据库中有 {count} 个节点")
                
                driver.close()
                return True
    except Exception as e:
        print(f"❌ Neo4j 连接失败: {e}")
        return False

def test_modules():
    """测试各个模块是否可以导入"""
    print("\n" + "=" * 50)
    print("测试应用模块...")
    print("=" * 50)
    
    modules = [
        'modules.auth',
        'modules.case_library',
        'modules.knowledge_graph',
        'modules.ability_recommender',
        'modules.classroom_interaction',
        'modules.analytics',
    ]
    
    failed = []
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ {len(failed)} 个模块导入失败")
        return False
    else:
        print(f"\n✓ 所有模块都可以导入")
        return True

def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("Streamlit Cloud 部署兼容性测试")
    print("=" * 50 + "\n")
    
    tests = [
        ("包导入", test_imports),
        ("配置文件", test_config),
        ("数据文件", test_data_files),
        ("应用模块", test_modules),
        ("Neo4j连接", test_neo4j_connection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 发生异常: {e}")
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status:10s} {name}")
    
    print("\n" + "=" * 50)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 50)
    
    if passed == total:
        print("\n✅ 所有测试通过，可以部署到 Streamlit Cloud")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请修复后再部署")
        return 1

if __name__ == "__main__":
    sys.exit(main())
