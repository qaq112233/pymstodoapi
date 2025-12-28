# Dockerized MS To Do API Gateway

一个基于 Python 的 RESTful API 服务，使用 MSAL 官方库和 Microsoft Graph API 与 Microsoft To Do 交互。

## 功能特性

✅ **OAuth 2.0 授权码流** - 完整的 Microsoft 登录和授权流程  
✅ **Token 自动刷新** - 自动管理和刷新访问令牌  
✅ **Token 持久化** - 令牌存储在 Docker Volume 中，容器重启后仍然有效  
✅ **API Key 保护** - 可选的 API 密钥认证保护业务端点  
✅ **自定义 API 前缀** - 支持通过环境变量设置基础路径  
✅ **完整的 To Do API** - 任务列表和任务的 CRUD 操作  
✅ **Docker 容器化** - 使用非 root 用户运行，提高安全性  
✅ **健康检查** - 内置健康检查端点和 Docker 健康监控  

## 快速开始

### 前置要求

- Docker 和 Docker Compose
- Microsoft Azure 应用注册（获取 Client ID 和 Client Secret）

### 1. 注册 Azure 应用

1. 访问 [Azure Portal](https://portal.azure.com/)
2. 前往 "Azure Active Directory" > "App registrations" > "New registration"
3. 设置重定向 URI 为: `https://localhost/login/authorized`
4. 在 "API permissions" 中添加 `Tasks.ReadWrite` 权限
5. 在 "Certificates & secrets" 中创建新的 client secret
6. 记录 Application (client) ID 和 client secret 值

### 2. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
nano .env
```

必需的配置项：
```env
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
```

可选的配置项：
```env
# Microsoft Graph API 版本（v1.0 或 beta，默认：beta）
GRAPH_API_VERSION=beta

# 自定义 API 基础路径（例如：/secret/api）
API_PREFIX=

# 启用 API Key 保护
ENABLE_API_KEY=false
X_API_KEY=your_secret_api_key

# 服务端口
PORT=8000
```

### 3. 启动服务

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f
```

服务将在 `http://localhost:8000` 启动。

### 4. 首次认证

1. 获取授权 URL：
```bash
curl http://localhost:8000/auth/login
```

2. 访问返回的 URL，使用 Microsoft 账号登录并授权

3. 授权成功后，复制浏览器地址栏的完整 URL（包含 code 参数）

4. 调用回调端点：
```bash
curl "http://localhost:8000/auth/callback?code=YOUR_CODE&state=YOUR_STATE"
```

5. 认证成功！现在可以使用 API 了

## API 文档

### 认证端点（无需 API Key）

#### 获取登录 URL
```bash
GET /auth/login
```

#### OAuth 回调
```bash
GET /auth/callback?code={code}&state={state}
```

#### 检查认证状态
```bash
GET /auth/status
```

#### 登出
```bash
POST /auth/logout
```

### 任务列表端点

#### 获取所有列表
```bash
GET /lists?limit=99
```

#### 创建列表
```bash
POST /lists
Content-Type: application/json

{
  "displayName": "我的新列表"
}
```

#### 获取单个列表
```bash
GET /lists/{list_id}
```

#### 更新列表
```bash
PATCH /lists/{list_id}
Content-Type: application/json

{
  "displayName": "更新的列表名称"
}
```

#### 删除列表
```bash
DELETE /lists/{list_id}
```

### 任务端点

#### 获取列表中的任务
```bash
GET /lists/{list_id}/tasks?status=notCompleted&limit=1000
```

参数：
- `status`: `completed` | `notCompleted` | `all` (默认: notCompleted)
- `limit`: 最大返回数量（默认: 1000）

#### 创建任务
```bash
POST /lists/{list_id}/tasks
Content-Type: application/json

{
  "title": "完成项目文档",
  "body": "需要编写完整的 API 文档",
  "dueDateTime": "2024-12-31T23:59:59Z",
  "importance": "high",
  "isReminderOn": true,
  "reminderDateTime": "2024-12-31T09:00:00Z",
  "categories": ["工作", "重要"]
}
```

#### 获取单个任务
```bash
GET /tasks/{task_id}?list_id={list_id}
```

#### 更新任务
```bash
PATCH /tasks/{task_id}?list_id={list_id}
Content-Type: application/json

{
  "title": "更新的任务标题",
  "status": "completed",
  "importance": "normal"
}
```

#### 删除任务
```bash
DELETE /tasks/{task_id}?list_id={list_id}
```

### 健康检查
```bash
GET /health
```

## 使用 API Key 保护

启用 API Key 保护后，所有业务端点（/lists 和 /tasks）都需要在请求头中携带 API Key：

```bash
curl -H "X-API-KEY: your_api_key" http://localhost:8000/lists
```

## 自定义 API 前缀

设置 `API_PREFIX` 环境变量可以为所有端点添加基础路径：

```env
API_PREFIX=/secret/api
```

端点将变为：
- `/secret/api/auth/login`
- `/secret/api/lists`
- `/secret/api/tasks`

## 交互式 API 文档

启动服务后，访问以下地址查看自动生成的 API 文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

如果设置了 API_PREFIX，文档地址将变为：
- `http://localhost:8000{API_PREFIX}/docs`
- `http://localhost:8000{API_PREFIX}/redoc`

## Docker 管理

### 查看日志
```bash
docker-compose logs -f
```

### 停止服务
```bash
docker-compose down
```

### 重新构建
```bash
docker-compose up -d --build
```

### 清理（包括 Token 缓存）
```bash
docker-compose down -v
```

## 文件结构

```
.
├── api/                          # API 应用代码
│   ├── __init__.py
│   ├── main.py                   # FastAPI 应用主文件
│   ├── config.py                 # 配置管理
│   ├── auth.py                   # 认证和 Token 管理（MSAL）
│   ├── graph_client.py           # Microsoft Graph API 客户端
│   ├── dependencies.py           # FastAPI 依赖注入
│   ├── models.py                 # Pydantic 数据模型
│   └── routes/                   # API 路由
│       ├── __init__.py
│       ├── auth.py               # 认证路由
│       ├── lists.py              # 任务列表路由
│       └── tasks.py              # 任务路由
├── Dockerfile                    # Docker 镜像定义
├── docker-compose.yml            # Docker Compose 配置
├── .env.example                  # 环境变量示例
├── api_requirements.txt          # API 服务依赖
└── README_API.md                 # 本文档
```

## 安全建议

1. **使用强 API Key**: 如果启用 API Key 保护，使用复杂的随机字符串
2. **保护环境变量**: 不要将 .env 文件提交到版本控制
3. **使用 HTTPS**: 生产环境中使用反向代理（如 Nginx）提供 HTTPS
4. **限制网络访问**: 使用防火墙限制对 API 的访问
5. **定期更新**: 保持 Docker 镜像和依赖包更新

## 故障排除

### Token 过期
Token 会自动刷新，如果遇到认证问题：
```bash
curl -X POST http://localhost:8000/auth/logout
# 然后重新认证
```

### 容器无法启动
检查日志：
```bash
docker-compose logs
```

确保环境变量配置正确：
```bash
docker-compose config
```

### 端口被占用
修改 .env 文件中的 PORT 变量：
```env
PORT=8080
```

## 技术栈

- **Python 3.11**
- **FastAPI** - 现代的高性能 Web 框架
- **MSAL** - Microsoft Authentication Library
- **Microsoft Graph API** - Microsoft To Do API 客户端
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证和设置管理
- **Docker** - 容器化部署

## 开发

### 本地开发（不使用 Docker）

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r api_requirements.txt

# 设置环境变量
export CLIENT_ID=your_client_id
export CLIENT_SECRET=your_client_secret
export GRAPH_API_VERSION=beta

# 运行服务
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请提交 Issue。
