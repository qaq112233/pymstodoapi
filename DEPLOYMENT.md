# MS To Do API Gateway 部署指南

本指南将详细说明如何在不同环境中部署 MS To Do API Gateway。

## 目录

1. [前置要求](#前置要求)
2. [Azure 应用注册](#azure-应用注册)
3. [本地开发部署](#本地开发部署)
4. [Docker 部署（推荐）](#docker-部署推荐)
5. [生产环境部署](#生产环境部署)
6. [故障排除](#故障排除)

---

## 前置要求

### 必需软件

- **Python 3.11+** (本地开发)
- **Docker 20.10+** (容器部署)
- **Docker Compose 2.0+** (容器编排)

### Microsoft 账户

- 需要有效的 Microsoft 账户
- Azure Portal 访问权限（用于应用注册）

---

## Azure 应用注册

### 步骤 1: 创建应用注册

1. 访问 [Azure Portal](https://portal.azure.com/)
2. 搜索并进入 "Azure Active Directory"
3. 左侧菜单选择 "App registrations"
4. 点击 "New registration"

### 步骤 2: 配置应用

**基本信息:**
- **Name**: `MS To Do API Gateway` (或自定义名称)
- **Supported account types**: 选择 "Accounts in any organizational directory and personal Microsoft accounts"

**Redirect URI:**
- Platform: `Web`
- URI: `https://localhost/login/authorized`

点击 "Register" 完成创建。

### 步骤 3: 记录应用信息

在 "Overview" 页面记录：
- **Application (client) ID** - 这是你的 `CLIENT_ID`
- **Directory (tenant) ID** - 用于参考

### 步骤 4: 创建客户端密钥

1. 左侧菜单选择 "Certificates & secrets"
2. 点击 "New client secret"
3. 设置描述: `API Gateway Secret`
4. 选择过期时间（推荐 24 months）
5. 点击 "Add"
6. **立即复制 Value** - 这是你的 `CLIENT_SECRET`（只显示一次！）

### 步骤 5: 配置 API 权限

1. 左侧菜单选择 "API permissions"
2. 点击 "Add a permission"
3. 选择 "Microsoft Graph"
4. 选择 "Delegated permissions"
5. 搜索并添加以下权限:
   - `Tasks.ReadWrite` - 读写用户任务
   - `Tasks.ReadWrite.Shared` - 读写共享任务
   - `User.Read` - 读取用户基本信息
6. 点击 "Add permissions"
7. 点击 "Grant admin consent for [Your Organization]" (如果可用)

**注意**: 不需要手动添加 `offline_access`、`openid`、`profile` 等权限，MSAL 会自动处理这些保留作用域。

### 完成

现在你已获得：
- ✅ CLIENT_ID
- ✅ CLIENT_SECRET
- ✅ 已配置的重定向 URI
- ✅ 必需的 API 权限

---

## 本地开发部署

### 步骤 1: 准备环境

```bash
# 克隆或进入项目目录
cd pymstodo-master

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r api_requirements.txt
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

填入你的配置:
```env
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
API_PREFIX=
ENABLE_API_KEY=false
TOKEN_CACHE_PATH=./token_cache
PORT=8000
```

### 步骤 3: 启动服务

```bash
# 使用启动脚本
./start.sh

# 或直接使用 uvicorn
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤 4: 验证服务

```bash
# 健康检查
curl http://localhost:8000/health

# 查看 API 文档
# 浏览器访问: http://localhost:8000/docs
```

---

## Docker 部署（推荐）

### 方式 1: 使用快速启动脚本

```bash
# 首次配置
cp .env.example .env
nano .env  # 填入你的 CLIENT_ID 和 CLIENT_SECRET

# 启动服务
python3 quickstart.py
```

脚本会自动:
- ✅ 检查环境配置
- ✅ 验证 Docker 安装
- ✅ 构建并启动容器
- ✅ 显示访问信息

### 方式 2: 手动 Docker Compose

```bash
# 1. 配置环境
cp .env.example .env
nano .env

# 2. 构建并启动
docker-compose up -d --build

# 3. 查看日志
docker-compose logs -f

# 4. 查看运行状态
docker-compose ps
```

### 验证 Docker 部署

```bash
# 健康检查
curl http://localhost:8000/health

# 查看容器日志
docker-compose logs -f mstodo-api

# 进入容器 shell
docker-compose exec mstodo-api bash
```

---

## 生产环境部署

### 使用 Nginx 反向代理

#### 1. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### 2. 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/mstodo-api`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 日志
    access_log /var/log/nginx/mstodo-api-access.log;
    error_log /var/log/nginx/mstodo-api-error.log;
    
    # 代理设置
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 限制请求大小
    client_max_body_size 10M;
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/mstodo-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 使用 Systemd 管理服务

创建服务文件 `/etc/systemd/system/mstodo-api.service`:

```ini
[Unit]
Description=MS To Do API Gateway
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/mstodo-api
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
ExecReload=/usr/local/bin/docker-compose restart
User=root
Group=root

[Install]
WantedBy=multi-user.target
```

管理服务:
```bash
# 启动服务
sudo systemctl start mstodo-api

# 开机自启
sudo systemctl enable mstodo-api

# 查看状态
sudo systemctl status mstodo-api

# 重启服务
sudo systemctl restart mstodo-api
```

### 环境变量安全配置

**生产环境建议:**

1. **不要将 .env 提交到版本控制**
```bash
echo ".env" >> .gitignore
```

2. **使用环境变量而非 .env 文件**
```bash
# 在 docker-compose.yml 中使用环境变量
docker-compose up -d
```

3. **使用 Docker Secrets (Swarm 模式)**
```yaml
# docker-compose.yml
services:
  mstodo-api:
    secrets:
      - client_id
      - client_secret
      
secrets:
  client_id:
    external: true
  client_secret:
    external: true
```

4. **限制文件权限**
```bash
chmod 600 .env
chown root:root .env
```

### 监控和日志

#### 日志管理

```bash
# 限制日志大小
docker-compose logs --tail=1000 -f

# 配置日志轮转
# 在 docker-compose.yml 添加:
services:
  mstodo-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### 监控脚本

创建 `monitor.sh`:
```bash
#!/bin/bash
while true; do
    STATUS=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"')
    if [ -z "$STATUS" ]; then
        echo "$(date): API is DOWN!" | tee -a /var/log/mstodo-api-monitor.log
        # 发送告警
    else
        echo "$(date): API is UP"
    fi
    sleep 60
done
```

### 性能优化

#### Docker 资源限制

```yaml
# docker-compose.yml
services:
  mstodo-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

#### Uvicorn 配置

修改 Dockerfile:
```dockerfile
CMD ["python", "-m", "uvicorn", "api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
```

---

## 认证流程

### 首次认证

1. **获取授权 URL**
```bash
curl http://localhost:8000/auth/login
```

2. **用户授权**
- 在浏览器中打开返回的 URL
- 使用 Microsoft 账号登录
- 同意授权请求

3. **处理回调**
- 浏览器会跳转到包含 `code` 参数的 URL
- 复制完整的 URL
- 调用回调端点:
```bash
curl "http://localhost:8000/auth/callback?code=YOUR_CODE&state=YOUR_STATE"
```

4. **验证认证**
```bash
curl http://localhost:8000/auth/status
```

### 自动化认证（仅用于测试）

可以使用 Selenium 或类似工具自动化认证流程，但**不建议在生产环境使用**。

---

## 故障排除

### 问题 1: Docker 容器无法启动

**症状**: `docker-compose up -d` 失败

**解决方法**:
```bash
# 查看详细日志
docker-compose logs

# 检查配置
docker-compose config

# 验证环境变量
docker-compose exec mstodo-api env | grep CLIENT
```

### 问题 2: 认证失败

**症状**: 回调返回 400 错误

**可能原因**:
- CLIENT_ID 或 CLIENT_SECRET 错误
- 重定向 URI 配置不匹配
- Azure 应用权限未配置

**解决方法**:
```bash
# 检查环境变量
cat .env | grep CLIENT

# 验证 Azure 配置
# 1. 检查重定向 URI: https://localhost/login/authorized
# 2. 检查 API 权限: Tasks.ReadWrite, offline_access
# 3. 验证 Client Secret 未过期
```

### 问题 3: Token 刷新失败

**症状**: API 调用返回 401 错误

**解决方法**:
```bash
# 清除旧 token
curl -X POST http://localhost:8000/auth/logout

# 重新认证
curl http://localhost:8000/auth/login
# 然后完成认证流程
```

### 问题 4: 端口被占用

**症状**: `Address already in use`

**解决方法**:
```bash
# 查找占用端口的进程
sudo lsof -i :8000

# 或修改 .env 文件
PORT=8080
```

### 问题 5: 健康检查失败

**症状**: Docker 健康检查一直失败

**解决方法**:
```bash
# 进入容器检查
docker-compose exec mstodo-api bash
curl http://localhost:8000/health

# 查看应用日志
docker-compose logs -f

# 禁用健康检查（临时）
# 在 docker-compose.yml 中注释掉 healthcheck
```

---

## 测试部署

运行测试套件验证部署:

```bash
# 基础测试
python3 test_api.py

# 带 API Key 的测试
python3 test_api.py --api-key your_api_key

# 测试自定义 URL
python3 test_api.py --url http://your-domain.com
```

---

## 维护和更新

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 查看日志确认
docker-compose logs -f
```

### 备份

```bash
# 备份 token 缓存
docker-compose exec mstodo-api tar czf /tmp/token_backup.tar.gz /app/token_cache
docker cp mstodo-api:/tmp/token_backup.tar.gz ./backup/

# 备份环境配置
cp .env .env.backup
```

### 恢复

```bash
# 恢复 token
docker cp ./backup/token_backup.tar.gz mstodo-api:/tmp/
docker-compose exec mstodo-api tar xzf /tmp/token_backup.tar.gz -C /
```

---

## 安全清单

- [ ] 使用强随机字符串作为 API_KEY
- [ ] 不将 .env 文件提交到版本控制
- [ ] 使用 HTTPS（生产环境）
- [ ] 配置防火墙规则
- [ ] 定期更新 Docker 镜像
- [ ] 监控异常日志
- [ ] 限制容器资源
- [ ] 使用非 root 用户运行
- [ ] 定期备份配置和 token

---

## 联系和支持

- 查看项目文档: [README_API.md](README_API.md)
- 查看使用示例: [EXAMPLES.md](EXAMPLES.md)
- 查看项目结构: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

如有问题，请提交 GitHub Issue。
