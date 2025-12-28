# Microsoft To Do API Gateway

基于 FastAPI 的生产级 Microsoft To Do RESTful API 服务。

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Azure 应用凭据：

```env
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
API_PREFIX=/api/v1
ENABLE_API_KEY=false
```

### 2. 启动服务

```bash
docker-compose up -d --build
```

### 3. 授权认证

访问 `http://localhost:8000/auth/login` 获取授权链接，在浏览器中完成授权后，将重定向URL复制到：

```
http://localhost:8000/auth/callback-simple?url=<完整重定向URL>
```

### 4. 开始使用

```bash
# 健康检查
curl http://localhost:8000/health

# 认证状态
curl http://localhost:8000/auth/status

# 获取任务列表
curl http://localhost:8000/lists
```

## API文档

启动服务后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 项目结构

```
api/
├── main.py          # FastAPI应用入口
├── config.py        # 环境配置
├── auth.py          # OAuth认证管理
├── dependencies.py  # 依赖注入
├── models.py        # 数据模型
└── routes/          # API路由
    ├── auth.py      # 认证端点
    ├── lists.py     # 列表管理
    └── tasks.py     # 任务管理
```

## 核心功能

- ✅ OAuth 2.0 授权码流程
- ✅ 自动令牌刷新
- ✅ 任务列表 CRUD
- ✅ 任务 CRUD（支持状态过滤）
- ✅ Docker 容器化部署
- ✅ 非root用户运行（安全）
- ✅ 健康检查
- ✅ API密钥保护（可选）

## 镜像优化

本服务采用多阶段构建，优化后镜像大小约 **200MB**（比原来减少 66%）：

- 使用 `python:3.11-slim` 基础镜像
- 多阶段构建分离编译和运行环境
- 固定版本依赖，避免不必要的包
- 从PyPI安装pymstodo，无需打包源码

## 文档

- [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) - 详细认证指南
- [API_KEY_GUIDE.md](API_KEY_GUIDE.md) - API密钥保护指南
- [DEPLOYMENT.md](DEPLOYMENT.md) - 生产部署指南
- [README_API.md](README_API.md) - 完整API文档
- [SOLUTION.md](SOLUTION.md) - 技术方案说明

## Azure应用配置

重定向URI: `https://localhost/login/authorized`

详见 [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)


