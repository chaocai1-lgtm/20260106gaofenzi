"""
高分子物理知识图谱可视化模块（节点+关系形式）
采用 xjygraph 的交互设计，支持点击节点高亮关联内容
"""

import streamlit as st
import json
from data.knowledge_graph_graph_format import (
    get_graph_data, 
    get_node_by_id, 
    GFZ_CATEGORY_COLORS
)


def create_knowledge_graph_html(selected_node_id=None):
    """
    生成知识图谱的 HTML 内容
    使用 vis.js 库进行可视化
    """
    try:
        graph_data = get_graph_data()
        nodes = graph_data.get("nodes", [])
        relationships = graph_data.get("relationships", [])
        
        if not nodes:
            return None
        
        # 转换节点数据格式供 vis.js 使用
        vis_nodes = []
        for node in nodes:
            color = GFZ_CATEGORY_COLORS.get(node["category"], "#888888")
            
            # 根据层级设置节点大小
            size_map = {1: 60, 2: 50, 3: 40}
            size = size_map.get(node["level"], 40)
            
            # 如果是选中的节点，增加边框宽度
            border_width = 5 if selected_node_id == node["id"] else 2
            
            vis_nodes.append({
                "id": node["id"],
                "label": node["label"],
                "title": f"{node['label']} ({node['category']})",
                "color": color,
                "size": size,
                "shape": "dot",  # 圆形节点
                "borderWidth": border_width,
                "font": {"size": 14 if node["level"] == 1 else 12}
            })
        
        # 转换关系数据
        vis_edges = []
        for rel in relationships:
            vis_edges.append({
                "from": rel["source"],
                "to": rel["target"],
                "label": rel["type"],
                "title": rel["type"],
                "color": "#999999",
                "arrows": "to"
            })
        
        # 生成 HTML
        nodes_json = json.dumps(vis_nodes, ensure_ascii=False)
        edges_json = json.dumps(vis_edges, ensure_ascii=False)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
            <style type="text/css">
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                
                #network {{
                    width: 100%;
                    height: 100%;
                    border: 1px solid #ddd;
                    background-color: #ffffff;
                }}
                
                .vis-network {{
                    border-radius: 8px;
                }}
                
                .vis-tooltip {{
                    background-color: rgba(50, 50, 50, 0.9);
                    color: #ffffff;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    z-index: 9999;
                }}
            </style>
        </head>
        <body>
            <div id="network"></div>
            <script type="text/javascript">
                var nodes = new vis.DataSet({nodes_json});
                var edges = new vis.DataSet({edges_json});
                
                var container = document.getElementById('network');
                var data = {{
                    nodes: nodes,
                    edges: edges
                }};
                
                var options = {{
                    physics: {{
                        enabled: true,
                        barnesHut: {{
                            gravitationalConstant: -8000,
                            centralGravity: 0.1,
                            springLength: 300,
                            springConstant: 0.01,
                            avoidOverlap: 0.8,
                            damping: 0.5
                        }},
                        stabilization: {{
                            enabled: true,
                            iterations: 300,
                            fit: true
                        }}
                    }},
                    interaction: {{
                        hover: true,
                        navigationButtons: true,
                        keyboard: true,
                        dragNodes: true,
                        dragView: true,
                        zoomView: true
                    }},
                    edges: {{
                        smooth: {{
                            enabled: false
                        }}
                    }}
                }};
                
                var network = new vis.Network(container, data, options);
                
                // Handle node click events
                network.on("click", function(params) {{
                    if (params.nodes.length > 0) {{
                        var nodeId = params.nodes[0];
                        console.log("Clicked node:", nodeId);
                        // Highlight selected node
                        nodes.update({{id: nodeId, borderWidth: 5}});
                        highlightRelated(nodeId);
                    }}
                }});
                
                function highlightRelated(nodeId) {{
                    // Reset all nodes and edges to default colors
                    nodes.forEach(function(node) {{
                        nodes.update({{id: node.id, borderWidth: 2}});
                    }});
                    
                    // Find related nodes
                    var relatedNodeIds = new Set([nodeId]);
                    var relatedEdgeIds = new Set();
                    
                    edges.forEach(function(edge) {{
                        if (edge.from === nodeId || edge.to === nodeId) {{
                            relatedNodeIds.add(edge.from);
                            relatedNodeIds.add(edge.to);
                            relatedEdgeIds.add(edge.id);
                        }}
                    }});
                    
                    // Update node colors
                    nodes.forEach(function(node) {{
                        if (relatedNodeIds.has(node.id)) {{
                            nodes.update({{id: node.id, opacity: 1}});
                        }} else {{
                            nodes.update({{id: node.id, opacity: 0.3}});
                        }}
                    }});
                    
                    // Update edge colors
                    edges.forEach(function(edge) {{
                        if (relatedEdgeIds.has(edge.id)) {{
                            edges.update({{id: edge.id, opacity: 1}});
                        }} else {{
                            edges.update({{id: edge.id, opacity: 0.1}});
                        }}
                    }});
                }}
            </script>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        print(f"创建知识图谱 HTML 失败: {e}")
        return None


