"""
知识图谱模块
可视化展示五模块知识图谱
"""

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from config.settings import *

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

def log_graph_activity(activity_type, content_id=None, content_name=None, details=None):
    """记录知识图谱活动"""
    student_id = get_current_student()
    if not student_id:
        return
    
    from modules.auth import log_activity
    log_activity(
        student_id=student_id,
        activity_type=activity_type,
        module_name="知识图谱",
        content_id=content_id,
        content_name=content_name,
        details=details
    )

def get_knowledge_graph_data(module_id=None):
    """从Neo4j获取知识图谱数据"""
    if not check_neo4j_available():
        return []
    
    try:
        driver = get_neo4j_driver()
        
        with driver.session() as session:
            if module_id:
                # 获取特定模块的知识图谱
                result = session.run("""
                    MATCH path = (m:yzbx_Module {id: $module_id})-[:CONTAINS]->(c:yzbx_Chapter)-[:CONTAINS]->(k:yzbx_Knowledge)
                    OPTIONAL MATCH (k)-[r:PREREQUISITE]->(k2:yzbx_Knowledge)
                    RETURN m, c, k, r, k2
                """, module_id=module_id)
            else:
                # 获取所有模块
                result = session.run("""
                    MATCH (m:yzbx_Module)-[:CONTAINS]->(c:yzbx_Chapter)-[:CONTAINS]->(k:yzbx_Knowledge)
                    RETURN m, c, k
                    LIMIT 50
                """)
            
            data = [dict(record) for record in result]
        
        # 不关闭driver，保持连接池复用
        return data
    except Exception:
        return []

