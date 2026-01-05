"""
学习报告生成模块
使用 DeepSeek AI 生成个人、板块和整体学习分析报告
"""

import streamlit as st
from datetime import datetime
from openai import OpenAI
from config.settings import *
import pandas as pd

def check_neo4j_available():
    """检查Neo4j是否可用"""
    from modules.auth import check_neo4j_available as auth_check
    return auth_check()

def get_neo4j_driver():
    """获取Neo4j连接"""
    from modules.auth import get_neo4j_driver as auth_get_driver
    return auth_get_driver()

def get_all_students():
    """获取所有学生列表"""
    if not check_neo4j_available():
        return []
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (s:Student)
                RETURN s.id as student_id, s.name as name
                ORDER BY s.id
            """)
            students = [dict(record) for record in result]
        return students
    except Exception as e:
        st.error(f"获取学生列表失败: {e}")
        return []

def get_all_modules():
    """获取所有学习板块"""
    if not check_neo4j_available():
        return []
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (m:Module)
                RETURN m.id as module_id, m.name as name
                ORDER BY m.id
            """)
            modules = [dict(record) for record in result]
        return modules
    except Exception as e:
        st.error(f"获取板块列表失败: {e}")
        return []

def get_student_learning_data(student_id):
    """获取学生的学习数据"""
    if not check_neo4j_available():
        return None
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            # 获取学生基本信息
            student_info = session.run("""
                MATCH (s:Student {id: $student_id})
                RETURN s.id as student_id, s.name as name
            """, student_id=student_id).single()
            
            if not student_info:
                return None
            
            # 获取学习活动记录
            activities = session.run("""
                MATCH (s:Student {id: $student_id})-[r:LEARNED]->(k)
                RETURN 
                    labels(k) as node_type,
                    k.name as content_name,
                    r.activity_type as activity_type,
                    r.timestamp as timestamp,
                    r.duration as duration,
                    r.score as score
                ORDER BY r.timestamp DESC
                LIMIT 100
            """, student_id=student_id)
            
            activity_list = [dict(record) for record in activities]
            
            # 获取知识点掌握情况
            knowledge_mastery = session.run("""
                MATCH (s:Student {id: $student_id})-[r:MASTERED]->(k:KnowledgePoint)
                RETURN 
                    k.name as knowledge_point,
                    r.level as mastery_level,
                    r.last_updated as last_updated
                ORDER BY r.last_updated DESC
            """, student_id=student_id)
            
            mastery_list = [dict(record) for record in knowledge_mastery]
            
            # 获取能力评估
            abilities = session.run("""
                MATCH (s:Student {id: $student_id})-[r:HAS_ABILITY]->(a)
                WHERE labels(a)[0] CONTAINS 'Ability'
                RETURN 
                    a.name as ability_name,
                    r.score as ability_score,
                    r.last_updated as last_updated
            """, student_id=student_id)
            
            ability_list = [dict(record) for record in abilities]
            
        return {
            'student_info': dict(student_info),
            'activities': activity_list,
            'knowledge_mastery': mastery_list,
            'abilities': ability_list
        }
    except Exception as e:
        st.error(f"获取学生数据失败: {e}")
        return None

