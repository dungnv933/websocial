#!/bin/bash

# SMM Panel Backend - API Test Script
# Script để test các API endpoints

echo "🧪 Testing SMM Panel Backend API..."

BASE_URL="http://localhost:8000"

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "$BASE_URL/health" | jq . || echo "❌ Health check failed"

echo ""

# Test services endpoint
echo "2. Testing services endpoint..."
curl -s "$BASE_URL/api/services" | jq . || echo "❌ Services endpoint failed"

echo ""

# Test register endpoint
echo "3. Testing register endpoint..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}')

echo "Register response:"
echo "$REGISTER_RESPONSE" | jq . || echo "$REGISTER_RESPONSE"

echo ""

# Extract token from login
echo "4. Testing login endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}')

echo "Login response:"
echo "$LOGIN_RESPONSE" | jq . || echo "$LOGIN_RESPONSE"

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo ""
    echo "5. Testing authenticated endpoints..."
    
    # Test user info
    echo "Testing /api/auth/me..."
    curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/auth/me" | jq . || echo "❌ User info failed"
    
    echo ""
    
    # Test balance
    echo "Testing /api/balance..."
    curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/balance" | jq . || echo "❌ Balance failed"
    
    echo ""
    
    # Test deposit
    echo "Testing deposit..."
    curl -s -X POST "$BASE_URL/api/balance/deposit" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"amount": 100.0}' | jq . || echo "❌ Deposit failed"
    
    echo ""
    
    # Test create order
    echo "Testing create order..."
    curl -s -X POST "$BASE_URL/api/orders" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"service_id": 1, "link": "https://example.com", "quantity": 1000}' | jq . || echo "❌ Create order failed"
    
    echo ""
    
    # Test order history
    echo "Testing order history..."
    curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/orders/history" | jq . || echo "❌ Order history failed"
    
    echo ""
    
    # Test promotions
    echo "Testing promotions..."
    curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/promotions" | jq . || echo "❌ Promotions failed"
    
else
    echo "❌ Could not extract token from login response"
fi

echo ""
echo "🎉 API testing completed!"
echo ""
echo "📋 Available endpoints:"
echo "   Health: $BASE_URL/health"
echo "   API Docs: $BASE_URL/docs"
echo "   Services: $BASE_URL/api/services"
echo "   Register: $BASE_URL/api/auth/register"
echo "   Login: $BASE_URL/api/auth/login"
echo "   Balance: $BASE_URL/api/balance"
echo "   Orders: $BASE_URL/api/orders"
echo "   Promotions: $BASE_URL/api/promotions"
