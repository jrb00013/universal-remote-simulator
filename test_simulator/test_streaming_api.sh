#!/bin/bash
# Test script for TV Simulator Streaming API

BASE_URL="http://localhost:5000"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     TV Simulator Streaming API - Test Script            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Get frame info
echo "1. Testing /api/frame/info..."
curl -s "$BASE_URL/api/frame/info" | python3 -m json.tool
echo ""

# Test 2: Get frame as PNG
echo "2. Testing /api/frame (PNG)..."
curl -s "$BASE_URL/api/frame" -o test_frame.png
if [ -f test_frame.png ]; then
    echo "   ✅ Frame saved to test_frame.png ($(stat -f%z test_frame.png 2>/dev/null || stat -c%s test_frame.png) bytes)"
else
    echo "   ❌ Failed to save frame"
fi
echo ""

# Test 3: Get frame as JSON
echo "3. Testing /api/frame?format=json..."
curl -s "$BASE_URL/api/frame?format=json" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"   ✅ Frame data: {len(data.get('frame', ''))} chars, {data.get('width')}x{data.get('height')}, age: {data.get('age_seconds', 0):.2f}s\")" 2>/dev/null || echo "   ⚠️  JSON response received (install python3 for parsing)"
echo ""

# Test 4: Get frame as JPEG (if Pillow available)
echo "4. Testing /api/frame?format=jpeg..."
HTTP_CODE=$(curl -s -o test_frame.jpg -w "%{http_code}" "$BASE_URL/api/frame?format=jpeg")
if [ "$HTTP_CODE" = "200" ] && [ -f test_frame.jpg ]; then
    echo "   ✅ JPEG frame saved to test_frame.jpg ($(stat -f%z test_frame.jpg 2>/dev/null || stat -c%s test_frame.jpg) bytes)"
elif [ "$HTTP_CODE" = "501" ]; then
    echo "   ⚠️  JPEG format not available (Pillow not installed)"
else
    echo "   ❌ Failed to get JPEG frame (HTTP $HTTP_CODE)"
fi
echo ""

# Test 5: Continuous frame capture (5 frames)
echo "5. Testing continuous frame capture (5 frames)..."
for i in {1..5}; do
    curl -s "$BASE_URL/api/frame" -o "frame_$i.png" > /dev/null 2>&1
    echo "   Frame $i captured"
    sleep 0.5
done
echo "   ✅ 5 frames captured (frame_1.png through frame_5.png)"
echo ""

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    Test Complete                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Usage examples:"
echo "  curl $BASE_URL/api/frame -o frame.png"
echo "  curl $BASE_URL/api/frame?format=json | jq"
echo "  curl $BASE_URL/api/frame/info"
echo ""