def get_module_learning_data(module_id):
    """获取某个板块的整体学习数据"""
    if not check_neo4j_available():
        return None
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            # 获取板块信息
            module_info = session.run("""
                MATCH (m:Module {id: $module_id})
                RETURN m.id as module_id, m.name as name
            """, module_id=module_id).single()
            
            if not module_info:
                return None
            
            # 获取该板块下的知识点
            knowledge_points = session.run("""
                MATCH (m:Module {id: $module_id})-[:CONTAINS*]->(k:KnowledgePoint)
                RETURN DISTINCT k.name as knowledge_point
            """, module_id=module_id)
            
            kp_list = [record['knowledge_point'] for record in knowledge_points]
            
            # 获取学生学习情况统计
            student_stats = session.run("""
                MATCH (m:Module {id: $module_id})-[:CONTAINS*]->(k:KnowledgePoint)
                MATCH (s:Student)-[r:LEARNED]->(k)
                RETURN 
                    s.name as student_name,
                    count(DISTINCT k) as learned_count,
                    avg(r.score) as avg_score,
                    sum(r.duration) as total_duration
                ORDER BY learned_count DESC
            """, module_id=module_id)
            
            stats_list = [dict(record) for record in student_stats]
            
            # 获取板块总体统计
            overall_stats = session.run("""
                MATCH (m:Module {id: $module_id})-[:CONTAINS*]->(k:KnowledgePoint)
                WITH count(DISTINCT k) as total_kp
                MATCH (m:Module {id: $module_id})-[:CONTAINS*]->(k:KnowledgePoint)
                OPTIONAL MATCH (s:Student)-[r:LEARNED]->(k)
                RETURN 
                    total_kp,
                    count(DISTINCT s) as student_count,
                    count(r) as total_activities,
                    avg(r.score) as avg_score
            """, module_id=module_id).single()
            
        return {
            'module_info': dict(module_info),
            'knowledge_points': kp_list,
            'student_stats': stats_list,
            'overall_stats': dict(overall_stats) if overall_stats else {}
        }
    except Exception as e:
        st.error(f"获取板块数据失败: {e}")
        return None

def get_overall_learning_data():
    """获取整体学习数据"""
    if not check_neo4j_available():
        return None
    
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            # 获取总体统计
            overall_stats = session.run("""
                MATCH (s:Student)
                WITH count(s) as total_students
                MATCH (k:KnowledgePoint)
                WITH total_students, count(k) as total_kp
                MATCH (s:Student)-[r:LEARNED]->(k:KnowledgePoint)
                RETURN 
                    total_students,
                    total_kp,
                    count(r) as total_activities,
                    avg(r.score) as avg_score,
                    sum(r.duration) as total_duration
            """).single()
            
            # 获取各板块学习情况
            module_stats = session.run("""
                MATCH (m:Module)
                OPTIONAL MATCH (m)-[:CONTAINS*]->(k:KnowledgePoint)
                OPTIONAL MATCH (s:Student)-[r:LEARNED]->(k)
                RETURN 
                    m.name as module_name,
                    count(DISTINCT k) as kp_count,
                    count(DISTINCT s) as student_count,
                    avg(r.score) as avg_score
                ORDER BY m.id
            """)
            
            module_list = [dict(record) for record in module_stats]
            
            # 获取活跃学生Top10
            active_students = session.run("""
                MATCH (s:Student)-[r:LEARNED]->()
                RETURN 
                    s.name as student_name,
                    count(r) as activity_count,
                    avg(r.score) as avg_score
                ORDER BY activity_count DESC
                LIMIT 10
            """)
            
            active_list = [dict(record) for record in active_students]
            
            # 获取掌握较好的知识点Top10
            mastered_kp = session.run("""
                MATCH (s:Student)-[r:MASTERED]->(k:KnowledgePoint)
                WHERE r.level >= 3
                RETURN 
                    k.name as knowledge_point,
                    count(s) as student_count,
                    avg(r.level) as avg_level
                ORDER BY student_count DESC, avg_level DESC
                LIMIT 10
            """)
            
            mastered_list = [dict(record) for record in mastered_kp]
            
            # 获取需要加强的知识点
            weak_kp = session.run("""
                MATCH (s:Student)-[r:MASTERED]->(k:KnowledgePoint)
                WHERE r.level < 3
                RETURN 
                    k.name as knowledge_point,
                    count(s) as student_count,
                    avg(r.level) as avg_level
                ORDER BY student_count DESC, avg_level ASC
                LIMIT 10
            """)
            
            weak_list = [dict(record) for record in weak_kp]
            
        return {
            'overall_stats': dict(overall_stats) if overall_stats else {},
            'module_stats': module_list,
            'active_students': active_list,
            'mastered_knowledge': mastered_list,
            'weak_knowledge': weak_list
        }
    except Exception as e:
        st.error(f"获取整体数据失败: {e}")
        return None

