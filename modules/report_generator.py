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
                MATCH (s:mfx_Student)
                RETURN s.student_id as student_id, s.name as name
                ORDER BY s.student_id
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
                MATCH (m:yzbx_Module)
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
                MATCH (s:mfx_Student {student_id: $student_id})
                RETURN s.student_id as student_id, s.name as name
            """, student_id=student_id).single()
            
            if not student_info:
                return None
            
            # 获取学习活动记录
            activities = session.run("""
                MATCH (s:mfx_Student {student_id: $student_id})-[:PERFORMED]->(a:mfx_Activity)
                RETURN 
                    a.activity_type as activity_type,
                    a.module_name as module_name,
                    a.content_name as content_name,
                    a.timestamp as timestamp,
                    a.details as details
                ORDER BY a.timestamp DESC
                LIMIT 100
            """, student_id=student_id)
            
            activity_list = [dict(record) for record in activities]
            
            # 获取学生统计信息
            stats = session.run("""
                MATCH (s:mfx_Student {student_id: $student_id})-[:PERFORMED]->(a:mfx_Activity)
                RETURN 
                    count(a) as total_activities,
                    count(DISTINCT a.module_name) as modules_accessed,
                    max(a.timestamp) as last_activity
            """, student_id=student_id).single()
            
            stats_dict = dict(stats) if stats else {}
            
        return {
            'student_info': dict(student_info),
            'activities': activity_list,
            'stats': stats_dict
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
                MATCH (m:yzbx_Module {id: $module_id})
                RETURN m.id as module_id, m.name as name
            """, module_id=module_id).single()
            
            if not module_info:
                return None
            
            # 获取该板块下的章节和知识点
            knowledge_points = session.run("""
                MATCH (m:yzbx_Module {id: $module_id})-[:CONTAINS]->(c:yzbx_Chapter)-[:CONTAINS]->(k:yzbx_Knowledge)
                RETURN DISTINCT k.name as knowledge_point, c.name as chapter_name
            """, module_id=module_id)
            
            kp_list = [dict(record) for record in knowledge_points]
            
            # 获取该板块的学习活动统计
            student_stats = session.run("""
                MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                WHERE a.module_name CONTAINS $module_name
                RETURN 
                    s.student_id as student_id,
                    s.name as student_name,
                    count(a) as activity_count,
                    max(a.timestamp) as last_activity
                ORDER BY activity_count DESC
            """, module_name=module_info['name'])
            
            stats_list = [dict(record) for record in student_stats]
            
            # 获取板块总体统计
            overall_stats = session.run("""
                MATCH (m:yzbx_Module {id: $module_id})-[:CONTAINS]->(c:yzbx_Chapter)-[:CONTAINS]->(k:yzbx_Knowledge)
                WITH count(DISTINCT k) as total_kp, count(DISTINCT c) as total_chapters
                OPTIONAL MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                WHERE a.module_name IS NOT NULL
                RETURN 
                    total_kp,
                    total_chapters,
                    count(DISTINCT s) as student_count,
                    count(a) as total_activities
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
                MATCH (s:mfx_Student)
                WITH count(s) as total_students
                MATCH (k:yzbx_Knowledge)
                WITH total_students, count(k) as total_kp
                OPTIONAL MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                RETURN 
                    total_students,
                    total_kp,
                    count(a) as total_activities
            """).single()
            
            # 获取各板块学习情况
            module_stats = session.run("""
                MATCH (m:yzbx_Module)
                OPTIONAL MATCH (m)-[:CONTAINS]->(c:yzbx_Chapter)-[:CONTAINS]->(k:yzbx_Knowledge)
                WITH m, count(DISTINCT k) as kp_count, count(DISTINCT c) as chapter_count
                OPTIONAL MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                WHERE a.module_name = m.name
                RETURN 
                    m.name as module_name,
                    kp_count,
                    chapter_count,
                    count(DISTINCT s) as student_count,
                    count(a) as activity_count
                ORDER BY m.id
            """)
            
            module_list = [dict(record) for record in module_stats]
            
            # 获取活跃学生Top10
            active_students = session.run("""
                MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                RETURN 
                    s.student_id as student_id,
                    s.name as student_name,
                    count(a) as activity_count
                ORDER BY activity_count DESC
                LIMIT 10
            """)
            
            active_list = [dict(record) for record in active_students]
            
            # 获取热门学习内容
            popular_content = session.run("""
                MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                WHERE a.content_name IS NOT NULL
                RETURN 
                    a.content_name as content_name,
                    a.module_name as module_name,
                    count(DISTINCT s) as student_count,
                    count(a) as access_count
                ORDER BY access_count DESC
                LIMIT 10
            """)
            
            popular_list = [dict(record) for record in popular_content]
            
        return {
            'overall_stats': dict(overall_stats) if overall_stats else {},
            'module_stats': module_list,
            'active_students': active_list,
            'popular_content': popular_list
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
        stats = student_data.get('stats', {})
        
        # 统计数据
        activity_count = len(activities)
        total_activities = stats.get('total_activities', activity_count)
        modules_accessed = stats.get('modules_accessed', 0)
        
        # 按模块统计活动
        module_counts = {}
        for a in activities:
            module = a.get('module_name', '未知模块')
            module_counts[module] = module_counts.get(module, 0) + 1
        
        prompt = f"""
请作为一名资深的管理学教师，为以下学生生成一份详细的学习分析报告。

# 学生信息
- 学号：{student_info.get('student_id', 'N/A')}
- 姓名：{student_info.get('name', 'N/A')}

# 学习数据概览
- 总学习活动次数：{total_activities}次
- 访问模块数：{modules_accessed}个

# 各模块学习情况
{chr(10).join([f"- {m}: {c}次活动" for m, c in module_counts.items()])}

# 最近学习活动（前10条）
{chr(10).join([f"- [{a.get('activity_type', 'N/A')}] {a.get('module_name', '')}: {a.get('content_name', 'N/A')}" for a in activities[:10]])}

请从以下几个方面生成报告：
1. **学习表现总结**：总体评价该学生的学习态度、学习频率和学习覆盖面
2. **学习特点分析**：分析学生的学习模式和偏好
3. **后续学习建议**：推荐接下来应该重点学习的内容和学习方法

报告要求：
- 语言专业、客观、具有建设性
- 结合数据给出分析
- 给出切实可行的学习建议
- 报告字数500-800字
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
        
        # 提取知识点名称列表
        kp_names = [kp.get('knowledge_point', 'N/A') for kp in knowledge_points] if knowledge_points else []
        
        prompt = f"""
请作为一名资深的管理学教师，为以下学习板块生成一份整体学习分析报告。

# 板块信息
- 板块名称：{module_info.get('name', 'N/A')}
- 包含知识点：{overall_stats.get('total_kp', len(kp_names))}个
- 包含章节：{overall_stats.get('total_chapters', 0)}个

# 整体统计
- 参与学习学生数：{overall_stats.get('student_count', 0)}人
- 总学习活动次数：{overall_stats.get('total_activities', 0)}次

# 知识点列表
{chr(10).join([f"- {kp}" for kp in kp_names[:20]])}
{f"... 等共{len(kp_names)}个知识点" if len(kp_names) > 20 else ""}

# 学生学习情况Top10
{chr(10).join([f"- {s.get('student_name', 'N/A')}: {s.get('activity_count', 0)}次活动" for s in student_stats[:10]])}

请从以下几个方面生成报告：
1. **板块学习概况**：该板块的整体学习情况和参与度
2. **学习效果分析**：学生对该板块内容的掌握程度
3. **存在问题**：学习中可能遇到的问题和薄弱环节
4. **教学建议**：针对该板块的教学改进建议

报告要求：
- 语言专业、客观、具有指导意义
- 结合数据进行分析
- 给出切实可行的教学改进建议
- 报告字数600-800字
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
        popular_content = overall_data.get('popular_content', [])
        
        prompt = f"""
请作为一名资深的管理学教师和教学管理者，为整个管理学课程生成一份全面的教学分析报告。

# 总体数据
- 学生总数：{overall_stats.get('total_students', 0)}人
- 知识点总数：{overall_stats.get('total_kp', 0)}个
- 总学习活动：{overall_stats.get('total_activities', 0)}次

# 各板块学习情况
{chr(10).join([f"- {m.get('module_name', 'N/A')}: {m.get('kp_count', 0)}个知识点, {m.get('chapter_count', 0)}章节, {m.get('activity_count', 0)}次活动" for m in module_stats])}

# 最活跃学生Top10
{chr(10).join([f"- {s.get('student_name', 'N/A') or s.get('student_id', 'N/A')}: {s.get('activity_count', 0)}次活动" for s in active_students])}

# 热门学习内容Top10
{chr(10).join([f"- {c.get('content_name', 'N/A')}: {c.get('access_count', 0)}次访问, {c.get('student_count', 0)}人学习" for c in popular_content])}

请从以下几个方面生成报告：
1. **整体学习状况**：课程的总体学习情况和参与度分析
2. **各板块对比分析**：不同板块的学习效果对比
3. **学生学习特征**：分析学生群体的学习特点和学习习惯
4. **热门内容分析**：哪些内容最受欢迎
5. **改进建议**：针对课程整体的教学改进建议

报告要求：
- 语言专业、系统、具有指导意义
- 数据驱动，深入分析
- 给出可落地的改进方案
- 报告字数800-1200字
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
        
        # 创建学生选择选项 - 处理 name 可能为 None 的情况
        student_options = []
        for s in students:
            name = s.get('name') or '未命名'
            student_id = s.get('student_id', 'N/A')
            student_options.append(f"{name} ({student_id})")
        
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
        
        # 创建板块选择选项 - 处理 name 可能为 None 的情况
        module_options = []
        module_id_map = {}
        for m in modules:
            name = m.get('name') or f"板块{m.get('module_id', 'N/A')}"
            module_options.append(name)
            module_id_map[name] = m.get('module_id')
        
        selected_module = st.selectbox("选择学习板块", module_options)
        
        # 获取板块ID
        module_id = module_id_map.get(selected_module)
    
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
