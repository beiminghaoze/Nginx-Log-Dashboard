#!/bin/bash

# 生成自签名SSL证书脚本

echo "正在生成自签名SSL证书..."

# 创建certs目录
mkdir -p certs

# 生成私钥（使用更快的算法）
echo "生成私钥..."
openssl genrsa -out certs/key.pem 2048

# 生成自签名证书（优化配置）
echo "生成自签名证书..."
openssl req -new -x509 -key certs/key.pem -out certs/cert.pem -days 365 \
    -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost" \
    -sha256 -extensions v3_req \
    -config <(cat <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = CN
ST = State
L = City
O = Organization
CN = localhost

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
EOF
)

# 设置文件权限
chmod 600 certs/key.pem
chmod 644 certs/cert.pem

echo "SSL证书生成完成！"
echo "证书文件位置："
echo "  - certs/cert.pem (证书文件)"
echo "  - certs/key.pem (私钥文件)"
echo ""
echo "现在可以重新构建和运行Docker容器："
echo "  docker-compose down"
echo "  docker-compose up -d"
echo ""
echo "访问地址："
echo "  - HTTP:  http://localhost:5000"
echo "  - HTTPS: https://localhost:5000 (自签名证书，浏览器会显示警告)" 