def render_knowledge_graph_interactive():
    """
    渲染交互式知识图谱主界面
    包含侧边栏导航和知识图谱展示
    """
    # 初始化 session_state
    if "selected_node" not in st.session_state:
        st.session_state.selected_node = None
    
    # 侧边栏
    with st.sidebar:
        st.markdown("### 📚 知识导航")
        
        # 搜索框
        search_term = st.text_input("🔍 搜索知识点", "")
        
        # 加载数据
        try:
            graph_data = get_graph_data()
            nodes = graph_data.get("nodes", [])
            
            # 按类别分组显示节点
            categories = {}
            for node in nodes:
                cat = node["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(node)
            
            # 显示分类展开器
            for category, cat_nodes in categories.items():
                with st.expander(f"📁 {category} ({len(cat_nodes)})"):
                    # 过滤节点
                    filtered_nodes = cat_nodes
                    if search_term:
                        filtered_nodes = [n for n in cat_nodes if search_term.lower() in n["label"].lower()]
                    
                    # 显示节点列表
                    for node in filtered_nodes:
                        if st.button(node["label"], key=f"nav_{node['id']}", use_container_width=True):
                            st.session_state.selected_node = node
                            st.rerun()
        
        except Exception as e:
            st.error(f"❌ 加载知识列表失败: {e}")
        
        # 显示选中节点的详情
        st.markdown("---")
        if st.session_state.get("selected_node"):
            render_node_detail_panel(st.session_state.get("selected_node"))
    
    # 主区域
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("##### 📊 知识分类")
        # 获取所有模块用于下拉选择
        try:
            graph_data = get_graph_data()
            all_nodes = graph_data.get("nodes", [])
            modules = [n for n in all_nodes if n["category"] == "模块"]
            
            module_options = ["全部模块"] + [m["label"] for m in modules]
            selected_module = st.selectbox("选择模块", module_options)
        except:
            selected_module = "全部模块"
    
    with col2:
        # 显示颜色图例
        legend_html = "<div style='display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;margin-bottom:10px;'>"
        for cat, color in GFZ_CATEGORY_COLORS.items():
            legend_html += f"<span style='background:{color}33;border:1px solid {color};border-radius:4px;padding:2px 8px;font-size:11px;color:{color};'>{cat}</span>"
        legend_html += "</div>"
        st.markdown(legend_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 创建图谱
    st.markdown("### 🗺️ 知识图谱（点击节点可在左侧查看详情）")
    
    try:
        # 获取选中节点 ID
        selected_node_id = None
        if st.session_state.get("selected_node"):
            selected_node_id = st.session_state.selected_node["id"]
        
        # 生成 HTML
        html_content = create_knowledge_graph_html(selected_node_id)
        
        if html_content:
            st.components.v1.html(html_content, height=1100, scrolling=True)
        else:
            st.error("❌ 无法生成知识图谱")
            
    except Exception as e:
        st.error(f"❌ 知识图谱渲染出错: {str(e)}")


def render_node_detail_panel(node):
    """
    在侧边栏显示节点详情
    """
    if not node:
        return
    
    color = GFZ_CATEGORY_COLORS.get(node["category"], "#888888")
    
    st.markdown(f"""
    <div style='
        background: #ffffff;
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    '>
        <h4 style='color: {color}; margin: 0 0 10px 0;'>📌 {node["label"]}</h4>
        <div style='display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;'>
            <span style='background: {color}22; color: {color}; padding: 3px 8px; border-radius: 12px; font-size: 11px;'>
                {node["category"]}
            </span>
            <span style='background: #f0f0f0; color: #666; padding: 3px 8px; border-radius: 12px; font-size: 11px;'>
                {node["type"]}
            </span>
            <span style='background: #f0f0f0; color: #666; padding: 3px 8px; border-radius: 12px; font-size: 11px;'>
                L{node["level"]}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 属性详情
    st.markdown("**详细信息**")
    props = node.get("properties", {})
    if props:
        for key, value in props.items():
            st.markdown(f"- **{key}**: {value}")
    else:
        st.info("暂无详细属性")
