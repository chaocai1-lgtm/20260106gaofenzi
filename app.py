"""
管理学自适应学习系统 - 主应用
"""

import streamlit as st
import random
from modules.case_library import render_case_library
from modules.knowledge_graph import render_knowledge_graph
from modules.ability_recommender import render_ability_recommender
from modules.classroom_interaction import render_classroom_interaction
from modules.auth import render_login_page, check_login, get_current_user, logout
from modules.analytics import render_analytics_dashboard, render_module_analytics
from modules.report_generator import render_report_generator
from modules.teaching_design import render_teaching_design

# 页面配置
st.set_page_config(
    page_title="管理学自适应学习系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🔥 全新颠覆性UI - 暖橙渐变 + 大圆角卡片 + 浮动布局
st.markdown("""
<style>
    /* 导入圆润现代字体 */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Nunito', 'Microsoft YaHei', sans-serif;
    }
    
    *, *::before, *::after { transition: none !important; animation: none !important; }
    .stMetric, .stDataFrame, div[data-testid="stMetricValue"], div[data-testid="stDataFrame"], .stPlotlyChart {
        animation: none !important; border: none !important; outline: none !important;
    }
    [data-testid="stDataFrame"] input[type="text"], .ag-floating-filter { display: none !important; }
    .stStatusWidget, div[data-testid="stStatusWidget"] { display: none !important; }
    
    /* ====== 奶油暖色渐变背景 ====== */
    .stApp {
        background: linear-gradient(180deg, #fef7f0 0%, #fff5eb 50%, #fef3e7 100%);
        min-height: 100vh;
    }
    
    [data-testid="stSidebar"] { display: none !important; }
    
    /* ====== 顶部导航 - 悬浮玻璃卡片 ====== */
    .top-nav {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 100px;
        border: none;
        padding: 12px 12px 12px 28px;
        margin: 10px 0 30px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 8px 40px rgba(255, 120, 50, 0.12), 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .logo-icon {
        font-size: 36px;
        filter: drop-shadow(0 2px 4px rgba(255,120,50,0.3));
    }
    
    .logo-text {
        font-size: 20px;
        font-weight: 800;
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    
    .logo-subtitle {
        font-size: 10px;
        color: #9ca3af;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    /* 用户信息 - 橙色药丸胶囊 */
    .user-info {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 20px 8px 10px;
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        border-radius: 100px;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.35);
    }
    
    .user-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: rgba(255,255,255,0.95);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .user-name {
        color: #ffffff;
        font-weight: 700;
        font-size: 14px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .user-role {
        color: rgba(255,255,255,0.85);
        font-size: 11px;
        font-weight: 500;
    }
    
    /* ====== 功能卡片 - 大圆角浮动卡 ====== */
    .feature-card {
        background: #ffffff;
        border-radius: 28px;
        border: none;
        padding: 32px 28px;
        text-align: center;
        cursor: pointer;
        height: 240px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 40px rgba(255, 120, 50, 0.08), 0 4px 12px rgba(0,0,0,0.03);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #ff6b35, #f7931e, #ffb347);
        border-radius: 28px 28px 0 0;
    }
    
    .feature-card:hover {
        box-shadow: 0 20px 60px rgba(255, 107, 53, 0.18), 0 8px 20px rgba(0,0,0,0.05);
        transform: translateY(-4px);
    }
    
    .feature-icon {
        font-size: 56px;
        margin-bottom: 18px;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(255,120,50,0.2));
    }
    
    .feature-title {
        color: #1f2937;
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .feature-desc {
        color: #6b7280;
        font-size: 13px;
        line-height: 1.6;
    }
    
    /* ====== 统计卡片 - 圆形数字徽章 ====== */
    .stat-card {
        background: #ffffff;
        border-radius: 24px;
        border: none;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 8px 30px rgba(255, 120, 50, 0.08);
        position: relative;
    }
    
    .stat-number {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 13px;
        margin-top: 10px;
        font-weight: 600;
    }
    
    /* 页面标题 */
    .page-title {
        font-size: 28px;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .page-subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 28px;
        font-weight: 500;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* ====== 按钮 - 渐变圆角药丸 ====== */
    .stButton>button {
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        color: white !important;
        border: none;
        border-radius: 50px;
        padding: 12px 24px;
        font-weight: 700;
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.35);
        width: 100%;
        font-size: 14px;
        text-transform: none;
    }
    
    .stButton>button:hover {
        box-shadow: 0 8px 30px rgba(255, 107, 53, 0.45);
        transform: translateY(-2px);
    }
    
    /* 输入框 - 柔和圆角 */
    .stTextInput>div>div>input, 
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea,
    .stTextArea>div>div>textarea:focus {
        background: #ffffff !important;
        border: 2px solid #fed7c3 !important;
        border-radius: 16px !important;
        color: #1f2937 !important;
        padding: 14px 18px !important;
        outline: none !important;
        box-shadow: none !important;
        font-size: 15px !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #ff6b35 !important;
        box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.12) !important;
    }
    
    .stTextInput>div, .stTextInput>div>div,
    .stTextArea>div, .stTextArea>div>div {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stSelectbox>div>div {
        background: #ffffff;
        border-radius: 16px;
        border: 2px solid #fed7c3;
    }
    
    .stRadio>div {
        background: #ffffff;
        border-radius: 20px;
        padding: 16px;
        border: 2px solid #fde8dc;
    }
    
    .stRadio>div>div>label { color: #1f2937 !important; }
    
    /* 指标卡片 */
    [data-testid="metric-container"] {
        background: #ffffff;
        border-radius: 20px;
        padding: 24px;
        border: none;
        box-shadow: 0 6px 25px rgba(255,120,50,0.08);
    }
    
    [data-testid="metric-container"] label { color: #6b7280 !important; font-weight: 600; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { 
        color: #ff6b35 !important; 
        font-weight: 800;
    }
    
    .streamlit-expanderHeader {
        background: #fff8f3;
        border-radius: 16px;
        color: #1f2937 !important;
        border: 2px solid #fde8dc;
        font-weight: 600;
    }
    
    hr { border-color: #fde8dc; }
    
    /* ====== 标签页 - 圆角胶囊切换 ====== */
    .stTabs [data-baseweb="tab-list"] {
        background: #fff8f3;
        border-radius: 50px;
        padding: 6px;
        gap: 6px;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #6b7280;
        border-radius: 50px;
        padding: 10px 22px;
        font-weight: 600;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.35);
    }
    
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #fef7f0; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #ffb08a, #ff8c5a); border-radius: 10px; }
    
    .stSuccess {
        background: #f0fdf4 !important;
        border: 2px solid #86efac !important;
        color: #166534 !important;
        border-radius: 16px;
        font-weight: 600;
    }
    
    .stWarning {
        background: #fffbeb !important;
        border: 2px solid #fde047 !important;
        color: #a16207 !important;
        border-radius: 16px;
        font-weight: 600;
    }
    
    .stError {
        background: #fef2f2 !important;
        border: 2px solid #fca5a5 !important;
        color: #991b1b !important;
        border-radius: 16px;
        font-weight: 600;
    }
    
    .stInfo {
        background: #fff7ed !important;
        border: 2px solid #fdba74 !important;
        color: #c2410c !important;
        border-radius: 16px;
        font-weight: 600;
    }
    
    .stMarkdown p, .stMarkdown li { color: #4b5563; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1f2937; font-weight: 800; }
    
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    
    /* ====== 欢迎横幅 - 大圆角渐变边框 ====== */
    .welcome-banner {
        background: #ffffff;
        border-radius: 32px;
        border: none;
        padding: 36px 40px;
        margin-bottom: 30px;
        box-shadow: 0 12px 50px rgba(255, 120, 50, 0.1), 0 4px 15px rgba(0,0,0,0.03);
        position: relative;
        overflow: hidden;
    }
    
    .welcome-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #ff6b35, #f7931e, #ffb347, #ff6b35);
        background-size: 200% 100%;
    }
    
    .welcome-title {
        font-size: 26px;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 10px;
    }
    
    .welcome-subtitle {
        color: #6b7280;
        font-size: 15px;
        font-weight: 500;
    }
    
    .back-btn {
        background: #fff8f3;
        border: 2px solid #fde8dc;
        border-radius: 50px;
        padding: 10px 22px;
        color: #ff6b35;
        cursor: pointer;
        font-weight: 700;
    }
    
    .back-btn:hover { background: #fef0e7; border-color: #ffb08a; }
    
    .module-header {
        background: #ffffff;
        border-radius: 24px;
        border: none;
        padding: 22px 30px;
        margin-bottom: 24px;
        box-shadow: 0 8px 35px rgba(255, 120, 50, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .module-title {
        font-size: 24px;
        font-weight: 800;
        color: #1f2937;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .footer-info {
        text-align: center;
        color: #9ca3af;
        font-size: 12px;
        margin-top: 50px;
        padding: 20px;
        font-weight: 500;
    }
    
    .stSlider [data-baseweb="slider"] { background: #fde8dc; }
    .stSlider { padding-top: 0 !important; padding-bottom: 0 !important; }
    .stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] { display: none !important; }
    
    .stDataFrame {
        background: #ffffff;
        border-radius: 20px;
        overflow: hidden;
        border: 2px solid #fde8dc;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #ff6b35, #f7931e, #ffb347);
        border-radius: 50px;
    }
    
    .content-panel {
        background: #ffffff;
        border-radius: 24px;
        padding: 28px;
        margin: 18px 0;
        box-shadow: 0 8px 35px rgba(255, 120, 50, 0.08);
    }
    
    .panel-header {
        font-size: 17px;
        font-weight: 700;
        color: #1f2937;
        padding-bottom: 14px;
        border-bottom: 2px solid #fde8dc;
        margin-bottom: 18px;
    }
    
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: 700;
    }
    
    .badge-primary { background: #fff0e6; color: #ff6b35; }
    .badge-success { background: #ecfdf5; color: #059669; }
    .badge-warning { background: #fffbeb; color: #d97706; }
    
    /* ====== 特色装饰元素 ====== */
    .accent-dot {
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, #ff6b35, #f7931e);
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
    }
    
    .highlight-box {
        background: linear-gradient(135deg, rgba(255,107,53,0.08), rgba(247,147,30,0.08));
        border-radius: 20px;
        padding: 24px;
        border-left: 4px solid #ff6b35;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # 检查登录状态
    if not check_login():
        render_login_page()
        return
    
    # 获取当前用户
    user = get_current_user()
    
    # 显示欢迎消息（仅刚登录时）
    if st.session_state.get('just_logged_in', False):
        if user['role'] == 'student':
            st.success(f"🎓 欢迎，{user.get('name')}！")
        else:
            st.success(f"👨‍🏫 教师登录成功！")
        st.session_state['just_logged_in'] = False  # 清除标记
    
    # 顶部导航栏
    st.markdown(f"""
    <div class="top-nav">
        <div class="logo-section">
            <span class="logo-icon">📊</span>
            <div>
                <div class="logo-text">管理学自适应学习系统</div>
                <div class="logo-subtitle">MANAGEMENT AI LEARNING PLATFORM</div>
            </div>
        </div>
        <div class="user-info">
            <div class="user-avatar">{'👨‍🎓' if user['role'] == 'student' else '👨‍🏫'}</div>
            <div>
                <div class="user-name">{user.get('name', '教师')}</div>
                <div class="user-role">{'学生' if user['role'] == 'student' else '教师'}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化当前页面状态
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # 导航按钮行（教师端分两行）
    if user['role'] == 'teacher':
        # 第一行：数据分析
        st.markdown("##### 📊 数据分析")
        nav_cols_1 = st.columns([1, 1, 1, 1, 1])
        with nav_cols_1[0]:
            if st.button("🏠 首页", key="nav_home_t", use_container_width=True):
                st.session_state.current_page = 'home'
        with nav_cols_1[1]:
            if st.button("📚 案例库数据", key="nav_case_t", use_container_width=True):
                st.session_state.current_page = 'case_analytics'
        with nav_cols_1[2]:
            if st.button("🗺️ 图谱数据", key="nav_graph_t", use_container_width=True):
                st.session_state.current_page = 'graph_analytics'
        with nav_cols_1[3]:
            if st.button("🎯 推荐数据", key="nav_ability_t", use_container_width=True):
                st.session_state.current_page = 'ability_analytics'
        with nav_cols_1[4]:
            if st.button("💬 互动数据", key="nav_int_t", use_container_width=True):
                st.session_state.current_page = 'interaction_analytics'
        
        # 第二行：管理功能
        st.markdown("##### ⚙️ 管理功能")
        nav_cols_2 = st.columns([1, 1, 1, 1, 1])
        with nav_cols_2[0]:
            if st.button("📄 学习报告", key="nav_report_t", use_container_width=True):
                st.session_state.current_page = 'report_generator'
        with nav_cols_2[1]:
            if st.button("📐 教学设计", key="nav_teaching_t", use_container_width=True):
                st.session_state.current_page = 'teaching_design'
        with nav_cols_2[2]:
            if st.button("📊 数据管理", key="nav_data_t", use_container_width=True):
                st.session_state.current_page = 'data_management'
        with nav_cols_2[3]:
            if st.button("⚙️ 系统设置", key="nav_settings_t", use_container_width=True):
                st.session_state.current_page = 'system_settings'
        with nav_cols_2[4]:
            if st.button("🚪 退出登录", key="nav_logout_t", use_container_width=True):
                logout()
                st.rerun()
    else:
        nav_cols = st.columns([1, 1, 1, 1, 1, 1])
        with nav_cols[0]:
            if st.button("🏠 首页", key="nav_home", use_container_width=True):
                st.session_state.current_page = 'home'
        with nav_cols[1]:
            if st.button("📚 案例库", key="nav_case", use_container_width=True):
                st.session_state.current_page = 'case_library'
        with nav_cols[2]:
            if st.button("🗺️ 知识图谱", key="nav_graph", use_container_width=True):
                st.session_state.current_page = 'knowledge_graph'
        with nav_cols[3]:
            if st.button("📊 知识掌握", key="nav_ability", use_container_width=True):
                st.session_state.current_page = 'ability_recommender'
        with nav_cols[4]:
            if st.button("💬 课中互动", key="nav_int", use_container_width=True):
                st.session_state.current_page = 'classroom'
        with nav_cols[5]:
            if st.button("🚪 退出登录", key="nav_logout", use_container_width=True):
                logout()
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 根据当前页面渲染内容
    current = st.session_state.current_page
    
    # 使用错误处理防止页面卡住
    try:
        # 教师端直接显示数据概览
        if user['role'] == 'teacher':
            # 教师端直接显示数据概览
            if current == 'home':
                render_teacher_dashboard()
            elif current == 'case_analytics':
                render_module_analytics("案例库")
            elif current == 'graph_analytics':
                render_module_analytics("知识图谱")
            elif current == 'ability_analytics':
                render_module_analytics("知识点掌握评估")
            elif current == 'interaction_analytics':
                render_module_analytics("课中互动")
            elif current == 'report_generator':
                render_report_generator()
            elif current == 'teaching_design':
                render_teaching_design()
            elif current == 'data_management':
                render_data_management()
            elif current == 'system_settings':
                render_system_settings()
            else:
                render_teacher_dashboard()
        else:
            # 学生端
            if current == 'home':
                render_home_page(user)
            elif current == 'case_library':
                render_case_library()
            elif current == 'knowledge_graph':
                render_knowledge_graph()
            elif current == 'ability_recommender':
                render_ability_recommender()
            elif current == 'classroom':
                render_classroom_interaction()
            else:
                render_home_page(user)
    except Exception as e:
        st.error(f"⚠️ 页面加载出错：{str(e)}")
        st.info("请点击顶部导航按钮返回首页，或点击下方按钮重新尝试")
        if st.button("🏠 返回首页", type="primary"):
            st.session_state.current_page = 'home'
            st.rerun()

def render_teacher_dashboard():
    """渲染教师端数据概览首页"""
    try:
        import pandas as pd
        import plotly.express as px
        from modules.analytics import get_activity_summary, get_daily_activity_trend
        from modules.auth import check_neo4j_available, get_all_students, get_all_modules_statistics, get_single_module_statistics, get_neo4j_driver, get_neo4j_driver
        
        # 顶部标题和刷新按钮
        header_col1, header_col2 = st.columns([6, 1])
        with header_col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 16px; margin-bottom: 30px;">
                <h2 style="margin: 0; color: white;">📊 教学数据概览</h2>
                <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9);">
                    实时查看学生学习情况，掌握教学效果
                </p>
            </div>
            """, unsafe_allow_html=True)
        with header_col2:
            if st.button("🔄 刷新数据", key="refresh_teacher_data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        # 显示加载进度
        with st.spinner("正在加载数据..."):
            # 获取真实数据
            has_neo4j = check_neo4j_available()
            
            # 获取数据
            summary = get_activity_summary()
            all_students = get_all_students() if has_neo4j else []
    except Exception as e:
        st.error(f"⚠️ 教师端数据加载失败：{str(e)}")
        st.info("💡 提示：系统正在使用默认配置运行。如需连接数据库，请配置 config/settings.py 文件。")
        st.markdown("---")
        st.markdown("""
        ### 🏠 教师端功能
        - 📚 **案例库数据**: 查看学生案例学习情况
        - 🗺️ **图谱数据**: 分析知识图谱学习路径
        - 🎯 **推荐数据**: 查看知识掌握评估效果
        - 💬 **互动数据**: 查看课堂互动统计
        
        请使用顶部导航栏访问各功能模块。
        """)
        return
    
    # 计算统计数据
    total_students = summary.get('total_students', 0)
    today_active = summary.get('today_activities', 0)
    active_7d = summary.get('active_students', 0)
    total_acts = summary.get('total_activities', 0)
    
    # 调试信息（可以在终端看到）
    print(f"[教师端调试] Neo4j可用: {has_neo4j}")
    print(f"[教师端调试] 学生总数: {total_students}, 今日活跃: {today_active}, 7日活跃: {active_7d}, 总活动: {total_acts}")
    
    # 显示详细调试信息在页面上
    with st.expander("🔍 调试信息（点击展开）", expanded=False):
        st.write("**数据库连接状态:**")
        st.write(f"- Neo4j可用: {has_neo4j}")
        
        # 显示 secrets 中所有可用的 keys
        from modules.auth import get_all_secret_keys
        all_keys = get_all_secret_keys()
        st.write(f"**所有 secrets keys:** `{all_keys}`")
        
        # 安全地检查环境变量
        try:
            st.write(f"- 环境变量检查: NEO4J_URI={'已设置' if st.secrets.get('NEO4J_URI') else '未设置'}")
            st.write(f"- 环境变量检查: NEO4J_USER={'已设置' if st.secrets.get('NEO4J_USER') else '未设置'}")
            st.write(f"- 环境变量检查: NEO4J_USERNAME={'已设置' if st.secrets.get('NEO4J_USERNAME') else '未设置'}")
            st.write(f"- 环境变量检查: NEO4J_PASSWORD={'已设置' if st.secrets.get('NEO4J_PASSWORD') else '未设置'}")
        except Exception as e:
            st.write(f"- 环境变量检查失败（可能未配置secrets.toml）: {str(e)}")
            st.info("💡 系统将使用 config/settings.py 中的配置")
        
        if not has_neo4j:
            from modules.auth import get_neo4j_error
            error_msg = get_neo4j_error()
            st.error(f"**连接失败原因:** {error_msg}")
            
            # 显示secrets的实际值（仅用于调试）
            try:
                uri = st.secrets.get('NEO4J_URI', '未设置')
                user = st.secrets.get('NEO4J_USER') or st.secrets.get('NEO4J_USERNAME') or '未设置'
                # 不显示完整密码，只显示是否为空
                pwd_status = '已设置且非空' if st.secrets.get('NEO4J_PASSWORD') else '未设置或为空'
                st.write(f"- NEO4J_URI值: `{uri}`")
                st.write(f"- NEO4J_USER/USERNAME值: `{user}`")
                st.write(f"- NEO4J_PASSWORD状态: {pwd_status}")
            except Exception as e:
                st.write(f"- 读取secrets失败: {e}")
                st.write("- 将使用 config/settings.py 中的配置")
        
        st.write("**查询结果:**")
        st.write(f"- summary数据: {summary}")
        st.write(f"- 学生列表长度: {len(all_students)}")
        if len(all_students) > 0:
            st.write(f"- 前3个学生: {all_students[:3]}")
        
        st.write("**计算的统计数据:**")
        st.write(f"- 学生总数: {total_students}")
        st.write(f"- 今日活跃: {today_active}")
        st.write(f"- 7日活跃学生: {active_7d}")
        st.write(f"- 总学习记录: {total_acts}")
    
    # 只在真正无数据时提示（避免本地开发时误报）
    if total_students == 0 and not has_neo4j:
        st.info("💡 提示：当前无学生数据。学生登录使用后即可在此查看学习统计。")
    
    # 核心数据指标 - 使用真实数据
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("👥 学生总数", str(total_students))
    with col2:
        st.metric("📚 今日活跃", str(today_active))
    with col3:
        st.metric("👨‍🎓 7日活跃学生", str(active_7d))
    with col4:
        if has_neo4j:
            completion_rate = int((active_7d / total_students * 100)) if total_students > 0 else 0
            st.metric("✅ 7日活跃率", f"{completion_rate}%")
        else:
            st.metric("✅ 7日活跃率", "0%")
    with col5:
        st.metric("📝 总学习记录", str(total_acts))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 四个模块数据概览 - 调用真实数据
    st.markdown("### 📈 各模块学习数据")
    
    modules = ["案例库", "知识图谱", "知识点掌握评估", "课中互动"]
    module_cols = st.columns(4)
    
    # 一次性获取所有模块统计（性能优化）
    all_module_stats = {}
    if has_neo4j:
        from modules.auth import get_all_modules_statistics
        all_module_stats = get_all_modules_statistics()
        
        # 调试：显示模块统计信息
        with st.expander("🔍 模块统计调试信息", expanded=False):
            st.write("**所有模块统计数据:**")
            st.json(all_module_stats)
        
    for i, module in enumerate(modules):
        with module_cols[i]:
            if has_neo4j and module in all_module_stats:
                stats = all_module_stats[module]
                visit_count = stats.get('total_visits', 0)
                student_count = stats.get('unique_students', 0)
                completion = int((student_count / total_students * 100)) if total_students > 0 else 0
                print(f"[教师端调试] {module}: 访问{visit_count}次, 学生{student_count}人, 参与率{completion}%")
            else:
                visit_count = 0
                completion = 0
                
            st.markdown(f"""
            <div style="background: #fff; border-radius: 12px; padding: 20px; 
                        border: 1px solid rgba(102,126,234,0.2); text-align: center;">
                <h4 style="color: #667eea; margin-bottom: 15px;">{module}</h4>
                <div style="font-size: 24px; font-weight: 600; color: #333;">{visit_count}</div>
                <div style="color: #888; font-size: 13px;">学习人次</div>
                <hr style="margin: 15px 0; border: none; border-top: 1px solid #eee;">
                <div style="display: flex; justify-content: space-between; font-size: 13px;">
                    <span>学生参与率</span>
                    <span style="color: #667eea; font-weight: 600;">{completion}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 图表区域 - 使用真实数据
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("### 📊 近7天学习趋势")
        if has_neo4j:
            trend_data = get_daily_activity_trend(7)
            if trend_data:
                df = pd.DataFrame(trend_data)
                fig = px.line(df, x="date", y="count", markers=True, 
                            labels={"date": "日期", "count": "活动数"})
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无近7天数据")
        else:
            st.info("需要连接数据库查看趋势")
    
    with chart_col2:
        st.markdown("### 🥧 学生学习模块分布")
        if has_neo4j:
            # 统计每个模块的访问学生数
            module_data = []
            for module in modules:
                stats = get_single_module_statistics(module)
                module_data.append({
                    "模块": module,
                    "学生数": stats.get('unique_students', 0)
                })
            
            if any(m['学生数'] > 0 for m in module_data):
                progress_df = pd.DataFrame(module_data)
                fig = px.pie(progress_df, values="学生数", names="模块", 
                            color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#4facfe'])
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无模块访问数据")
        else:
            st.info("需要连接数据库查看分布")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 学生排行榜 - 使用真实数据
    st.markdown("### 🏆 学习排行榜 (Top 10)")
    
    if has_neo4j:
        # 从数据库获取学生活动统计
        try:
            driver = get_neo4j_driver()
            with driver.session() as session:
                result = session.run("""
                    MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                    RETURN s.student_id as student_id, 
                           s.name as name,
                           count(a) as activity_count,
                           count(DISTINCT date(a.timestamp)) as active_days
                    ORDER BY activity_count DESC
                    LIMIT 10
                """)
                
                leaderboard = []
                for i, record in enumerate(result):
                    leaderboard.append({
                        "排名": "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else str(i+1))),
                        "学号": record['student_id'],
                        "姓名": record['name'] if record['name'] else "未设置",
                        "学习记录数": record['activity_count'],
                        "活跃天数": record['active_days']
                    })
                
                if leaderboard:
                    st.dataframe(pd.DataFrame(leaderboard), use_container_width=True, hide_index=True)
                else:
                    st.info("暂无学生学习数据")
        except Exception as e:
            st.error(f"获取排行榜数据失败: {e}")
    else:
        st.info("需要连接数据库查看学生排行榜")

def render_home_page(user):
    """渲染首页"""
    # 导入必要的函数
    from modules.auth import check_neo4j_available, get_neo4j_driver
    
    # 获取真实统计数据
    from data.cases import get_cases
    from data.abilities import ABILITIES
    
    # 案例数量 - 从cases.py获取真实数量
    case_count = len(get_cases())
    
    # 知识点数量 - 从数据库获取
    knowledge_points = 0
    if check_neo4j_available():
        try:
            driver = get_neo4j_driver()
            with driver.session() as session:
                result = session.run("MATCH (k:glx_Knowledge) RETURN count(k) as count")
                knowledge_points = result.single()['count']
        except:
            knowledge_points = 0
    
    # 核心能力数量 - 从abilities.py获取
    core_abilities = len(ABILITIES) if ABILITIES else 0
    
    # 欢迎横幅
    st.markdown(f"""
    <div class="welcome-banner">
        <div class="welcome-title">👋 欢迎回来，{user.get('name', '用户')}！</div>
        <div class="welcome-subtitle">今天想学习什么？选择下方功能模块开始你的学习之旅</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 统计卡片 - 使用真实数据
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{case_count}</div>
            <div class="stat-label">📚 案例总数</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_cols[1]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{knowledge_points}</div>
            <div class="stat-label">🧠 知识点</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_cols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{core_abilities}</div>
            <div class="stat-label">🎯 核心能力</div>
        </div>
        """, unsafe_allow_html=True)
    with stat_cols[3]:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">AI</div>
            <div class="stat-label">🤖 智能推荐</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 功能模块标题
    st.markdown("""
    <div class="page-title">
        <span>🚀</span> 
        <span class="gradient-text">功能模块</span>
    </div>
    <div class="page-subtitle">选择一个模块开始学习，AI将为你提供个性化的学习体验</div>
    """, unsafe_allow_html=True)
    
    # 功能模块卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card glow">
            <span class="feature-icon">📚</span>
            <div class="feature-title">智能案例库</div>
            <div class="feature-desc">真实管理案例学习<br>AI辅助分析<br>掌握管理思维与方法</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入案例库", key="btn_case", use_container_width=True):
            st.session_state.current_page = 'case_library'
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🗺️</span>
            <div class="feature-title">知识图谱</div>
            <div class="feature-desc">可视化知识网络<br>理清知识脉络<br>构建管理学知识体系</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入图谱", key="btn_graph", use_container_width=True):
            st.session_state.current_page = 'knowledge_graph'
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <div class="feature-title">知识掌握评估</div>
            <div class="feature-desc">评估知识点掌握程度<br>AI智能推荐<br>规划个性化学习路径</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入推荐", key="btn_ability", use_container_width=True):
            st.session_state.current_page = 'ability_recommender'
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💬</span>
            <div class="feature-title">课中互动</div>
            <div class="feature-desc">实时投票弹幕<br>AI智能答疑<br>提升课堂参与度</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入互动", key="btn_class", use_container_width=True):
            st.session_state.current_page = 'classroom'
    
    # 技术栈展示
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="footer-info">
        <div style="margin-bottom: 15px;">
            <span style="padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border-radius: 20px; margin: 0 5px; display: inline-block;">🤖 DeepSeek AI</span>
            <span style="padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border-radius: 20px; margin: 0 5px; display: inline-block;">📊 Neo4j</span>
            <span style="padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border-radius: 20px; margin: 0 5px; display: inline-block;">🔍 Elasticsearch</span>
            <span style="padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; border-radius: 20px; margin: 0 5px; display: inline-block;">⚡ Streamlit</span>
        </div>
        © 2026 管理学自适应学习系统 · Powered by AI Technology
    </div>
    """, unsafe_allow_html=True)

def render_module_analytics(module_name):
    """渲染教师端模块数据分析页面"""
    from modules.auth import check_neo4j_available, get_all_students, get_student_activities, get_single_module_statistics, get_neo4j_driver
    import pandas as pd
    
    # 先显示标题
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 25px; border-radius: 16px; margin-bottom: 30px;">
        <h2 style="margin: 0; color: white;">📊 {module_name} - 数据分析</h2>
        <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9);">
            查看学生在该模块的学习情况和整体数据统计
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用spinner显示加载状态
    with st.spinner("正在加载数据..."):
        has_neo4j = check_neo4j_available()
    
    # 调试信息面板
    with st.expander("🔧 调试信息（点击展开）", expanded=False):
        st.markdown("**连接状态检查：**")
        st.write(f"- Neo4j可用: `{has_neo4j}`")
        
        if has_neo4j:
            try:
                from modules.analytics import get_activity_summary
                summary = get_activity_summary()
                st.write(f"- 学生总数: `{summary.get('total_students', 0)}`")
                st.write(f"- 活动总数: `{summary.get('total_activities', 0)}`")
                
                all_students_debug = get_all_students()
                st.write(f"- get_all_students返回: `{len(all_students_debug)}` 条记录")
                
                stats = get_single_module_statistics(module_name)
                st.write(f"- {module_name}统计: `{stats}`")
            except Exception as e:
                st.error(f"查询出错: {e}")
        else:
            st.warning("Neo4j不可用，无法获取数据")
    
    # 选项卡：个人数据 / 整体数据
    tab1, tab2 = st.tabs(["👤 学生个人数据", "📈 整体统计数据"])
    
    with tab1:
        st.markdown("### 🔍 查询学生学习数据")
        
        # 获取真实学生列表
        all_students = get_all_students() if has_neo4j else []
        if not all_students:
            st.info("💡 当前暂无学生数据。学生注册登录后，数据会自动显示在此处。")
            # 不要return，让tab2可以继续显示
        else:
            student_options = {f"学生 {s['student_id']} (活动数: {s.get('activity_count', 0)})": s['student_id'] 
                              for s in all_students}
            
            selected_display = st.selectbox("选择学生", list(student_options.keys()), key=f"select_{module_name}")
            selected_student_id = student_options[selected_display]
            
            if selected_student_id:
                # 获取该学生在该模块的活动记录
                activities = get_student_activities(selected_student_id, module_name)
            
                st.markdown(f"#### 学生 {selected_student_id} 的{module_name}学习数据")
                
                # 统计数据
                total_activities = len(activities)
                # 从timestamp提取日期
                unique_dates = set()
                for a in activities:
                    if 'timestamp' in a and a['timestamp']:
                        try:
                            # timestamp格式: "2025-01-01 10:30:00"
                            date_str = str(a['timestamp']).split(' ')[0]
                            unique_dates.add(date_str)
                        except:
                            pass
                unique_days = len(unique_dates)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("学习记录数", str(total_activities))
                with col2:
                    st.metric("活跃天数", str(unique_days))
                with col3:
                    avg_per_day = round(total_activities / unique_days, 1) if unique_days > 0 else 0
                    st.metric("日均记录数", str(avg_per_day))
                
                # 学习记录列表
                if activities:
                    st.markdown("##### 📋 最近学习记录 (最新10条)")
                    records = []
                    for act in activities[:10]:
                        records.append({
                            "时间": act['timestamp'],
                            "活动类型": act['activity_type'],
                            "内容": act.get('content_name', '-'),
                            "详情": act.get('details', '-')
                        })
                    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
                else:
                    st.info(f"该学生暂无{module_name}学习记录")
    
    with tab2:
        st.markdown("### 📊 整体统计数据")
        
        # 获取模块统计数据
        stats = get_single_module_statistics(module_name)
        
        # 整体统计卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats.get('unique_students', 0)}</div>
                <div class="stat-label">👥 学习学生数</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats.get('total_visits', 0)}</div>
                <div class="stat-label">📝 总访问次数</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats.get('avg_visits_per_student', 0)}</div>
                <div class="stat-label">📊 人均访问次数</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats.get('recent_7d_visits', 0)}</div>
                <div class="stat-label">🔥 近7日访问</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 显示活跃学生排行
        st.markdown(f"#### 🏆 {module_name}学习排行榜")
        try:
            driver = get_neo4j_driver()
            with driver.session() as session:
                result = session.run("""
                    MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                    WHERE COALESCE(a.module_name, a.module) = $module_name
                    RETURN s.student_id as student_id, 
                           count(a) as activity_count
                    ORDER BY activity_count DESC
                    LIMIT 10
                """, module_name=module_name)
                
                ranking = []
                for i, record in enumerate(result):
                    ranking.append({
                        "排名": "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else str(i+1))),
                        "学号": record['student_id'],
                        "学习记录数": record['activity_count']
                    })
                
                if ranking:
                    st.dataframe(pd.DataFrame(ranking), use_container_width=True, hide_index=True)
                else:
                    st.info(f"暂无{module_name}学习数据")
        except Exception as e:
            st.error(f"获取排行数据失败: {e}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 图表展示
        import plotly.express as px
        import pandas as pd
        
        # 近7天学习人数趋势
        st.markdown("##### 📈 近7天学习人数趋势")
        if has_neo4j:
            try:
                from modules.analytics import get_daily_activity_trend
                trend_data = get_daily_activity_trend(7)
                if trend_data:
                    df = pd.DataFrame(trend_data)
                    # 确保日期是字符串格式（已在函数中转换）
                    fig = px.line(df, x="date", y="count", markers=True)
                    fig.update_traces(line_color='#667eea')
                    fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="日期", yaxis_title="活动数")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无近7天数据")
            except Exception as e:
                st.error(f"加载趋势数据失败: {e}")
        else:
            st.info("需要连接数据库查看趋势")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 学生排行榜
        st.markdown("##### 🏆 学习排行榜 (Top 10)")
        if has_neo4j:
            try:
                driver = get_neo4j_driver()
                with driver.session() as session:
                    result = session.run("""
                        MATCH (s:mfx_Student)-[:PERFORMED]->(a:mfx_Activity)
                        WHERE COALESCE(a.module_name, a.module) = $module_name
                        RETURN s.student_id as student_id, 
                               count(a) as activity_count
                        ORDER BY activity_count DESC
                        LIMIT 10
                    """, module_name=module_name)
                    
                    leaderboard = []
                    for i, record in enumerate(result):
                        leaderboard.append({
                            "排名": "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else str(i+1))),
                            "学号": record['student_id'],
                            "学习记录数": record['activity_count']
                        })
                    
                    if leaderboard:
                        st.dataframe(pd.DataFrame(leaderboard), use_container_width=True, hide_index=True)
                    else:
                        st.info(f"暂无{module_name}学习数据")
            except Exception as e:
                st.error(f"获取排行榜失败: {e}")
        else:
            st.info("需要连接数据库查看排行榜")

def render_data_management():
    """渲染数据管理页面"""
    import pandas as pd
    import io
    from modules.auth import get_neo4j_driver, check_neo4j_available
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 16px; margin-bottom: 30px;">
        <h2 style="margin: 0; color: white;">📊 数据管理中心</h2>
        <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9);">
            导出、查看和管理系统数据
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    has_neo4j = check_neo4j_available()
    
    if not has_neo4j:
        st.warning("⚠️ 数据库连接不可用，无法进行数据管理操作")
        return
    
    # 创建选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["📥 数据导出", "👥 学生管理", "📝 活动记录管理", "🔧 数据修复"])
    
    # ===== 数据导出 =====
    with tab1:
        st.markdown("### 📥 导出数据")
        st.info("💡 选择需要导出的数据类型，点击下载按钮即可获取CSV文件")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 学生数据导出")
            if st.button("📥 导出所有学生数据", key="export_students", use_container_width=True):
                with st.spinner("正在导出学生数据..."):
                    try:
                        driver = get_neo4j_driver()
                        with driver.session() as session:
                            result = session.run("""
                                MATCH (s:mfx_Student)
                                OPTIONAL MATCH (s)-[r:PERFORMED]->(a:mfx_Activity)
                                WITH s, count(r) as activity_count, 
                                     max(a.timestamp) as last_activity
                                RETURN s.student_id as 学号, 
                                       s.name as 姓名,
                                       COALESCE(s.login_count, 0) as 登录次数,
                                       activity_count as 学习记录数,
                                       toString(s.last_login) as 最后登录时间,
                                       toString(last_activity) as 最后学习时间
                                ORDER BY s.student_id
                            """)
                            data = [dict(record) for record in result]
                        
                        if data:
                            df = pd.DataFrame(data)
                            csv = df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="⬇️ 下载学生数据 CSV",
                                data=csv,
                                file_name=f"学生数据_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key="download_students"
                            )
                            st.success(f"✅ 成功导出 {len(data)} 条学生记录")
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.warning("没有找到学生数据")
                    except Exception as e:
                        st.error(f"导出失败: {e}")
        
        with col2:
            st.markdown("#### 📝 学习记录导出")
            if st.button("📥 导出所有学习记录", key="export_activities", use_container_width=True):
                with st.spinner("正在导出学习记录..."):
                    try:
                        driver = get_neo4j_driver()
                        with driver.session() as session:
                            result = session.run("""
                                MATCH (s:mfx_Student)-[r:PERFORMED]->(a:mfx_Activity)
                                RETURN s.student_id as 学号,
                                       s.name as 姓名,
                                       COALESCE(a.module_name, a.module) as 学习模块,
                                       COALESCE(a.activity_type, a.type) as 活动类型,
                                       a.content_name as 内容名称,
                                       toString(a.timestamp) as 学习时间,
                                       a.details as 详情
                                ORDER BY a.timestamp DESC
                            """)
                            data = [dict(record) for record in result]
                        
                        if data:
                            df = pd.DataFrame(data)
                            csv = df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="⬇️ 下载学习记录 CSV",
                                data=csv,
                                file_name=f"学习记录_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key="download_activities"
                            )
                            st.success(f"✅ 成功导出 {len(data)} 条学习记录")
                            st.dataframe(df.head(100), use_container_width=True)
                            if len(data) > 100:
                                st.info(f"预览显示前100条，共{len(data)}条记录")
                        else:
                            st.warning("没有找到学习记录")
                    except Exception as e:
                        st.error(f"导出失败: {e}")
        
        st.markdown("---")
        
        # 按模块导出
        st.markdown("#### 📂 按模块导出学习记录")
        
        # 添加调试工具
        with st.expander("🔧 调试工具：查看数据库中的模块名称", expanded=False):
            try:
                driver = get_neo4j_driver()
                with driver.session() as session:
                    # 查询所有不同的模块名称(兼容新旧字段)
                    result = session.run("""
                        MATCH (a:mfx_Activity)
                        RETURN DISTINCT COALESCE(a.module_name, a.module) as module_name, count(a) as count
                        ORDER BY count DESC
                    """)
                    module_stats = [dict(record) for record in result]
                
                if module_stats:
                    st.write("**数据库中实际存储的模块名称及记录数：**")
                    for stat in module_stats:
                        st.write(f"- `{stat['module_name']}`: {stat['count']}条记录")
                    
                    # 检查模块名称匹配情况
                    st.write("**匹配检查：**")
                    db_modules = [s['module_name'] for s in module_stats]
                    expected_modules = ["案例库", "知识图谱", "知识点掌握评估", "课中互动"]
                    for expected in expected_modules:
                        if expected in db_modules:
                            st.success(f"✅ `{expected}` - 匹配成功")
                        else:
                            st.error(f"❌ `{expected}` - 未在数据库中找到")
                else:
                    st.warning("数据库中没有任何活动记录")
            except Exception as e:
                st.error(f"调试查询失败: {e}")
        
        # 初始化 session_state（必须在使用之前）
        if 'selected_export_module' not in st.session_state:
            st.session_state.selected_export_module = None
        
        module_col1, module_col2, module_col3, module_col4 = st.columns(4)
        
        modules = ["案例库", "知识图谱", "知识点掌握评估", "课中互动"]
        selected_module = None
        
        for i, module in enumerate(modules):
            with [module_col1, module_col2, module_col3, module_col4][i]:
                if st.button(f"📥 {module}", key=f"export_btn_{module}", use_container_width=True):
                    selected_module = module
                    st.session_state.selected_export_module = module
        
        display_module = selected_module or st.session_state.selected_export_module
        
        # 如果选择了模块，执行导出
        if display_module:
            st.markdown(f"**正在查看：{display_module}**")
            with st.spinner(f"正在加载{display_module}数据..."):
                try:
                    driver = get_neo4j_driver()
                    with driver.session() as session:
                        # 添加调试信息
                        st.write(f"🔍 查询参数: module_name = `{display_module}`")
                        
                        result = session.run("""
                            MATCH (s:mfx_Student)-[r:PERFORMED]->(a:mfx_Activity)
                            WHERE COALESCE(a.module_name, a.module) = $module
                            RETURN s.student_id as 学号,
                                   s.name as 姓名,
                                   COALESCE(a.activity_type, a.type) as 活动类型,
                                   a.content_name as 内容名称,
                                   toString(a.timestamp) as 学习时间,
                                   a.details as 详情
                            ORDER BY a.timestamp DESC
                        """, module=display_module)
                        data = [dict(record) for record in result]
                        
                        st.write(f"🔍 查询结果: {len(data)}条记录")
                    
                    if data:
                        df = pd.DataFrame(data)
                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        
                        st.success(f"✅ {display_module}记录: {len(data)}条")
                        st.dataframe(df.head(50), use_container_width=True)
                        if len(data) > 50:
                            st.info(f"预览显示前50条，共{len(data)}条记录")
                        
                        st.download_button(
                            label=f"⬇️ 下载{display_module}数据 CSV",
                            data=csv,
                            file_name=f"{display_module}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            key=f"download_{display_module}_csv"
                        )
                    else:
                        st.warning(f"{display_module}暂无数据")
                        st.info("💡 提示：展开上方的'调试工具'查看数据库中实际的模块名称")
                except Exception as e:
                    st.error(f"导出失败: {e}")
    
    # ===== 学生管理 =====
    with tab2:
        st.markdown("### 👥 学生管理")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📋 学生列表")
            try:
                driver = get_neo4j_driver()
                with driver.session() as session:
                    result = session.run("""
                        MATCH (s:mfx_Student)
                        OPTIONAL MATCH (s)-[r:PERFORMED]->(a:mfx_Activity)
                        WITH s, count(r) as activity_count
                        RETURN s.student_id as student_id,
                               s.name as name,
                               activity_count
                        ORDER BY s.student_id
                    """)
                    students = [dict(record) for record in result]
                
                if students:
                    df = pd.DataFrame(students)
                    df.columns = ['学号', '姓名', '学习记录数']
                    st.dataframe(df, use_container_width=True)
                    st.info(f"📊 共 {len(students)} 名学生")
                else:
                    st.warning("暂无学生数据")
            except Exception as e:
                st.error(f"获取学生列表失败: {e}")
        
        with col2:
            st.markdown("#### 🗑️ 删除学生")
            st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
            
            student_id_to_delete = st.text_input("输入要删除的学号", key="delete_student_id")
            
            if st.button("🗑️ 删除该学生", key="delete_student_btn", type="primary"):
                if student_id_to_delete:
                    if st.session_state.get('confirm_delete') != student_id_to_delete:
                        st.session_state.confirm_delete = student_id_to_delete
                        st.warning(f"⚠️ 确认删除学号为 {student_id_to_delete} 的学生？再次点击确认删除。")
                    else:
                        try:
                            driver = get_neo4j_driver()
                            with driver.session() as session:
                                # 先删除关联的活动记录
                                session.run("""
                                    MATCH (s:mfx_Student {student_id: $student_id})-[r:PERFORMED]->(a:mfx_Activity)
                                    DELETE r, a
                                """, student_id=student_id_to_delete)
                                
                                # 再删除学生节点
                                result = session.run("""
                                    MATCH (s:mfx_Student {student_id: $student_id})
                                    DELETE s
                                    RETURN count(s) as deleted_count
                                """, student_id=student_id_to_delete)
                                
                                deleted = result.single()['deleted_count']
                                
                            if deleted > 0:
                                st.success(f"✅ 已删除学号 {student_id_to_delete} 及其所有学习记录")
                                st.session_state.confirm_delete = None
                                st.rerun()
                            else:
                                st.error(f"未找到学号为 {student_id_to_delete} 的学生")
                        except Exception as e:
                            st.error(f"删除失败: {e}")
                else:
                    st.warning("请输入学号")
    
    # ===== 活动记录管理 =====
    with tab3:
        st.markdown("### 📝 活动记录管理")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### 📊 最近活动记录")
            try:
                driver = get_neo4j_driver()
                with driver.session() as session:
                    result = session.run("""
                        MATCH (s:mfx_Student)-[r:PERFORMED]->(a:mfx_Activity)
                        RETURN s.student_id as 学号,
                               a.module_name as 模块,
                               a.activity_type as 类型,
                               toString(a.timestamp) as 时间
                        ORDER BY a.timestamp DESC
                        LIMIT 100
                    """)
                    activities = [dict(record) for record in result]
                
                if activities:
                    df = pd.DataFrame(activities)
                    st.dataframe(df, use_container_width=True)
                    st.info(f"显示最近100条记录")
                else:
                    st.warning("暂无活动记录")
            except Exception as e:
                st.error(f"获取活动记录失败: {e}")
        
        with col2:
            st.markdown("#### 🗑️ 清除数据")
            st.error("⚠️ 危险操作区域")
            
            if st.button("🗑️ 清除所有学习记录", key="clear_all_activities", type="primary"):
                if st.session_state.get('confirm_clear_activities') != True:
                    st.session_state.confirm_clear_activities = True
                    st.warning("⚠️ 将删除所有学习记录（不删除学生）！再次点击确认。")
                else:
                    try:
                        driver = get_neo4j_driver()
                        with driver.session() as session:
                            # 先统计数量
                            count_result = session.run("MATCH (a:mfx_Activity) RETURN count(a) as count")
                            deleted = count_result.single()['count']
                            # 再删除
                            session.run("MATCH (a:mfx_Activity) DETACH DELETE a")
                        
                        # 清除相关缓存
                        st.cache_data.clear()
                        
                        st.success(f"✅ 已清除 {deleted} 条学习记录，缓存已清空")
                        st.session_state.confirm_clear_activities = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"清除失败: {e}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("🗑️ 清除所有数据", key="clear_all_data", type="primary"):
                if st.session_state.get('confirm_clear_all') != True:
                    st.session_state.confirm_clear_all = True
                    st.error("⚠️ 将删除所有学生和学习记录！再次点击确认。")
                else:
                    try:
                        driver = get_neo4j_driver()
                        with driver.session() as session:
                            # 先统计数量
                            count_result = session.run("""
                                MATCH (n)
                                WHERE n:mfx_Student OR n:mfx_Activity
                                RETURN count(n) as count
                            """)
                            deleted = count_result.single()['count']
                            # 再删除
                            session.run("""
                                MATCH (n)
                                WHERE n:mfx_Student OR n:mfx_Activity
                                DETACH DELETE n
                            """)
                        
                        # 清除相关缓存
                        st.cache_data.clear()
                        
                        st.success(f"✅ 已清除 {deleted} 个节点（学生和活动记录），缓存已清空")
                        st.session_state.confirm_clear_all = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"清除失败: {e}")
    
    # ===== 数据修复 =====
    with tab4:
        st.markdown("### 🔧 数据修复工具")
        st.warning("⚠️ 此工具用于修复历史数据中的字段不一致问题")
        
        st.markdown("#### 问题诊断")
        
        try:
            driver = get_neo4j_driver()
            with driver.session() as session:
                # 检查 module 字段（旧字段名）
                result1 = session.run("""
                    MATCH (a:mfx_Activity)
                    WHERE a.module IS NOT NULL
                    RETURN count(a) as count
                """)
                old_field_count = result1.single()['count']
                
                # 检查 module_name 字段（新字段名）
                result2 = session.run("""
                    MATCH (a:mfx_Activity)
                    WHERE a.module_name IS NOT NULL
                    RETURN count(a) as count
                """)
                new_field_count = result2.single()['count']
                
                # 检查 activity_type 字段
                result3 = session.run("""
                    MATCH (a:mfx_Activity)
                    WHERE a.activity_type IS NOT NULL
                    RETURN count(a) as count
                """)
                activity_type_count = result3.single()['count']
                
                # 检查 type 字段（旧字段名）
                result4 = session.run("""
                    MATCH (a:mfx_Activity)
                    WHERE a.type IS NOT NULL
                    RETURN count(a) as count
                """)
                old_type_count = result4.single()['count']
                
                st.write("**字段使用情况：**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("使用旧字段 'module' 的记录", old_field_count)
                    st.metric("使用新字段 'module_name' 的记录", new_field_count)
                with col2:
                    st.metric("使用旧字段 'type' 的记录", old_type_count)
                    st.metric("使用新字段 'activity_type' 的记录", activity_type_count)
                
                if old_field_count > 0 or old_type_count > 0:
                    st.error(f"⚠️ 发现 {old_field_count} 条使用旧字段名的记录，需要修复")
                    
                    if st.button("🔧 修复历史数据字段名", key="fix_fields", type="primary"):
                        with st.spinner("正在修复数据..."):
                            try:
                                # 修复 module -> module_name
                                session.run("""
                                    MATCH (a:mfx_Activity)
                                    WHERE a.module IS NOT NULL
                                    SET a.module_name = a.module
                                    REMOVE a.module
                                """)
                                
                                # 修复 type -> activity_type
                                session.run("""
                                    MATCH (a:mfx_Activity)
                                    WHERE a.type IS NOT NULL
                                    SET a.activity_type = a.type
                                    REMOVE a.type
                                """)
                                
                                st.success("✅ 字段名修复完成！")
                                st.info("💡 页面将在3秒后刷新...")
                                import time
                                time.sleep(3)
                                st.rerun()
                            except Exception as e:
                                st.error(f"修复失败: {e}")
                else:
                    st.success("✅ 所有数据字段名正确，无需修复")
                    
        except Exception as e:
            st.error(f"诊断失败: {e}")

def render_system_settings():
    """渲染系统设置页面（仅教师可用）"""
    st.title("⚙️ 系统设置")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 12px; margin-bottom: 30px;">
        <h3 style="margin: 0; color: white;">📊 首页统计数据设置</h3>
        <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9);">
            设置首页展示的统计数据，这些数据将显示给所有学生
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 读取当前配置
    import json
    try:
        with open('config/stats_config.json', 'r', encoding='utf-8') as f:
            stats = json.load(f)
    except:
        stats = {"case_count": 12, "knowledge_points": 45, "core_abilities": 10}
    
    # 编辑表单
    with st.form("stats_form"):
        st.markdown("### 📝 编辑统计数据")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            case_count = st.number_input(
                "📚 病例总数", 
                min_value=0, 
                value=stats.get("case_count", 12),
                step=1,
                help="设置系统中的病例总数"
            )
        
        with col2:
            knowledge_points = st.number_input(
                "🧠 知识点数量", 
                min_value=0, 
                value=stats.get("knowledge_points", 45),
                step=1,
                help="设置系统中的知识点数量"
            )
        
        with col3:
            core_abilities = st.number_input(
                "🎯 核心能力数", 
                min_value=0, 
                value=stats.get("core_abilities", 10),
                step=1,
                help="设置系统中的核心能力数量"
            )
        
        submitted = st.form_submit_button("💾 保存设置", use_container_width=True, type="primary")
        
        if submitted:
            new_stats = {
                "case_count": int(case_count),
                "knowledge_points": int(knowledge_points),
                "core_abilities": int(core_abilities)
            }
            
            try:
                with open('config/stats_config.json', 'w', encoding='utf-8') as f:
                    json.dump(new_stats, f, ensure_ascii=False, indent=4)
                st.success("✅ 设置已保存！学生在首页将看到更新后的数据。")
            except Exception as e:
                st.error(f"❌ 保存失败：{str(e)}")
    
    # 当前设置预览
    st.markdown("---")
    st.markdown("### 👀 当前设置预览")
    
    preview_cols = st.columns(3)
    with preview_cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('case_count', 12)}</div>
            <div class="stat-label">📚 病例总数</div>
        </div>
        """, unsafe_allow_html=True)
    with preview_cols[1]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('knowledge_points', 45)}</div>
            <div class="stat-label">🧠 知识点</div>
        </div>
        """, unsafe_allow_html=True)
    with preview_cols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats.get('core_abilities', 10)}</div>
            <div class="stat-label">🎯 核心能力</div>
        </div>
        """, unsafe_allow_html=True)

# 确保 session_state 在程序开始时就被初始化
def init_session_state():
    """初始化所有 session_state 变量"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'selected_export_module' not in st.session_state:
        st.session_state.selected_export_module = None
    if 'just_logged_in' not in st.session_state:
        st.session_state.just_logged_in = False
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = None
    if 'confirm_clear_activities' not in st.session_state:
        st.session_state.confirm_clear_activities = False
    if 'confirm_clear_all' not in st.session_state:
        st.session_state.confirm_clear_all = False

if __name__ == "__main__":
    # 先初始化 session_state
    init_session_state()
    # 再运行主程序
    main()

