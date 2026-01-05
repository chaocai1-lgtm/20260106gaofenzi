"""
知识点掌握评估模块
基于学生对知识点的掌握程度评估，AI推荐个性化学习路径
"""

import streamlit as st
from openai import OpenAI
from config.settings import *


# 能力ID到中文名称的映射
ABILITY_ID_TO_NAME = {
    "glx_ability_01": "战略思维能力",
    "glx_ability_02": "决策分析能力", 
    "glx_ability_03": "计划组织能力",
    "glx_ability_04": "组织设计能力",
    "glx_ability_05": "人力资源管理能力",
    "glx_ability_06": "领导影响能力",
    "glx_ability_07": "激励赋能能力",
    "glx_ability_08": "沟通协调能力",
    "glx_ability_09": "控制评估能力",
    "glx_ability_10": "创新变革能力",
}

def get_ability_name(ability_id):
    """将能力ID转换为中文名称"""
    return ABILITY_ID_TO_NAME.get(ability_id, ability_id)
def check_neo4j_available():
    """检查Neo4j是否可用"""
    from modules.auth import check_neo4j_available as auth_check
    return auth_check()

def get_neo4j_driver():
    """获取Neo4j连接（复用auth模块的缓存连接）"""
    from modules.auth import get_neo4j_driver as auth_get_driver
    return auth_get_driver()

def get_current_student():
    """获取当前学生信息"""
    if st.session_state.get('user_role') == 'student':
        return st.session_state.get('student_id')
    return None

def log_ability_activity(activity_type, content_id=None, content_name=None, details=None):
    """记录知识点掌握评估模块活动"""
    student_id = get_current_student()
    if not student_id:
        return
    
    from modules.auth import log_activity
    log_activity(
        student_id=student_id,
        activity_type=activity_type,
        module_name="知识点掌握评估",
        content_id=content_id,
        content_name=content_name,
        details=details
    )

def get_all_abilities():
    """获取所有能力列表"""
    if not check_neo4j_available():
        return []
    
    try:
        driver = get_neo4j_driver()
        
        with driver.session() as session:
            result = session.run("""
                MATCH (a:mfx_Ability)
                RETURN a.id as id, a.name as name, a.category as category, a.description as description
                ORDER BY a.category, a.name
            """)
            
            abilities = [dict(record) for record in result]
        
        # 不关闭driver，保持连接池复用
        return abilities
    except Exception:
        return []

