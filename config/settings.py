"""
配置文件
存储数据库连接信息和API密钥
支持本地开发和Streamlit Cloud部署
"""

import os

# 尝试导入streamlit获取secrets（部署环境）
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def get_secret(key, default=None):
    """
    获取配置值，优先级：
    1. Streamlit secrets (部署环境)
    2. 环境变量
    3. 默认值
    """
    # 首先尝试从Streamlit secrets获取
    if HAS_STREAMLIT:
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
    
    # 然后尝试环境变量
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # 最后使用默认值
    return default

# Neo4j配置 - 阿里云私有版
NEO4J_URI = get_secret("NEO4J_URI", "bolt://47.110.83.32:11001")
NEO4J_USERNAME = get_secret("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = get_secret("NEO4J_PASSWORD", "mima123456")

# Elasticsearch配置
ELASTICSEARCH_CLOUD_ID = get_secret(
    "ELASTICSEARCH_CLOUD_ID",
    "41ed8f6c58a942fb9aea8f6804841099:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyQ1ZTRhNGI5ZGNlZjc0NDI4YjI3MWEzZDg3YzRmZjY2OCRlZjhhODRlYjliNzc0YjM3ODk0NWQ3ZTQ3OWVkOWRkNQ=="
)
ELASTICSEARCH_USERNAME = get_secret("ELASTICSEARCH_USERNAME", "elastic")
ELASTICSEARCH_PASSWORD = get_secret("ELASTICSEARCH_PASSWORD", "x5ZwEPmZewPZlnZIn1Fy3XoQ")

# DeepSeek API配置
DEEPSEEK_API_KEY = get_secret("DEEPSEEK_API_KEY", "sk-bdf96d7f1aa74a53a83ff167f7f2f5a9")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# 应用配置
APP_TITLE = "管理学自适应学习系统"
APP_ICON = "📊"

# Neo4j标签 - 实际数据库中的标签（无前缀）
# 注意：数据库中使用的是 Module, Chapter, KnowledgePoint 等标签
NEO4J_LABEL_MODULE = "Module"
NEO4J_LABEL_CHAPTER = "Section"  # 数据库中的Section对应章节
NEO4J_LABEL_KNOWLEDGE = "KnowledgePoint"
NEO4J_LABEL_STUDENT = "Student"
NEO4J_LABEL_ACTIVITY = "SearchLog"  # 学习活动日志
NEO4J_LABEL_DANMU = "Log_Danmu_xinli"  # 弹幕日志
