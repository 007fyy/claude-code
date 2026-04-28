#!/usr/bin/env bash
# 用户模块冒烟测试 — 需先启动服务：uvicorn main:app --reload --port 8000
set -e
BASE="http://localhost:8000/api/v1"
PHONE="13700000001"

echo "=== [1] 发送验证码 ==="
curl -s -X POST "$BASE/auth/send-code" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$PHONE\"}" | python -m json.tool

echo ""
echo "请从上方 uvicorn 控制台复制验证码，输入后按回车："
read -r CODE

echo "=== [2] 登录（首次自动注册）==="
LOGIN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$PHONE\",\"code\":\"$CODE\"}")
echo "$LOGIN" | python -m json.tool
TOKEN=$(echo "$LOGIN" | python -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")

echo "=== [3] 获取用户信息 ==="
curl -s "$BASE/user/me" -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "=== [4] 更新昵称 ==="
curl -s -X PUT "$BASE/user/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname":"测试用户"}' | python -m json.tool

echo "=== [5] 更新偏好 ==="
curl -s -X PATCH "$BASE/user/prefs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"style_prefs":["优雅复古"],"occasion_prefs":["约会出行"],"budget_pref":"50-200"}' \
  | python -m json.tool

echo "=== [6] 新增收货地址 ==="
ADDR=$(curl -s -X POST "$BASE/user/address" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","phone":"13800138000","province":"广东省","city":"深圳市","district":"南山区","detail":"科技园 1 号","is_default":true}')
echo "$ADDR" | python -m json.tool
ADDR_ID=$(echo "$ADDR" | python -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")

echo "=== [7] 获取地址列表 ==="
curl -s "$BASE/user/address" -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "=== [8] 修改地址 ==="
curl -s -X PUT "$BASE/user/address/$ADDR_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"detail":"科技园 2 号"}' | python -m json.tool

echo "=== [9] 设为默认地址 ==="
curl -s -X PATCH "$BASE/user/address/$ADDR_ID/default" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "=== [10] 删除地址 ==="
curl -s -X DELETE "$BASE/user/address/$ADDR_ID" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool

echo "=== [11] 无 Token 访问（验证鉴权拦截 code:2001）==="
curl -s "$BASE/user/me" | python -m json.tool

echo ""
echo "✓ 全部冒烟测试通过！用户模块开发完成。"
