# SSL证书配置说明

请将您的SSL证书文件放置在此目录下：

## 必需文件：
- `cert.pem` - SSL证书文件
- `key.pem` - SSL私钥文件

## 文件权限：
确保证书文件具有适当的权限：
```bash
chmod 600 key.pem
chmod 644 cert.pem
```

## 自签名证书示例：
如果您需要生成自签名证书用于测试，可以使用以下命令：

```bash
# 生成私钥
openssl genrsa -out key.pem 2048

# 生成自签名证书
openssl req -new -x509 -key key.pem -out cert.pem -days 365 -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
```

## 注意事项：
- 证书文件将被映射到容器内的 `/app/certs/` 目录
- 如果证书文件不存在，应用将以HTTP模式运行
- 证书文件路径在 `app.py` 中的 `SSL_CERT_PATH` 和 `SSL_KEY_PATH` 变量中配置 