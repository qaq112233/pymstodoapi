# 认证指南 - 简化版

## 问题解决

### 1. OAuth 错误："OAuth 2 MUST utilize https"

**已修复！** 代码已更新，允许在开发环境使用 HTTP。

### 2. 简化的认证流程

我们提供了**三种**认证方式，推荐使用**方式 1**（最简单）：

---

## 方式 1: 简化回调（推荐）⭐

### 步骤：

#### 1. 获取授权 URL
```bash
curl http://localhost:8000/auth/login
```

返回类似：
```json
{
  "authorization_url": "https://login.microsoftonline.com/...",
  "message": "Please visit this URL to authorize the application"
}
```

#### 2. 在浏览器中打开授权 URL

复制上面返回的 URL，在浏览器中打开并使用 Microsoft 账号登录授权。

#### 3. 获取重定向 URL

授权成功后，浏览器会跳转到类似这样的地址（地址栏会显示连接失败，这是正常的）：

```
https://localhost/login/authorized?code=1.Ab4ADE3lnq...（很长的code）&state=SvN964MgrV...&session_state=00b8d099...
```

#### 4. 完成认证（直接在浏览器中操作）

在浏览器地址栏中，将地址修改为：

```
http://localhost:8000/auth/callback-simple?url=https://localhost/login/authorized?code=1.Ab4ADE3lnq...（保留完整的code）&state=SvN964MgrV...&session_state=00b8d099...
```

**简单说就是：**
- 将 `https://localhost/login/authorized?` 替换为 `http://localhost:8000/auth/callback-simple?url=https://localhost/login/authorized?`
- 保留后面所有的参数

#### 5. 成功！

浏览器会显示一个漂亮的成功页面，表示认证完成。

现在可以使用 API 了：
```bash
curl http://localhost:8000/lists
```

---

## 方式 2: 使用 POST 请求

如果你使用编程方式，可以直接 POST 完整的重定向 URL：

```bash
curl -X POST http://localhost:8000/auth/callback \
  -H "Content-Type: application/json" \
  -d '{
    "redirect_url": "https://localhost/login/authorized?code=...&state=..."
  }'
```

---

## 方式 3: 传统方式（手动提取参数）

如果你想手动提取 `code` 和 `state`：

```bash
# 从重定向 URL 中提取 code 和 state
# https://localhost/login/authorized?code=YOUR_CODE&state=YOUR_STATE

# 然后调用
curl "http://localhost:8000/auth/callback?code=YOUR_CODE&state=YOUR_STATE"
```

---

## Azure 应用注册配置

在 Azure Portal 中注册应用时，**重定向 URI** 必须设置为：

```
https://localhost/login/authorized
```

**注意事项：**
- 协议是 `https`（不是 http）
- 域名是 `localhost`（不是 127.0.0.1）
- 路径是 `/login/authorized`（不是其他）

---

## 常见问题

### Q: 为什么重定向到 localhost 会显示连接失败？

**A:** 这是正常的！因为 `https://localhost/login/authorized` 并不是一个真实的服务器地址。我们只需要浏览器地址栏中的完整 URL（包含 code 参数），然后通过我们的 API 来处理。

### Q: 如何知道认证成功了？

**A:** 
1. 使用方式 1 时，浏览器会显示绿色的成功页面
2. 可以测试 API：`curl http://localhost:8000/auth/status`
3. 尝试获取列表：`curl http://localhost:8000/lists`

### Q: Token 会过期吗？

**A:** 会，但不用担心：
- Access Token 约 1 小时后过期
- 系统会自动使用 Refresh Token 刷新
- 新 Token 自动保存
- 容器重启后 Token 依然有效

### Q: 如何重新认证？

**A:**
```bash
# 1. 登出
curl -X POST http://localhost:8000/auth/logout

# 2. 重新开始认证流程
curl http://localhost:8000/auth/login
```

---

## 快速参考

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/auth/login` | GET | 获取授权 URL |
| `/auth/callback-simple?url=<完整URL>` | GET | 简化回调（推荐）|
| `/auth/callback` | GET | 传统回调 |
| `/auth/callback` | POST | POST 方式回调 |
| `/auth/status` | GET | 检查认证状态 |
| `/auth/logout` | POST | 登出 |

### 完整示例流程

```bash
# 1. 获取授权 URL
curl http://localhost:8000/auth/login

# 2. 在浏览器打开返回的 URL 并授权

# 3. 复制浏览器地址栏的完整 URL，在浏览器访问：
# http://localhost:8000/auth/callback-simple?url=<完整的重定向URL>

# 4. 测试 API
curl http://localhost:8000/lists
curl http://localhost:8000/auth/status
```

---

## 需要帮助？

- 查看 [完整文档](README_API.md)
- 查看 [常见问题](FAQ.md)
- 查看 [使用示例](EXAMPLES.md)
- 运行测试：`python3 test_api.py`

---

**现在就开始使用吧！** 🚀