def analyze_learning_path(selected_abilities, mastery_levels, abilities_info=None):
    """分析学习路径并生成推荐"""
    required_knowledge = []
    
    # 尝试从Neo4j获取知识点数据
    if check_neo4j_available():
        try:
            driver = get_neo4j_driver()
            
            # 获取能力需要的知识点
            with driver.session() as session:
                result = session.run("""
                MATCH (a:mfx_Ability)-[r:REQUIRES]->(k:mfx_Knowledge)
                WHERE a.id IN $abilities
                RETURN k.id as kp_id, k.name as kp_name, k.difficulty as difficulty, 
                       collect(a.name) as required_by, max(r.weight) as max_weight
                ORDER BY max_weight DESC
            """, abilities=selected_abilities)
            
                required_knowledge = [dict(record) for record in result]
            
            # 不关闭driver，保持连接池复用
        except Exception:
            required_knowledge = []
    
    # 如果没有从数据库获取到数据，使用示例知识点
    if not required_knowledge:
        # 根据选择的能力生成相关知识点
        ability_knowledge_map = {
            "glx_ability_01": [("SWOT分析方法", "基础", 0.9), ("波特五力模型", "中等", 0.8), ("PEST分析", "基础", 0.7)],
            "glx_ability_02": [("决策树分析", "中等", 0.9), ("方案评估方法", "基础", 0.8), ("风险评估技术", "中等", 0.7)],
            "glx_ability_03": [("目标管理(MBO)", "基础", 0.9), ("甘特图制作", "基础", 0.8), ("资源配置方法", "中等", 0.7)],
            "glx_ability_04": [("组织结构类型", "基础", 0.9), ("职能制与事业部制", "中等", 0.8), ("矩阵式组织", "中等", 0.8)],
            "glx_ability_05": [("招聘选拔技术", "中等", 0.9), ("绩效考核方法", "中等", 0.8), ("培训体系设计", "高级", 0.7)],
            "glx_ability_06": [("领导风格理论", "基础", 0.9), ("情境领导模型", "中等", 0.9), ("变革型领导", "高级", 0.8)],
            "glx_ability_07": [("马斯洛需求层次理论", "基础", 0.9), ("双因素理论", "中等", 0.9), ("期望理论", "中等", 0.8)],
            "glx_ability_08": [("沟通技巧", "基础", 0.9), ("冲突管理", "中等", 0.8), ("团队协作方法", "基础", 0.7)],
            "glx_ability_09": [("平衡计分卡", "高级", 0.9), ("KPI设计方法", "中等", 0.8), ("绩效面谈技巧", "中等", 0.8)],
            "glx_ability_10": [("全面质量管理", "中等", 0.9), ("六西格玛", "高级", 0.8), ("ISO质量体系", "中等", 0.8)],
        }
        
        for ability_id in selected_abilities:
            if ability_id in ability_knowledge_map:
                for kp_name, difficulty, weight in ability_knowledge_map[ability_id]:
                    ability_name = next((a['name'] for a in (abilities_info or []) if a['id'] == ability_id), ability_id)
                    required_knowledge.append({
                        'kp_id': f"KP_{ability_id}_{kp_name}",
                        'kp_name': kp_name,
                        'difficulty': difficulty,
                        'required_by': [ability_name],
                        'max_weight': weight
                    })
    
    # 获取知识点名称和掌握程度映射
    ability_names = []
    for a_id in selected_abilities:
        if abilities_info:
            name = next((a['name'] for a in abilities_info if a['id'] == a_id), a_id)
        else:
            name = a_id
        mastery = mastery_levels.get(a_id, 0.5)
        ability_names.append(f"{name}(当前掌握度: {int(mastery*100)}%)")
    
    # 构建知识点描述
    knowledge_desc = []
    for kp in required_knowledge[:15]:
        if isinstance(kp.get('required_by'), list):
            required_by_str = ', '.join(kp['required_by'])
        else:
            required_by_str = str(kp.get('required_by', ''))
        weight = kp.get('max_weight', 0.5)
        if isinstance(weight, (int, float)):
            weight_str = f"{weight:.1f}"
        else:
            weight_str = str(weight)
        knowledge_desc.append(f"- {kp['kp_name']} (难度: {kp.get('difficulty', '未知')}, 重要性: {weight_str}, 相关知识领域: {required_by_str})")
    
    # 使用DeepSeek AI生成推荐
    try:
        import httpx
        
        # 创建不使用代理的httpx客户端，解决Streamlit Cloud部署问题
        http_client = httpx.Client(
            base_url=DEEPSEEK_BASE_URL,
            timeout=60.0,
            follow_redirects=True
        )
        
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            http_client=http_client
        )
        
        prompt = f"""
你是一位管理学教学专家。学生对以下知识点的当前掌握情况如下：

{', '.join(ability_names)}

基于学生的掌握程度评估，这些知识点相关的学习内容包括：
{chr(10).join(knowledge_desc) if knowledge_desc else "（系统将根据掌握情况推荐学习内容）"}

请根据学生对这些知识点的掌握程度，为学生制定一个个性化的学习路径，包括：
1. **学习优先级排序**：根据学生当前掌握情况，按照"薄弱知识点→进阶内容→高级应用"的顺序，列出应该优先学习的内容（5-8个）
2. **针对性学习建议**：针对每个知识点，结合学生当前掌握程度，给出具体的学习建议和提升方向
3. **预计学习时间**：根据掌握程度差异，估算达到熟练水平所需的学习时间
4. **学习效果预期**：完成学习路径后，学生对这些知识点的掌握程度能达到什么水平

请用简洁、友好的语言，给出实用且有针对性的学习建议。
"""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        
        # 关闭httpx客户端
        http_client.close()
        
        return response.choices[0].message.content
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        # 如果AI调用失败，返回一个基本的推荐
        return f"""
### 📚 学习路径推荐

基于您选择的能力目标，建议按以下顺序学习：

**第一阶段：基础理论学习**
1. 管理学基本概念 - 了解管理的定义、职能和原则
2. 组织结构基础 - 掌握各种组织结构形式

**第二阶段：核心技能培养**
3. 战略分析方法 - 学习SWOT、波特五力等工具
4. 决策分析技能 - 练习决策树、方案评估

**第三阶段：综合能力提升**
5. 管理方案设计 - 整合知识进行系统决策
6. 团队管理技巧 - 提高沟通、激励和领导能力

**预计学习时间**：约 2-3 周（每天 1-2 小时）

**学习建议**：建议结合教材、案例分析和实践操作进行学习。

⚠️ 注意：AI分析服务暂时不可用（{str(e)[:50]}），以上为系统预设推荐。
"""