def generate_personal_report_with_ai(student_data):
    """使用AI生成个人学习报告"""
    if not student_data:
        return "无法生成报告：学生数据为空"
    
    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        
        # 构建提示词
        student_info = student_data['student_info']
        activities = student_data['activities']
        knowledge_mastery = student_data['knowledge_mastery']
        abilities = student_data['abilities']
        
        # 统计数据
        activity_count = len(activities)
        avg_score = sum([a.get('score', 0) or 0 for a in activities]) / max(activity_count, 1)
        mastery_count = len(knowledge_mastery)
        high_mastery = len([m for m in knowledge_mastery if m.get('mastery_level', 0) >= 3])
        
        prompt = f"""
请作为一名资深的管理学教师，为以下学生生成一份详细的学习分析报告。

# 学生信息
- 学号：{student_info.get('student_id', 'N/A')}
- 姓名：{student_info.get('name', 'N/A')}

# 学习数据概览
- 总学习活动次数：{activity_count}次
- 平均学习成绩：{avg_score:.2f}分
- 已掌握知识点：{mastery_count}个
- 高水平掌握（3级及以上）：{high_mastery}个

# 最近学习活动（前10条）
{chr(10).join([f"- {a.get('activity_type', 'N/A')}: {a.get('content_name', 'N/A')} (得分: {a.get('score', 'N/A')})" for a in activities[:10]])}

# 知识点掌握情况（前10个）
{chr(10).join([f"- {m.get('knowledge_point', 'N/A')}: 掌握等级 {m.get('mastery_level', 0)}/5" for m in knowledge_mastery[:10]])}

# 能力评估
{chr(10).join([f"- {ab.get('ability_name', 'N/A')}: {ab.get('ability_score', 0):.1f}分" for ab in abilities])}

请从以下几个方面生成报告：
1. **学习表现总结**：总体评价该学生的学习态度、学习频率和学习质量
2. **优势分析**：指出学生掌握较好的知识点和能力
3. **不足与建议**：指出需要加强的方面，并给出具体的学习建议
4. **后续学习建议**：推荐接下来应该重点学习的内容和学习方法

报告要求：
- 语言专业、客观、具有建设性
- 数据和分析结合，既要有定量分析也要有定性评价
- 给出切实可行的改进建议
- 报告字数800-1200字
- 使用 Markdown 格式输出
"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位经验丰富的管理学教师，擅长分析学生的学习数据并给出专业的指导建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        report = response.choices[0].message.content
        return report
        
    except Exception as e:
        return f"生成报告失败：{str(e)}"

def generate_module_report_with_ai(module_data):
    """使用AI生成板块学习报告"""
    if not module_data:
        return "无法生成报告：板块数据为空"
    
    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        
        module_info = module_data['module_info']
        knowledge_points = module_data['knowledge_points']
        student_stats = module_data['student_stats']
        overall_stats = module_data['overall_stats']
        
        prompt = f"""
请作为一名资深的管理学教师，为以下学习板块生成一份整体学习分析报告。

# 板块信息
- 板块名称：{module_info.get('name', 'N/A')}
- 包含知识点：{len(knowledge_points)}个

# 整体统计
- 参与学习学生数：{overall_stats.get('student_count', 0)}人
- 总学习活动次数：{overall_stats.get('total_activities', 0)}次
- 平均成绩：{overall_stats.get('avg_score', 0) or 0:.2f}分

# 知识点列表
{chr(10).join([f"- {kp}" for kp in knowledge_points[:20]])}
{f"... 等共{len(knowledge_points)}个知识点" if len(knowledge_points) > 20 else ""}

# 学生学习情况Top10
{chr(10).join([f"- {s.get('student_name', 'N/A')}: 学习了{s.get('learned_count', 0)}个知识点, 平均分{s.get('avg_score', 0) or 0:.1f}" for s in student_stats[:10]])}

请从以下几个方面生成报告：
1. **板块学习概况**：该板块的整体学习情况和参与度
2. **学习效果分析**：学生对该板块内容的掌握程度和学习质量
3. **突出表现**：学习效果好的学生和掌握较好的知识点
4. **存在问题**：学习中遇到的共性问题和薄弱环节
5. **教学建议**：针对该板块的教学改进建议和重点关注内容

