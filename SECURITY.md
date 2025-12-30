# Security Best Practices

本文档概述了 pymstodoapi 项目的安全最佳实践和配置建议。

## 已实施的安全措施

### 1. 认证和授权

#### OAuth 2.0 授权
- ✅ 使用 Microsoft 官方 MSAL 库
- ✅ 支持授权码流程
- ✅ 自动令牌刷新
- ✅ 令牌安全存储

#### API 密钥保护
- ✅ 可选的 API 密钥认证
- ✅ 常数时间比较（防止定时攻击）
- ✅ 强密钥长度要求（最小 16 字符）

### 2. 安全响应头

所有响应包含以下安全头：

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 3. 速率限制

- ✅ 基于 IP 的请求频率限制
- ✅ 可配置的限制阈值
- ✅ 自动清理过期记录
- ✅ 速率限制响应头

### 4. 输入验证

- ✅ Pydantic 模型验证
- ✅ XSS 字符过滤
- ✅ 字段长度限制
- ✅ 类型验证

### 5. 配置安全

- ✅ 环境变量管理
- ✅ 启动时配置验证
- ✅ 敏感信息不记录日志
- ✅ 强密钥长度要求

## 部署安全建议

### 1. 环境变量

**必须设置强密钥**：

```bash
# 生成强 API 密钥（推荐 32 字符以上）
openssl rand -base64 32

# 生成强查询密码
openssl rand -base64 24
```

**示例 .env 配置**：

```env
# 使用真实的 Azure 应用凭据
CLIENT_ID=your_azure_client_id
CLIENT_SECRET=your_azure_client_secret

# 启用 API 密钥保护（生产环境强烈推荐）
ENABLE_API_KEY=true
X_API_KEY=<generated_strong_key_32chars+>

# 配置合理的速率限制
RATE_LIMIT_PER_MINUTE=60

# 查询认证（如果使用 HTML 路由）
ENABLE_QUERY_AUTH=true
QUERY_PASSWD=<generated_strong_password>
```

### 2. HTTPS/TLS

**生产环境必须使用 HTTPS**：

- 在反向代理（Nginx, Traefik）配置 TLS
- 使用 Let's Encrypt 免费证书
- 强制 HTTPS 重定向
- 配置正确的 TLS 版本（TLS 1.2+）

**Nginx 示例**：

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP 到 HTTPS 重定向
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Docker 安全

**已实施**：
- ✅ 非 root 用户运行
- ✅ 最小化基础镜像
- ✅ 多阶段构建

**额外建议**：

```dockerfile
# 限制容器资源
docker run -d \
  --memory="512m" \
  --cpus="1.0" \
  --read-only \
  --tmpfs /tmp \
  pymstodoapi:latest
```

**Docker Compose 安全配置**：

```yaml
services:
  api:
    image: pymstodoapi:latest
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    tmpfs:
      - /tmp
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
```

### 4. 网络安全

**防火墙规则**：
- 仅开放必要端口（443）
- 限制来源 IP（如果可能）
- 使用云服务商的安全组

**示例 iptables 规则**：

```bash
# 仅允许 HTTPS
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# 拒绝其他入站连接
iptables -A INPUT -j DROP
```

## 安全监控

### 1. 日志记录

**建议记录**：
- 认证尝试（成功和失败）
- API 密钥验证失败
- 速率限制触发
- 异常错误

**不要记录**：
- ❌ 密码或密钥
- ❌ 访问令牌
- ❌ 敏感用户数据

### 2. 定期安全检查

```bash
# 依赖漏洞扫描
safety check

# 代码安全扫描
bandit -r api/

# Docker 镜像扫描
docker scan pymstodoapi:latest

# 更新依赖
pip list --outdated
```

### 3. 设置监控告警

建议监控以下指标：
- 异常高的请求频率
- 认证失败率
- API 错误率
- 响应时间异常

## 应急响应

### 密钥泄露处理流程

如果 API 密钥或其他敏感信息泄露：

1. **立即更换密钥**
   ```bash
   # 生成新密钥
   openssl rand -base64 32
   
   # 更新 .env
   vim .env
   
   # 重启服务
   docker-compose restart
   ```

2. **检查访问日志**
   - 查找异常访问模式
   - 确认是否有未授权访问

3. **通知相关方**
   - 通知团队成员
   - 如果需要，通知用户

4. **审查安全措施**
   - 检查其他可能的漏洞
   - 更新安全策略

### Azure 凭据泄露

1. **立即在 Azure 门户撤销凭据**
2. **创建新的客户端密钥**
3. **更新环境配置**
4. **审查 Azure 活动日志**

## 合规性

### GDPR（如适用）

- 用户数据最小化
- 明确的数据保留策略
- 数据访问和删除请求处理
- 数据加密（传输和静态）

### 数据保护

- ✅ 传输加密（HTTPS/TLS）
- ✅ 令牌安全存储
- ⚠️ 考虑静态数据加密（如果存储用户数据）

## 安全清单

### 部署前检查

- [ ] 所有密钥和密码已更改为强随机值
- [ ] API 密钥保护已启用
- [ ] HTTPS/TLS 已正确配置
- [ ] 防火墙规则已设置
- [ ] 日志记录已配置
- [ ] 速率限制已启用
- [ ] Docker 以非 root 用户运行
- [ ] 依赖项已扫描漏洞
- [ ] 备份策略已实施

### 定期维护（每月）

- [ ] 更新依赖项
- [ ] 运行安全扫描
- [ ] 审查访问日志
- [ ] 检查速率限制触发
- [ ] 验证备份完整性
- [ ] 更新文档

### 季度审查

- [ ] 完整的安全审计
- [ ] 渗透测试（如适用）
- [ ] 更新安全策略
- [ ] 团队安全培训

## 报告安全问题

如果发现安全漏洞，请：

1. **不要**公开披露
2. 通过私有渠道联系维护者
3. 提供详细的漏洞信息
4. 给予合理的响应时间

## 参考资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Azure Security Best Practices](https://docs.microsoft.com/en-us/azure/security/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)

## 更新日志

- **2024-12-30**: 初始版本
  - 添加安全响应头
  - 添加速率限制
  - 修复定时攻击漏洞
  - 增强输入验证
