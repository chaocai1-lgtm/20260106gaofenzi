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
    """从Neo4j或本地数据获取知识图谱数据"""
    # 优先使用新的 data_provider 模块
    if check_neo4j_available():
        try:
            from modules.data_provider import get_knowledge_graph
            graph_data = get_knowledge_graph()
            if graph_data:
                return graph_data
        except:
            pass
    
    # 降级到原来的 Neo4j 查询方式
    if not check_neo4j_available():
        return []
    
    try:
        driver = get_neo4j_driver()
        
        with driver.session() as session:
            if module_id:
                # 获取特定模块的知识图谱
                result = session.run(f"""
                    MATCH path = (m:{NEO4J_LABEL_MODULE_GFZ} {{id: $module_id}})-[:CONTAINS]->(c:{NEO4J_LABEL_CHAPTER_GFZ})-[:CONTAINS]->(k:{NEO4J_LABEL_KNOWLEDGE_GFZ})
                    OPTIONAL MATCH (k)-[r:PREREQUISITE]->(k2:{NEO4J_LABEL_KNOWLEDGE_GFZ})
                    RETURN m, c, k, r, k2
                """, module_id=module_id)
            else:
                # 获取所有模块
                result = session.run(f"""
                    MATCH (m:{NEO4J_LABEL_MODULE_GFZ})-[:CONTAINS]->(c:{NEO4J_LABEL_CHAPTER_GFZ})-[:CONTAINS]->(k:{NEO4J_LABEL_KNOWLEDGE_GFZ})
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
        "高分子链结构": "研究高分子的化学组成、构型、构象和共聚物序列结构，是理解高分子性能的基础。",
        "构型与构象": "构型是化学键的固定排列，构象是单键旋转产生的空间排列，两者共同决定高分子性质。",
        "晶体结构": "高分子的晶态结构包括折叠链、伸直链等模型，晶区与非晶区共存形成半结晶态。",
        "结晶动力学": "通过成核和生长过程形成晶体，可用Avrami方程描述，受温度和冷却速率影响。",
        "玻璃化转变": "无定形高分子从玻璃态到高弹态的转变，Tg是重要的特征温度，影响材料使用范围。",
        "溶解热力学": "高分子溶解涉及熵变和焓变，通过Flory-Huggins理论描述溶液的热力学性质。",
        "相平衡": "高分子溶液的相图与小分子不同，存在UCST和LCST，影响溶液的稳定性。",
        "分子量测定": "通过粘度法、渗透压法、光散射法、GPC等方法测定，不同方法得到不同统计平均分子量。",
        "橡胶弹性": "基于交联网络的熵弹性，遵循统计热力学理论，与金属的能量弹性本质不同。",
        "松弛与蠕变": "高分子的黏弹性表现，应力松弛和蠕变是时间依赖的力学行为。",
        "动态力学性能": "通过DMA测试得到储能模量、损耗模量和损耗角正切，表征材料的黏弹性。",
        "屈服行为": "高分子受力时的塑性变形，与分子链的滑移和取向有关，影响材料的韧性。",
        "断裂机理": "包括银纹、裂纹扩展等过程，断裂强度取决于分子量、结晶度和缺陷。",
        "切黏度": "熔体在剪切流动中的粘度，随剪切速率增加呈现剪切变稀现象。",
        "非牛顿流体": "高分子熔体和溶液的流变行为偏离牛顿流体，表现出剪切变稀、法向应力等特性。",
        "熔体弹性": "高分子熔体具有弹性记忆效应，表现为挤出胀大、不稳定流动等现象。",
        "介电性能": "高分子的电绝缘性、介电常数和介电损耗，与分子极性和松弛过程相关。",
        "导电机理": "通过添加导电填料或本征导电实现导电性，应用于防静电和电子器件。",
        "热导率": "高分子的导热系数通常较低，可通过添加填料提高，应用于散热材料。",
        "热稳定性": "材料在高温下保持性能的能力，通过TGA分析分解温度和失重过程。",
        "表面张力": "高分子表面的自由能，影响润湿性、粘结性和相容性。",
        "界面粘结": "不同材料界面的相互作用力，决定复合材料的界面强度。",
        "相容性": "聚合物共混体系的混溶性，通过Flory-Huggins参数判断，影响材料性能。",
        "增容技术": "通过添加相容剂改善不相容聚合物的界面性能，提高共混物的力学性能。",
        "增韧改性": "通过共混、共聚等方法提高材料韧性，常用橡胶粒子作为增韧剂。",
        "功能化改性": "引入功能基团赋予材料特殊性能，如阻燃、抗菌、自愈合等功能。",
        "注塑成型": "将熔融聚合物注入模具冷却成型，是最常用的塑料加工方法。",
        "挤出成型": "通过螺杆挤出机连续生产型材、薄膜等制品，涉及流变学和传热过程。",
        "材料选择": "根据使用环境和性能要求选择合适的高分子材料，需综合考虑多种因素。",
        "失效分析": "通过断口形貌、化学分析等手段确定材料失效原因，指导产品改进。"
    }
    
    # 如果没有数据，创建示例数据
    if not data:
        # 创建示例知识图谱 - 完整的11个高分子物理模块
        example_modules = {
            "M1": {
                "name": "第1章 高分子链的结构", 
                "description": "化学组成、构型、构象和共聚物序列结构",
                "chapters": {
                    "链结构基础": ["高分子链结构", "构型与构象", "共聚物组成"],
                    "空间结构": ["链构象统计", "柔性链", "刚性链"]
                }
            },
            "M2": {
                "name": "第2章 凝聚态结构", 
                "description": "晶态、非晶态结构及液晶、取向态",
                "chapters": {
                    "晶态结构": ["晶体结构", "结晶动力学", "球晶形态"],
                    "非晶态": ["无定形结构", "自由体积", "链缠结"]
                }
            },
            "M3": {
                "name": "第3章 高分子溶液", 
                "description": "溶解过程、热力学性质和相平衡",
                "chapters": {
                    "溶液理论": ["溶解热力学", "相平衡", "Flory-Huggins理论"],
                    "溶液性质": ["渗透压", "光散射", "粘度"]
                }
            },
            "M4": {
                "name": "第4章 分子量与分布", 
                "description": "分子量的统计意义和测定方法",
                "chapters": {
                    "分子量概念": ["数均分子量", "重均分子量", "分布函数"],
                    "测定方法": ["分子量测定", "GPC技术", "光散射法"]
                }
            },
            "M5": {
                "name": "第5章 转变与运动", 
                "description": "玻璃化转变、结晶行为和分子运动",
                "chapters": {
                    "热转变": ["玻璃化转变", "熔融转变", "DSC分析"],
                    "分子运动": ["链段运动", "侧基运动", "局部运动"]
                }
            },
            "M6": {
                "name": "第6章 橡胶弹性", 
                "description": "橡胶的弹性理论和交联网络",
                "chapters": {
                    "弹性理论": ["橡胶弹性", "统计理论", "交联网络"],
                    "性能表征": ["溶胀平衡", "弹性模量", "网络参数"]
                }
            },
            "M7": {
                "name": "第7章 黏弹性", 
                "description": "黏弹性现象、松弛和蠕变",
                "chapters": {
                    "黏弹性基础": ["松弛与蠕变", "动态力学性能", "时温等效"],
                    "力学行为": ["屈服行为", "断裂机理", "韧性控制"]
                }
            },
            "M8": {
                "name": "第8章 屈服与断裂", 
                "description": "屈服现象、断裂机理和强度理论",
                "chapters": {
                    "屈服理论": ["屈服现象", "塑性变形", "银纹形成"],
                    "断裂分析": ["断裂机理", "裂纹扩展", "断裂韧性"]
                }
            },
            "M9": {
                "name": "第9章 流变性能", 
                "description": "粘性流动、流变测量和加工性能",
                "chapters": {
                    "流变基础": ["切黏度", "非牛顿流体", "熔体弹性"],
                    "流动性能": ["粘流性能", "拉伸黏度", "挤出胀大"]
                }
            },
            "M10": {
                "name": "第10章 电热光性能", 
                "description": "介电性能、导电性、热学性能等功能性能",
                "chapters": {
                    "电学性能": ["介电性能", "导电机理", "电导率"],
                    "热学性能": ["热导率", "热稳定性", "热膨胀"]
                }
            },
            "M11": {
                "name": "第11章 表面与界面", 
                "description": "表面张力、界面粘结、相容性和共混",
                "chapters": {
                    "表面性质": ["表面张力", "界面粘结", "表面改性"],
                    "共混理论": ["相容性", "增容技术", "复合材料"]
                }
            }
        }
        
        # 知识点之间的关联关系（高分子物理）
        knowledge_links = [
            # 第1章内部关联
            ("高分子链结构", "构型与构象", "包含"),
            ("构型与构象", "柔性链", "影响"),
            ("链构象统计", "柔性链", "描述"),
            # 第2章内部关联
            ("晶体结构", "结晶动力学", "决定"),
            ("结晶动力学", "球晶形态", "形成"),
            ("无定形结构", "链缠结", "包含"),
            # 第3章内部关联
            ("溶解热力学", "相平衡", "决定"),
            ("Flory-Huggins理论", "相平衡", "预测"),
            ("渗透压", "分子量测定", "用于"),
            # 第4章内部关联
            ("数均分子量", "重均分子量", "对比"),
            ("GPC技术", "分子量测定", "方法"),
            ("分布函数", "分子量测定", "表征"),
            # 第5章内部关联
            ("玻璃化转变", "分子运动", "基于"),
            ("DSC分析", "玻璃化转变", "测定"),
            ("链段运动", "玻璃化转变", "相关"),
            # 第6章内部关联
            ("橡胶弹性", "统计理论", "基于"),
            ("交联网络", "橡胶弹性", "产生"),
            ("溶胀平衡", "交联网络", "表征"),
            # 第7章内部关联
            ("松弚与蠕变", "动态力学性能", "表现"),
            ("屈服行为", "断裂机理", "先于"),
            # 跨章节关联
            ("构型与构象", "晶体结构", "影响"),
            ("柔性链", "玻璃化转变", "决定"),
            ("结晶动力学", "球晶形态", "形成"),
            ("溶解热力学", "Flory-Huggins理论", "包含"),
            ("分子量测定", "GPC技术", "使用"),
            ("玻璃化转变", "松弚与蠕变", "相关"),
            ("橡胶弹性", "屈服行为", "对比"),
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
                        title=f"📚 {m_info['name']}\n\n{module_desc}\n\n💡 这是高分子物理的核心模块之一，包含重要的理论和实践应用",
                        shape='dot', 
                        borderWidth=4)
            
            for chapter, knowledge_points in m_info['chapters'].items():
                c_id = f"{m_id}_{chapter}"
                
                # 章节解读（高分子物理）
                chapter_descriptions = {
                    "高分子链结构": "高分子链的结构是理解高分子性能的基础，包括化学组成、构型、构象等关键概念。",
                    "凝聚态结构": "高分子的凝聚态结构包括晶态、非晶态、液晶等多种形态，直接影响材料的宏观性能。",
                    "溶液性质": "高分子溶液的性质与小分子溶液有显著差异，涉及溶解热力学、相平衡等重要概念。",
                    "分子量": "分子量及其分布是高分子的重要特征，各种测定方法基于不同的物理化学原理。",
                    "分子运动": "高分子的分子运动具有多重性和多尺度性，表现为玻璃化转变、结晶等重要现象。",
                    "橡胶弹性": "橡胶弹性是高分子特有的力学行为，基于交联网络的熵弹性理论。",
                    "黏弹性": "黏弹性是高分子材料同时具有弹性和粘性的特征，表现为松弛和蠕变行为。",
                    "屈服断裂": "聚合物的屈服和断裂行为决定了材料的力学强度和韧性。",
                    "流变性能": "流变性能描述聚合物熔体的流动行为，对加工成型至关重要。",
                    "功能性能": "聚合物的电学、热学、光学性能赋予材料多样化的功能应用。",
                    "表面界面": "表面和界面性质影响聚合物的粘结、相容性和复合效果。",
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
                desc = m.get('description', '高分子物理核心知识模块')
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
    可视化展示高分子物理知识结构，帮助你建立系统的知识网络。
    - 🔴 **红色节点**：教学模块
    - 🔵 **蓝色节点**：章节
    - 🟢 **绿色节点**：知识点
    - **虚线箭头**：前置关系
    """)
    
    # 模块选择
    modules = [
        ("全部", None),
        ("M1 - 第1章 高分子链的结构", "M1"),
        ("M2 - 第2章 凝聚态结构", "M2"),
        ("M3 - 第3章 高分子溶液", "M3"),
        ("M4 - 第4章 分子量与分子量分布", "M4"),
        ("M5 - 第5章 转变与分子运动", "M5"),
        ("M6 - 第6章 橡胶弹性", "M6"),
        ("M7 - 第7章 黏弹性", "M7"),
        ("M8 - 第8章 屈服与断裂", "M8"),
        ("M9 - 第9章 流变性能", "M9"),
        ("M10 - 第10章 电学、热学和光学性能", "M10"),
        ("M11 - 第11章 表面与界面", "M11")
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