def create_knowledge_graph_viz(module_id=None):
    """创建知识图谱可视化"""
    # 使用浅色背景
    net = Network(height="1100px", width="100%", bgcolor="#ffffff", font_color="#333333")
    
    # 配置物理引擎 - 优化布局，使用直线，减少交叠
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "solver": "barnesHut",
            "barnesHut": {
                "gravitationalConstant": -35000,
                "centralGravity": 0.1,
                "springLength": 250,
                "springConstant": 0.02,
                "damping": 0.5,
                "avoidOverlap": 1
            },
            "stabilization": {
                "enabled": true,
                "iterations": 200,
                "fit": true
            },
            "minVelocity": 0.75
        },
        "layout": {
            "improvedLayout": true,
            "randomSeed": 42,
            "hierarchical": false
        },
        "edges": {
            "smooth": false,
            "font": {
                "size": 20,
                "color": "#000000",
                "strokeWidth": 0,
                "align": "middle",
                "bold": true
            },
            "color": {
                "inherit": false
            },
            "width": 2.5,
            "chosen": {
                "edge": true
            },
            "arrows": {
                "to": {
                    "enabled": true,
                    "scaleFactor": 0.8
                }
            }
        },
        "nodes": {
            "font": {
                "size": 50,
                "face": "Arial",
                "strokeWidth": 3,
                "strokeColor": "#ffffff",
                "color": "#000000",
                "bold": true,
                "align": "top",
                "vadjust": -140
            },
            "shadow": {
                "enabled": true,
                "size": 8,
                "x": 2,
                "y": 2
            },
            "borderWidth": 2,
            "borderWidthSelected": 4,
            "chosen": {
                "node": true
            }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "navigationButtons": true,
            "keyboard": true
        }
    }
    """)
    
    # 获取数据
    data = get_knowledge_graph_data(module_id)
    
    # 知识点详细信息（用于tooltip显示）
    knowledge_details = {
        "管理的概念": "管理是指在特定的环境下，组织协调他人，通过计划、组织、领导和控制等职能实现目标的过程。",
        "管理的职能": "包括计划、组织、领导和控制四大职能。计划确定目标，组织整合资源，领导协调活动，控制监督绩效。",
        "管理者角色": "根据明茨伯格的研究，管理者需扮演信息角色、决策角色和人际关系角色，不同层级侧重不同。",
        "科学管理理论": "泰勒提出的理论强调标准化、时间研究、工作分解，通过科学方法提高效率。其核心是用科学取代经验。",
        "一般管理理论": "法约尔提出的理论强调管理的普遍性原理，包括计划、组织、命令、协调和控制五大职能。",
        "官僚组织理论": "韦伯提出的理论强调规则、等级制度和制度化，认为理性组织的前提是规范化管理。",
        "行为科学理论": "强调人的需求、心理和社会因素对组织行为的影响，转变了对员工的看法。",
        "决策的过程": "包括确定问题、收集信息、提出方案、评估比较、选择方案和实施控制等阶段。",
        "定性决策方法": "包括头脑风暴法、德尔菲法、名义小组法等，基于专家经验和判断。",
        "定量决策方法": "包括线性规划、决策树、概率论等数学方法，追求最优决策。",
        "群体决策": "通过多人参与进行决策，优点是信息完整，缺点是耗时较长。",
        "计划的特征": "目的性、主观性、灵活性、前瞻性，计划指导组织的其他职能。",
        "战略环境分析": "包括外部环境（政治、经济、社会、技术）和内部环境分析，为战略制定提供基础。",
        "SWOT分析": "优势、劣势、机会和威胁分析，帮助企业清楚地认识自身状况和外部环境。",
        "波特五力模型": "分析产业吸引力的模型，包括供应商、购买者、竞争对手、替代品和潜在进入者的力量。",
        "竞争战略": "包括成本领先战略、差异化战略和集中化战略，企业需根据自身条件选择。",
        "战略实施": "通过组织设计、资源配置、绩效管理等方式确保战略的有效执行。",
        "组织结构": "规定了组织成员的分工、权力关系和协调机制，常见的有职能制、事业部制和矩阵制。",
        "组织文化": "企业成员共同的价值观、信念和行为准则，是组织的灵魂和核心竞争力之一。",
        "权力分析": "权力来源包括法定权、奖励权、强制权、专家权和参考权，管理者需要合理运用。",
        "管理沟通": "是信息流动的过程，包括正式和非正式沟通，有效沟通对组织运作至关重要。",
        "团队建设": "通过共同的目标、良好的沟通和相互信任形成团队，提高组织的整体效能。",
        "员工激励": "基于需要理论，包括物质激励和精神激励，合理激励能提升员工的积极性。",
        "绩效管理": "包括目标设定、过程监控、结果评价和反馈改进，是控制职能的重要体现。",
        "质量管理": "通过制定标准、过程控制、持续改进等方法确保产品或服务的质量。",
        "成本控制": "通过预算、成本分析、费用审批等方式控制企业成本，提高经济效益。",
        "知识管理": "企业收集、整理、共享和利用知识资源的过程，是数字化时代的重要管理内容。",
        "创新管理": "鼓励和支持员工的创意，通过组织创新、产品创新、管理创新驱动企业发展。",
        "供应链管理": "整合从原材料到最终用户的所有活动，优化资源配置，提升企业竞争力。",
        "企业社会责任": "企业对社会、员工、环境等方面的责任和承诺，是现代企业的重要标志。"
    }
    
    # 如果没有数据，创建示例数据
    if not data:
        # 创建示例知识图谱 - 更丰富的内容，添加知识点间的关联
        example_modules = {
            "M1": {
                "name": "管理基础理论", 
                "description": "管理的基本概念、职能和管理者的角色与技能",
                "chapters": {
                    "管理基础": ["管理的概念", "管理的职能", "管理者角色"],
                    "管理思想": ["科学管理理论", "一般管理理论", "官僚组织理论", "行为科学理论"]
                }
            },
            "M2": {
                "name": "决策与计划", 
                "description": "决策的过程和方法，计划工作的制定与实施",
                "chapters": {
                    "决策管理": ["决策的过程", "定性决策方法", "定量决策方法", "群体决策"],
                    "计划工作": ["计划的特征", "战略环境分析", "SWOT分析"]
                }
            },
            "M3": {
                "name": "战略管理", 
                "description": "企业战略分析、制定和实施的过程和方法",
                "chapters": {
                    "战略分析": ["波特五力模型", "战略环境分析", "SWOT分析"],
                    "战略选择": ["竞争战略", "战略实施", "战略创新"]
                }
            },
            "M4": {
                "name": "组织管理", 
                "description": "组织结构设计、文化建设和权力分配",
                "chapters": {
                    "组织设计": ["组织结构", "组织文化", "权力分析"],
                    "组织运作": ["管理沟通", "团队建设", "员工激励"]
                }
            },
            "M5": {
                "name": "控制与创新", 
                "description": "企业的控制管理和创新发展战略",
                "chapters": {
                    "控制管理": ["绩效管理", "质量管理", "成本控制"],
                    "创新发展": ["知识管理", "创新管理", "供应链管理", "企业社会责任"]
                }
            }
        }
        
        # 知识点之间的关联关系
        knowledge_links = [
            ("管理的概念", "管理的职能", "体现"),
            ("管理的职能", "管理者角色", "依赖"),
            ("科学管理理论", "一般管理理论", "继承"),
            ("官僚组织理论", "行为科学理论", "对比"),
            ("决策的过程", "定性决策方法", "包含"),
            ("决策的过程", "定量决策方法", "包含"),
            ("决策的过程", "群体决策", "关联"),
            ("计划的特征", "战略环境分析", "指导"),
            ("SWOT分析", "波特五力模型", "补充"),
            ("波特五力模型", "竞争战略", "驱动"),
            ("竞争战略", "战略实施", "需要"),
            ("组织结构", "权力分析", "定义"),
            ("管理沟通", "团队建设", "支撑"),
            ("团队建设", "员工激励", "促进"),
            ("绩效管理", "质量管理", "指导"),
            ("质量管理", "成本控制", "关联"),
            ("知识管理", "创新管理", "促进"),
            ("创新管理", "供应链管理", "推动"),
            # 跨模块关联
            ("管理者角色", "决策的过程", "执行"),
            ("战略实施", "绩效管理", "监控"),
            ("组织文化", "企业社会责任", "体现"),
        ]
        
        # 根据模块ID筛选
        if module_id and module_id in example_modules:
            modules_to_show = {module_id: example_modules[module_id]}
        else:
            modules_to_show = example_modules
        
        # 收集所有知识点ID用于建立关联
        all_knowledge_ids = {}
        
        for m_id, m_info in modules_to_show.items():
            # 添加模块节点 - 核心节点
            module_desc = m_info.get('description', '')
            net.add_node(m_id, 
                        label=m_info['name'], 
                        color='#FF6B6B', 
                        size=120, 
                        title=f"📚 {m_info['name']}\n\n{module_desc}\n\n💡 这是管理学的核心模块之一，包含重要的管理理论和实践应用",
                        shape='dot', 
                        borderWidth=4)
            
            for chapter, knowledge_points in m_info['chapters'].items():
                c_id = f"{m_id}_{chapter}"
                
                # 章节解读
                chapter_descriptions = {
                    "管理基础": "管理是一门重要的学科，涉及对人力、物资和信息资源的有效协调和利用，实现组织目标。理解管理的核心概念和职能是学习管理学的基础。",
                    "管理思想": "不同时期和学派的管理思想各有侧重。从科学管理到行为科学理论，反映了管理思想的演变和发展，揭示了管理的本质。",
                    "决策管理": "决策是管理的核心职能，贯穿于管理工作的全过程。有效的决策需要科学的方法和合理的程序，包括定性和定量方法。",
                    "计划工作": "计划是指挥其他管理职能的基础。战略规划需要充分分析内外部环境，制定合适的发展方向。",
                    "战略分析": "战略分析工具帮助企业准确把握自身优劣势和外部机遇与威胁，为战略决策提供重要参考。",
                    "战略选择": "企业需根据自身条件选择合适的竞争战略，并确保战略得到有效实施，实现组织目标。",
                    "组织设计": "组织结构是为实现企业目标而设计的。合理的组织设计需要明确权力结构和沟通机制。",
                    "组织运作": "组织的有效运作需要良好的沟通、有凝聚力的团队和适当的激励措施，调动员工的积极性。",
                    "控制管理": "控制是确保战略实施和目标实现的重要保障，包括绩效评估、质量管理和成本控制。",
                    "创新发展": "创新是企业保持竞争力的关键。企业需要建立知识管理体系，鼓励创新，优化供应链，承担社会责任。",
                }
                chapter_desc = chapter_descriptions.get(chapter, f"本章节介绍{chapter}相关内容")
                
                # 添加章节节点
                net.add_node(c_id, 
                            label=chapter, 
                            color='#4ECDC4', 
                            size=120,
                            title=f"📖 {chapter}\n\n{chapter_desc}\n\n包含知识点：{len(knowledge_points)}个",
                            shape='dot', 
                            borderWidth=4)
                net.add_edge(m_id, c_id, label="包含", title="模块包含章节", width=3, color="#888888", smooth=False)
                
                # 添加知识点
                for k_name in knowledge_points:
                    k_id = f"{c_id}_{k_name}"
                    all_knowledge_ids[k_name] = k_id
                    
                    # 获取知识点详细说明
                    detail = knowledge_details.get(k_name, f"{k_name}是{chapter}中的重要知识点，需要重点掌握。")
                    
                    net.add_node(k_id, 
                                label=k_name, 
                                color='#95E1D3', 
                                size=120,
                                title=f"📝 {k_name}\n\n{detail}\n\n所属章节：{chapter}",
                                shape='dot', 
                                borderWidth=4)
                    net.add_edge(c_id, k_id, label="涵盖", title="章节涵盖知识点", width=2, color="#aaaaaa", smooth=False)
        
        # 添加知识点之间的关联边 - 所有边都有标签
        for source, target, relation in knowledge_links:
            source_id = all_knowledge_ids.get(source)
            target_id = all_knowledge_ids.get(target)
            if source_id and target_id:
                net.add_edge(source_id, target_id, 
                           label=relation,
                           color="#e91e63", 
                           width=2.5, 
                           dashes=True,
                           arrows={'to': {'enabled': True, 'scaleFactor': 0.8}},
                           title=f"知识关联：{source} {relation} {target}",
                           smooth=False)
    else:
        nodes_added = set()
        
        for record in data:
            # 添加模块节点
            if 'm' in record and record['m'] and record['m']['id'] not in nodes_added:
                m = record['m']
                desc = m.get('description', '管理学核心知识模块')
                net.add_node(
                    m['id'],
                    label=m['name'],
                    color='#FF6B6B',
                    size=120,
                    title=f"📚 {m['name']}\n\n{desc}",
                    shape='dot',
                    borderWidth=4
                )
                nodes_added.add(m['id'])
            
            # 添加章节节点
            if 'c' in record and record['c'] and record['c']['id'] not in nodes_added:
                c = record['c']
                net.add_node(
                    c['id'],
                    label=c['name'],
                    color='#4ECDC4',
                    size=120,
                    title=f"📖 {c['name']}\n\n本章节包含多个相关知识点，构成完整的知识体系。",
                    shape='dot',
                    borderWidth=4
                )
                nodes_added.add(c['id'])
                if 'm' in record and record['m']:
                    net.add_edge(record['m']['id'], c['id'], 
                               label="包含", 
                               title="模块包含章节",
                               width=3, 
                               color="#888888",
                               smooth=False)
            
            # 添加知识点节点
            if 'k' in record and record['k'] and record['k']['id'] not in nodes_added:
                k = record['k']
                k_name = k['name']
                k_desc = knowledge_details.get(k_name, f"{k_name}的详细内容和学习要点")
                difficulty = k.get('difficulty', '未知')
                
                net.add_node(
                    k['id'],
                    label=k_name,
                    color='#95E1D3',
                    size=120,
                    title=f"📝 {k_name}\n\n{k_desc}\n\n难度：{difficulty}",
                    shape='dot',
                    borderWidth=4
                )
                nodes_added.add(k['id'])
                if 'c' in record and record['c']:
                    net.add_edge(record['c']['id'], k['id'], 
                               label="涵盖", 
                               title="章节涵盖知识点",
                               width=2, 
                               color="#aaaaaa",
                               smooth=False)
            
            # 添加知识点前置关系 - 确保有标签
            if 'k2' in record and record['k2']:
                k2 = record['k2']
                if k2['id'] not in nodes_added:
                    k2_name = k2['name']
                    k2_desc = knowledge_details.get(k2_name, f"{k2_name}的详细内容和学习要点")
                    
                    net.add_node(
                        k2['id'],
                        label=k2_name,
                        color='#95E1D3',
                        size=120,
                        title=f"📝 {k2_name}\n\n{k2_desc}",
                        shape='dot',
                        borderWidth=4
                    )
                    nodes_added.add(k2['id'])
                if 'k' in record and record['k']:
                    net.add_edge(record['k']['id'], k2['id'], 
                               label="前置", 
                               title=f"前置关系：需要先掌握 {k2['name']}",
                               arrows='to', 
                               dashes=True, 
                               color="#ff9999", 
                               width=2.5,
                               smooth=False)
    
    # 保存并返回HTML
    try:
        net.save_graph("temp_graph.html")
        with open("temp_graph.html", 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except Exception:
        return "<div style='padding:20px;text-align:center;'>知识图谱生成中...</div>"

def render_knowledge_graph():
    """渲染知识图谱页面"""
    st.title("🗺️ 章节知识图谱")
    
    # 记录进入知识图谱
    log_graph_activity("进入模块", details="访问知识图谱")
    
    st.markdown("""
    可视化展示管理学五模块知识结构，帮助你建立系统的知识网络。
    - 🔴 **红色节点**：教学模块
    - 🔵 **蓝色节点**：章节
    - 🟢 **绿色节点**：知识点
    - **虚线箭头**：前置关系
    """)
    
    # 模块选择
    modules = [
        ("全部", None),
        ("M1 - 管理基础理论", "M1"),
        ("M2 - 决策与计划", "M2"),
        ("M3 - 战略管理", "M3"),
        ("M4 - 组织管理", "M4"),
        ("M5 - 控制与创新", "M5")
    ]
    
    selected = st.selectbox(
        "选择要查看的模块",
        options=[m[0] for m in modules],
        index=0
    )
    
    module_id = next((m[1] for m in modules if m[0] == selected), None)
    
    # 记录查看模块
    if module_id:
        log_graph_activity("查看模块", content_id=module_id, content_name=selected)
    
    # 生成并显示图谱
    with st.spinner("生成知识图谱中..."):
        html_content = create_knowledge_graph_viz(module_id)
        components.html(html_content, height=1200)
    
    # 学习进度标记
    st.sidebar.title("📊 学习进度")
    st.sidebar.info("未来功能：标记已掌握的知识点")
