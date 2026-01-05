# 管理学自适应学习系统

一个基于知识图谱和AI的智能学习系统，用于管理学课程的自适应学习。

## 🌟 功能特点

- 📚 **案例库管理** - 丰富的管理学案例资源，支持多维度筛选
- 🗺️ **知识图谱** - 可视化知识点关系和学习路径
- 🎯 **能力推荐** - 基于学习数据的个性化能力提升建议  
- 💬 **课堂互动** - AI助手实时答疑和学习指导
- 📊 **数据分析** - 学习数据统计和可视化

## 🚀 快速开始

### 本地运行

1. **克隆仓库**
```bash
git clone https://github.com/chaocai1-lgtm/20260105_glx_cc.git
cd 20260105_glx_cc
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行应用**
```bash
streamlit run app.py
```

### Streamlit Cloud 部署

1. Fork 此仓库到你的 GitHub 账户

2. 访问 [Streamlit Cloud](https://share.streamlit.io/)

3. 点击 "New app"，选择你 fork 的仓库

4. 设置主文件为 `app.py`

5. 在 "Advanced settings" -> "Secrets" 中配置密钥（参考 `.streamlit/secrets.toml.example`）

6. 点击 "Deploy" 开始部署

## ⚙️ 配置说明

### 必需的环境变量

在 Streamlit Cloud 的 Secrets 中配置：

```toml
# Neo4j 数据库
NEO4J_URI = "neo4j+ssc://your-database.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "your-password"

# DeepSeek API
DEEPSEEK_API_KEY = "sk-your-api-key"
```

## 🧪 部署前测试

运行测试脚本确保一切正常：
```bash
python test_deployment.py
```

## 👥 测试账户
- 教师: teacher / admin888
- 学生: glx_202401 / 123456

## 知识体系
1. 管理与管理学 - 管理基本概念、管理思想发展
2. 决策与计划 - 决策方法、计划工作、战略规划
3. 组织 - 组织设计、人力资源管理、组织变革
4. 领导 - 领导理论、激励方法、沟通艺术
5. 控制 - 控制过程与方法
6. 创新 - 创新职能、技术与组织创新

## 经典案例
1. 华为公司的全球化战略转型
2. 海底捞的服务创新与人力资源管理
3. 字节跳动的组织创新与扁平化管理
