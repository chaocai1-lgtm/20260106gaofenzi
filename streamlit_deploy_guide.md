# Streamlit Cloud 部署指南

## 部署步骤

### 1. **准备工作**

#### 确保项目结构
```
.
├── app.py (主应用文件)
├── requirements.txt
├── .streamlit/
│   ├── config.toml (配置文件)
│   ├── secrets.toml (本地密钥，不提交)
│   └── .gitignore
├── modules/
├── config/
├── data/
└── lib/
```

#### 更新requirements.txt
确保所有依赖都已列出：
```
streamlit>=1.28.0
openai
httpx
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.0.0
pyvis>=0.3.0
streamlit-autorefresh
neo4j>=5.0.0
```

### 2. **GitHub推送**
```bash
git add .
git commit -m "Streamlit Cloud部署配置"
git push origin main
```

### 3. **Streamlit Cloud部署**

#### 登录 Streamlit Cloud
1. 访问 https://streamlit.io/cloud
2. 用GitHub账号登录
3. 点击 "New app"

#### 配置应用信息
- **Repository**: `chaocai1-lgtm/20260106_glx_demo`
- **Branch**: `main`
- **Main file path**: `管理学自适应学习系统/app.py`
- **App URL**: 选择自定义URL（如：`glx-demo`）

#### 配置密钥 (Secrets)
1. 点击 "Settings" → "Secrets"
2. 复制`.streamlit/secrets.toml`中的内容
3. 粘贴到Secrets编辑框：

```toml
NEO4J_URI = "bolt://47.110.83.32:11001"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "mima123456"
```

### 4. **高级配置**（可选）

#### 环境变量在Streamlit Cloud配置
- Memory: 1 GB
- CPU: 1 vCPU
- Max upload size: 200 MB
- Session timeout: 60分钟

#### 监控和日志
- Streamlit Cloud会自动保存应用日志
- 在App menu中查看"Manage app" → "View logs"

### 5. **性能优化建议**

#### 代码优化
- 使用`@st.cache_data`缓存重量级计算
- 使用`@st.cache_resource`缓存数据库连接

```python
@st.cache_resource
def get_neo4j_connection():
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        st.secrets["NEO4J_URI"],
        auth=(st.secrets["NEO4J_USERNAME"], st.secrets["NEO4J_PASSWORD"])
    )
    return driver
```

#### 依赖优化
- 删除不必要的包
- 使用轻量级替代品
- 预装wheels加快部署

### 6. **故障排除**

#### 连接问题
- 确认Neo4j服务器可从外网访问
- 检查防火墙和安全组设置
- 验证URI格式（bolt://不需要SSL）

#### 性能问题
- 检查Neo4j查询是否优化
- 使用缓存减少重复请求
- 考虑使用CDN加速静态资源

#### 日志查看
在Streamlit Cloud应用页面的菜单中：
```
Manage app → View logs
```

### 7. **持续部署**

当推送新代码到GitHub时，Streamlit Cloud会自动重新部署（1-3分钟）

### 8. **自定义域名**（付费功能）

在App settings中配置自定义域名

---

## config.toml 配置说明

### [client] 设置
- `showErrorDetails`: 显示错误详情（开发时true，生产false）
- `toolbarMode`: 工具栏模式（viewer/developer）
- `logger.level`: 日志级别

### [server] 设置
- `headless`: 无界面模式
- `enableXsrfProtection`: CSRF保护
- `enableCORS`: 跨域资源共享
- `maxUploadSize`: 最大上传文件大小（MB）
- `maxMessageSize`: 最大消息大小（MB）

### [theme] 设置
当前配置使用暖橙色主题，匹配应用UI设计

---

## 测试清单

- [ ] 本地运行无错误：`streamlit run 管理学自适应学习系统/app.py`
- [ ] Neo4j连接成功
- [ ] 所有依赖都在requirements.txt中
- [ ] .streamlit/.gitignore确保secrets.toml不被提交
- [ ] GitHub仓库公开且可访问
- [ ] Streamlit Cloud密钥配置正确

