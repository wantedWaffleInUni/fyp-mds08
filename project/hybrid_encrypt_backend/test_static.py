import requests
import os

# Test the static file serving
def test_static_serving():
    base_url = "http://localhost:5000"
    
    # First, create a test image
    print("Creating test image...")
    response = requests.get(f"{base_url}/test-static")
    if response.status_code == 200:
        data = response.json()
        print(f"Test image created: {data}")
        
        # Now try to access the static file
        print("\nTesting static file access...")
        static_url = f"{base_url}/static/test.png"
        print(f"Requesting: {static_url}")
        
        static_response = requests.get(static_url)
        print(f"Status code: {static_response.status_code}")
        print(f"Content type: {static_response.headers.get('content-type')}")
        print(f"Content length: {len(static_response.content)} bytes")
        
        if static_response.status_code == 200:
            print("✅ Static file serving is working!")
        else:
            print("❌ Static file serving failed!")
            print(f"Response: {static_response.text}")
    else:
        print(f"❌ Failed to create test image: {response.status_code}")

if __name__ == "__main__":
    test_static_serving()