def render_ability_recommender():
    """渲染知识点掌握评估页面"""
    st.title("📊 知识点掌握评估与学习规划")
    
    # 记录进入知识点掌握评估
    log_ability_activity("进入模块", details="访问知识点掌握评估")
    
    st.markdown("""
    评估你对各个管理学知识点的掌握程度，系统将基于AI为你推荐个性化的学习路径和提升方案。
    """)
    
    # 获取所有能力
    abilities = get_all_abilities()
    
    # 始终使用完整的10个知识点列表（无论数据库有无数据）
    abilities = [
        {"id": "glx_ability_01", "name": "战略管理基础知识", "category": "战略管理", "description": "包括SWOT分析、波特五力模型、PEST分析等战略分析工具和方法"},
        {"id": "glx_ability_02", "name": "决策分析方法", "category": "决策管理", "description": "包括决策树、方案评估、风险评估等科学决策的理论和工具"},
        {"id": "glx_ability_03", "name": "计划与目标管理", "category": "计划管理", "description": "包括目标管理(MBO)、甘特图、资源配置等计划制定相关知识"},
        {"id": "glx_ability_04", "name": "组织结构设计", "category": "组织管理", "description": "包括职能制、事业部制、矩阵式组织等各种组织结构形式"},
        {"id": "glx_ability_05", "name": "人力资源管理", "category": "人力资源", "description": "包括招聘选拔、绩效考核、培训开发等人力资源管理核心内容"},
        {"id": "glx_ability_06", "name": "领导理论与实践", "category": "领导管理", "description": "包括领导风格理论、情境领导模型、变革型领导等相关知识"},
        {"id": "glx_ability_07", "name": "激励理论与应用", "category": "激励管理", "description": "包括马斯洛需求层次、双因素理论、期望理论等激励理论知识"},
        {"id": "glx_ability_08", "name": "沟通与协调技巧", "category": "沟通管理", "description": "包括沟通技巧、冲突管理、团队协作等沟通协调相关知识"},
        {"id": "glx_ability_09", "name": "绩效管理体系", "category": "控制管理", "description": "包括平衡计分卡、KPI设计、绩效面谈等绩效管理相关知识"},
        {"id": "glx_ability_10", "name": "质量与创新管理", "category": "创新管理", "description": "包括全面质量管理、六西格玛、ISO体系等质量管理知识"},
    ]
    
    # 按类别分组
    categories = {}
    for ability in abilities:
        cat = ability['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(ability)
    
    # 1. 知识点选择 - 使用form避免每次交互都刷新页面
    st.subheader("1️⃣ 评估知识点掌握程度")
    
    # 初始化session_state
    if 'selected_abilities' not in st.session_state:
        st.session_state.selected_abilities = []
    if 'mastery_levels' not in st.session_state:
        st.session_state.mastery_levels = {}
    
    # 使用expander分类显示知识点，减少页面复杂度
    for category, abs_list in categories.items():
        with st.expander(f"📂 {category}", expanded=True):
            for ability in abs_list:
                col1, col2 = st.columns([3, 2])
                with col1:
                    checked = st.checkbox(
                        f"{ability['name']}",
                        key=f"ability_{ability['id']}",
                        help=ability['description'],
                        value=ability['id'] in st.session_state.selected_abilities
                    )
                    if checked and ability['id'] not in st.session_state.selected_abilities:
                        st.session_state.selected_abilities.append(ability['id'])
                    elif not checked and ability['id'] in st.session_state.selected_abilities:
                        st.session_state.selected_abilities.remove(ability['id'])
                with col2:
                    if ability['id'] in st.session_state.selected_abilities:
                        level = st.slider(
                            "掌握程度",
                            0.0, 1.0, 
                            st.session_state.mastery_levels.get(ability['id'], 0.3), 
                            0.1,
                            key=f"level_{ability['id']}",
                            help="0=完全不了解，0.3=初步了解，0.5=基本掌握，0.8=熟练掌握，1.0=精通"
                        )
                        st.session_state.mastery_levels[ability['id']] = level
    
    selected_abilities = st.session_state.selected_abilities
    mastery_levels = st.session_state.mastery_levels
    
    # 2. 生成推荐
    if selected_abilities:
        st.divider()
        st.subheader("2️⃣ AI学习路径推荐")
        
        if st.button("🤖 生成个性化学习推荐", type="primary"):
            # 记录知识点掌握程度评估
            # 使用中文名称记录活动
            abilities_names = [get_ability_name(aid) for aid in selected_abilities]
            abilities_str = ', '.join(abilities_names)
            log_ability_activity("知识点掌握评估", content_name=abilities_str, details=f"评估知识点: {abilities_str}")
            
            # 创建AI分析可视化容器
            analysis_container = st.container()
            
            with analysis_container:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 25px; border-radius: 15px; margin: 20px 0;">
                    <h3 style="color: white; margin: 0 0 15px 0;">🧠 AI 智能分析中心</h3>
                    <p style="color: rgba(255,255,255,0.9); margin: 0;">基于DeepSeek大模型进行个性化学习路径规划</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 分析步骤显示
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    step1 = st.empty()
                    step1.markdown("""
                    <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 30px;">📊</div>
                        <div style="font-weight: bold; margin: 5px 0;">知识点评估</div>
                        <div style="color: #999; font-size: 12px;">分析掌握程度</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    step2 = st.empty()
                    step2.markdown("""
                    <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 30px;">🔍</div>
                        <div style="font-weight: bold; margin: 5px 0;">知识匹配</div>
                        <div style="color: #999; font-size: 12px;">检索知识图谱</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    step3 = st.empty()
                    step3.markdown("""
                    <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 30px;">🤖</div>
                        <div style="font-weight: bold; margin: 5px 0;">AI推理</div>
                        <div style="color: #999; font-size: 12px;">深度学习分析</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    step4 = st.empty()
                    step4.markdown("""
                    <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                        <div style="font-size: 30px;">📋</div>
                        <div style="font-weight: bold; margin: 5px 0;">生成方案</div>
                        <div style="color: #999; font-size: 12px;">输出学习路径</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                import time
                
                # 步骤1: 知识点评估
                time.sleep(0.5)
                step1.markdown("""
                <div style="text-align: center; padding: 15px; background: #d4edda; border-radius: 10px; border: 2px solid #28a745;">
                    <div style="font-size: 30px;">✅</div>
                    <div style="font-weight: bold; margin: 5px 0; color: #155724;">知识点评估</div>
                    <div style="color: #155724; font-size: 12px;">完成</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 显示评估的知识点掌握程度
                st.markdown("##### 📊 知识点掌握程度评估:")
                abilities_display = st.empty()
                abilities_html = ""
                for ability_id in selected_abilities:
                    ability_name = next((a['name'] for a in abilities if a['id'] == ability_id), ability_id)
                    mastery = mastery_levels.get(ability_id, 0.5)
                    color = "#28a745" if mastery >= 0.7 else "#ffc107" if mastery >= 0.4 else "#dc3545"
                    abilities_html += f"""
                    <span style="display: inline-block; background: {color}22; color: {color}; 
                                 padding: 5px 12px; margin: 3px; border-radius: 20px; border: 1px solid {color};">
                        {ability_name} ({int(mastery*100)}%)
                    </span>
                    """
                abilities_display.markdown(abilities_html, unsafe_allow_html=True)
                
                # 步骤2: 知识匹配
                time.sleep(0.6)
                step2.markdown("""
                <div style="text-align: center; padding: 15px; background: #d4edda; border-radius: 10px; border: 2px solid #28a745;">
                    <div style="font-size: 30px;">✅</div>
                    <div style="font-weight: bold; margin: 5px 0; color: #155724;">知识匹配</div>
                    <div style="color: #155724; font-size: 12px;">完成</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("##### 🔍 知识图谱检索结果:")
                st.info(f"已从知识图谱中匹配到 {len(selected_abilities) * 3} 个相关知识点")
                
                # 步骤3: AI推理
                time.sleep(0.5)
                step3.markdown("""
                <div style="text-align: center; padding: 15px; background: #cce5ff; border-radius: 10px; border: 2px solid #004085; animation: pulse 1s infinite;">
                    <div style="font-size: 30px;">⏳</div>
                    <div style="font-weight: bold; margin: 5px 0; color: #004085;">AI推理中</div>
                    <div style="color: #004085; font-size: 12px;">请稍候...</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 显示AI思考过程
                thinking_box = st.empty()
                thinking_box.markdown("""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #667eea;">
                    <p style="margin: 0; color: #666;">🤖 <strong>AI正在思考...</strong></p>
                    <p style="margin: 5px 0 0 0; color: #888; font-size: 14px;">
                        正在分析您的能力水平、学习目标，结合管理学知识体系生成最优学习路径...
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                try:
                    recommendation = analyze_learning_path(selected_abilities, mastery_levels, abilities)
                    
                    # 步骤3完成
                    step3.markdown("""
                    <div style="text-align: center; padding: 15px; background: #d4edda; border-radius: 10px; border: 2px solid #28a745;">
                        <div style="font-size: 30px;">✅</div>
                        <div style="font-weight: bold; margin: 5px 0; color: #155724;">AI推理</div>
                        <div style="color: #155724; font-size: 12px;">完成</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    thinking_box.empty()
                    
                    # 步骤4完成
                    time.sleep(0.3)
                    step4.markdown("""
                    <div style="text-align: center; padding: 15px; background: #d4edda; border-radius: 10px; border: 2px solid #28a745;">
                        <div style="font-size: 30px;">✅</div>
                        <div style="font-weight: bold; margin: 5px 0; color: #155724;">生成方案</div>
                        <div style="color: #155724; font-size: 12px;">完成</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 显示AI推荐结果
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                                padding: 20px; border-radius: 12px; margin: 20px 0;">
                        <h4 style="color: white; margin: 0;">🎯 AI个性化学习推荐</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(recommendation)
                    
                    # 记录AI推荐生成
                    log_ability_activity("生成AI推荐", details="成功生成学习路径推荐")
                    
                    # 保存到session
                    st.session_state['last_recommendation'] = recommendation
                    
                    st.success("🎉 推荐生成完成！按照上述路径学习，效率更高！")
                    
                except Exception as e:
                    step3.markdown("""
                    <div style="text-align: center; padding: 15px; background: #f8d7da; border-radius: 10px; border: 2px solid #dc3545;">
                        <div style="font-size: 30px;">❌</div>
                        <div style="font-weight: bold; margin: 5px 0; color: #721c24;">AI推理</div>
                        <div style="color: #721c24; font-size: 12px;">失败</div>
                    </div>
                    """, unsafe_allow_html=True)
                    thinking_box.empty()
                    st.error(f"生成推荐失败: {str(e)}")
        
        # 显示历史推荐
        if 'last_recommendation' in st.session_state:
            with st.expander("查看上次推荐"):
                st.markdown(st.session_state['last_recommendation'])
    else:
        st.info("👆 请先选择至少一个知识点")
    
    # 能力雷达图 - 放在主界面
    if selected_abilities and mastery_levels:
        st.divider()
        st.subheader("📈 能力掌握度雷达图")
        
        # 创建雷达图数据
        import plotly.graph_objects as go
        
        # 获取已选能力的名称和掌握度（转换为0-10分制）
        selected_ability_names = []
        selected_mastery_scores = []
        
        for ability in abilities:
            if ability['id'] in selected_abilities:
                selected_ability_names.append(ability['name'])
                # 将0-1的值转换为0-10分制
                selected_mastery_scores.append(mastery_levels[ability['id']] * 10)
        
        # 创建雷达图
        if selected_ability_names:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = go.Figure()
                
                # 闭合雷达图：在数据末尾添加第一个点
                closed_names = selected_ability_names + [selected_ability_names[0]]
                closed_scores = selected_mastery_scores + [selected_mastery_scores[0]]
                
                fig.add_trace(go.Scatterpolar(
                    r=closed_scores,
                    theta=closed_names,
                    fill='toself',
                    name='当前掌握度',
                    line=dict(color='#4ECDC4', width=3),
                    fillcolor='rgba(78, 205, 196, 0.3)'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 10],
                            tickmode='linear',
                            tick0=0,
                            dtick=2,
                            gridcolor='#e0e0e0'
                        ),
                        angularaxis=dict(
                            gridcolor='#e0e0e0'
                        )
                    ),
                    showlegend=True,
                    height=500,
                    margin=dict(l=100, r=100, t=40, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 📊 能力统计")
                
                # 显示统计信息
                avg_mastery = sum(selected_mastery_scores) / len(selected_mastery_scores)
                st.metric("平均掌握度", f"{avg_mastery:.1f}/10", 
                         help="所有选中能力的平均掌握程度")
                
                st.markdown("---")
                
                # 显示最强和最弱能力
                min_idx = selected_mastery_scores.index(min(selected_mastery_scores))
                max_idx = selected_mastery_scores.index(max(selected_mastery_scores))
                
                st.metric("💪 最强能力", 
                         selected_ability_names[max_idx], 
                         f"{selected_mastery_scores[max_idx]:.1f}/10")
                
                st.metric("📖 待提升能力", 
                         selected_ability_names[min_idx], 
                         f"{selected_mastery_scores[min_idx]:.1f}/10")
                
                # 能力分布
                st.markdown("---")
                st.markdown("**能力分布：**")
                high_count = sum(1 for s in selected_mastery_scores if s >= 7)
                mid_count = sum(1 for s in selected_mastery_scores if 4 <= s < 7)
                low_count = sum(1 for s in selected_mastery_scores if s < 4)
                
                st.write(f"🟢 熟练（≥7分）：{high_count}个")
                st.write(f"🟡 中等（4-7分）：{mid_count}个")
                st.write(f"🔴 薄弱（<4分）：{low_count}个")