报告要求：
- 语言专业、客观、具有指导意义
- 结合数据进行分析
- 给出切实可行的教学改进建议
- 报告字数800-1200字
- 使用 Markdown 格式输出
"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位经验丰富的管理学教师，擅长分析课程板块的教学效果并给出专业的教学改进建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        report = response.choices[0].message.content
        return report
        
    except Exception as e:
        return f"生成报告失败：{str(e)}"

def generate_overall_report_with_ai(overall_data):
    """使用AI生成整体学习报告"""
    if not overall_data:
        return "无法生成报告：整体数据为空"
    
    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        
        overall_stats = overall_data['overall_stats']
        module_stats = overall_data['module_stats']
        active_students = overall_data['active_students']
        mastered_knowledge = overall_data['mastered_knowledge']
        weak_knowledge = overall_data['weak_knowledge']
        
        prompt = f"""
请作为一名资深的管理学教师和教学管理者，为整个管理学课程生成一份全面的教学分析报告。

# 总体数据
- 学生总数：{overall_stats.get('total_students', 0)}人
- 知识点总数：{overall_stats.get('total_kp', 0)}个
- 总学习活动：{overall_stats.get('total_activities', 0)}次
- 平均成绩：{overall_stats.get('avg_score', 0) or 0:.2f}分
- 总学习时长：{overall_stats.get('total_duration', 0) or 0:.0f}分钟

# 各板块学习情况
{chr(10).join([f"- {m.get('module_name', 'N/A')}: {m.get('kp_count', 0)}个知识点, {m.get('student_count', 0)}人参与, 平均分{m.get('avg_score', 0) or 0:.1f}" for m in module_stats])}

# 最活跃学生Top10
{chr(10).join([f"- {s.get('student_name', 'N/A')}: {s.get('activity_count', 0)}次活动, 平均分{s.get('avg_score', 0) or 0:.1f}" for s in active_students])}

# 掌握较好的知识点Top10
{chr(10).join([f"- {k.get('knowledge_point', 'N/A')}: {k.get('student_count', 0)}人掌握, 平均等级{k.get('avg_level', 0):.1f}" for k in mastered_knowledge])}

# 需要加强的知识点Top10
{chr(10).join([f"- {k.get('knowledge_point', 'N/A')}: {k.get('student_count', 0)}人掌握不足, 平均等级{k.get('avg_level', 0):.1f}" for k in weak_knowledge])}

请从以下几个方面生成报告：
1. **整体学习状况**：课程的总体学习情况和参与度分析
2. **各板块对比分析**：不同板块的学习效果对比，找出优势板块和薄弱板块
3. **学生学习特征**：分析学生群体的学习特点、学习习惯和学习效果分布
4. **知识点掌握分析**：哪些知识点掌握较好，哪些需要重点关注
5. **存在的问题**：课程教学中存在的主要问题和挑战
6. **改进建议**：针对课程整体的教学改进建议和优化方案

报告要求：
- 语言专业、系统、具有战略指导意义
- 数据驱动，深入分析
- 给出可落地的改进方案
- 报告字数1200-1500字
- 使用 Markdown 格式输出
"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位经验丰富的管理学教师和教学管理专家，擅长分析整体教学数据并给出战略性的教学改进建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        report = response.choices[0].message.content
        return report
        
    except Exception as e:
        return f"生成报告失败：{str(e)}"

def render_report_generator():
    """渲染学习报告生成页面"""
    st.markdown("## 📊 学习报告生成")
    st.markdown("---")
    
    if not check_neo4j_available():
        st.error("❌ Neo4j数据库连接失败，无法生成报告")
        return
    
    # 报告类型选择
    report_type = st.radio(
        "选择报告类型",
        ["个人学习报告", "板块学习报告", "整体学习报告"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # 根据报告类型显示不同的界面
    if report_type == "个人学习报告":
        render_personal_report_generator()
    elif report_type == "板块学习报告":
        render_module_report_generator()
    else:
        render_overall_report_generator()

def render_personal_report_generator():
    """渲染个人报告生成界面"""
    st.markdown("### 👤 个人学习报告")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        students = get_all_students()
        if not students:
            st.warning("暂无学生数据")
            return
        
        # 创建学生选择选项
        student_options = [f"{s['name']} ({s['student_id']})" for s in students]
        selected_student = st.selectbox("选择学生", student_options)
        
        # 提取学号
        student_id = selected_student.split('(')[1].strip(')')
    
    with col2:
        st.markdown("##### 报告说明")
        st.info("""
        个人报告包括：
        - 学习表现总结
        - 优势分析
        - 不足与建议
        - 后续学习计划
        """)
    
    # 生成报告按钮
    if st.button("🤖 生成个人报告", type="primary", use_container_width=True):
        with st.spinner("正在分析学生数据并生成报告..."):
            # 获取学生数据
            student_data = get_student_learning_data(student_id)
            
            if not student_data:
                st.error("未找到该学生的学习数据")
                return
            
            # 生成报告
            report = generate_personal_report_with_ai(student_data)
            
            # 显示报告
            st.markdown("---")
            st.markdown("### 📄 学习报告")
            st.markdown(report)
            
            # 下载按钮
            st.download_button(
                label="📥 下载报告",
                data=report,
                file_name=f"学习报告_{student_data['student_info']['name']}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

def render_module_report_generator():
    """渲染板块报告生成界面"""
    st.markdown("### 📚 板块学习报告")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        modules = get_all_modules()
        if not modules:
            st.warning("暂无板块数据")
            return
        
        # 创建板块选择选项
        module_options = [f"{m['name']}" for m in modules]
        selected_module = st.selectbox("选择学习板块", module_options)
        
        # 获取板块ID
        module_id = next((m['module_id'] for m in modules if m['name'] == selected_module), None)
    
    with col2:
        st.markdown("##### 报告说明")
        st.info("""
        板块报告包括：
        - 板块学习概况
        - 学习效果分析
        - 突出表现
        - 存在问题
        - 教学建议
        """)
    
    # 生成报告按钮
    if st.button("🤖 生成板块报告", type="primary", use_container_width=True):
        with st.spinner("正在分析板块数据并生成报告..."):
            # 获取板块数据
            module_data = get_module_learning_data(module_id)
            
            if not module_data:
                st.error("未找到该板块的学习数据")
                return
            
            # 生成报告
            report = generate_module_report_with_ai(module_data)
            
            # 显示报告
            st.markdown("---")
            st.markdown("### 📄 板块学习报告")
            st.markdown(report)
            
            # 下载按钮
            st.download_button(
                label="📥 下载报告",
                data=report,
                file_name=f"板块报告_{selected_module}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

def render_overall_report_generator():
    """渲染整体报告生成界面"""
    st.markdown("### 🌐 整体学习报告")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        整体学习报告将分析所有学生在所有板块的学习情况，
        为课程教学提供全面的数据支持和改进建议。
        """)
    
    with col2:
        st.markdown("##### 报告说明")
        st.info("""
        整体报告包括：
        - 整体学习状况
        - 各板块对比分析
        - 学生学习特征
        - 知识点掌握分析
        - 存在问题
        - 改进建议
        """)
    
    # 生成报告按钮
    if st.button("🤖 生成整体报告", type="primary", use_container_width=True):
        with st.spinner("正在分析所有数据并生成整体报告，这可能需要一些时间..."):
            # 获取整体数据
            overall_data = get_overall_learning_data()
            
            if not overall_data:
                st.error("无法获取整体学习数据")
                return
            
            # 生成报告
            report = generate_overall_report_with_ai(overall_data)
            
            # 显示报告
            st.markdown("---")
            st.markdown("### 📄 整体学习报告")
            st.markdown(report)
            
            # 下载按钮
            st.download_button(
                label="📥 下载报告",
                data=report,
                file_name=f"整体学习报告_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
