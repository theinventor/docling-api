#!/bin/bash

# Test script for the Docling API with authentication

API_URL="http://localhost:8000"
API_KEY="your-secret-api-key-here"
TEST_FILE="../docling-test/input/test_resume.docx"

echo "Testing Docling API..."
echo "========================"

# Test 1: Health check
echo "1. Testing health endpoint..."
curl -s "$API_URL/" | jq '.' || echo "Health check response received"

echo ""
echo "2. Testing document conversion with API key..."

# Test 2: Convert DOCX to Markdown
if [ -f "$TEST_FILE" ]; then
    echo "Converting: $TEST_FILE"
    
    # Make the request and save response
    curl -X POST "$API_URL/convert" \
        -H "X-API-Key: $API_KEY" \
        -F "file=@$TEST_FILE" \
        -o output_test.md \
        -w "\nHTTP Status: %{http_code}\n"
    
    echo ""
    echo "Markdown output preview (first 500 chars):"
    echo "-------------------------------------------"
    head -c 500 output_test.md
    echo ""
    echo "-------------------------------------------"
    echo "Full output saved to: output_test.md"
else
    echo "Test file not found: $TEST_FILE"
    echo "Creating a simple test document..."
    
    # Create a test with raw body
    echo "Testing raw body endpoint..."
    curl -X POST "$API_URL/convert/raw" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: text/plain" \
        -H "Filename: test.txt" \
        --data "This is a test document for Docling API conversion." \
        -w "\nHTTP Status: %{http_code}\n"
fi

echo ""
echo "3. Testing authentication (should fail with wrong key)..."
curl -X POST "$API_URL/convert" \
    -H "X-API-Key: wrong-key" \
    -F "file=@$TEST_FILE" \
    -w "\nHTTP Status: %{http_code}\n" 2>/dev/null || true

echo ""
echo "Test complete!"