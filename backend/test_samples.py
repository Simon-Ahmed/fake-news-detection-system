#!/usr/bin/env python3
"""
Test samples for the Fake News Detection API
Run this script to test the API with various sample texts
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

# Test cases with expected results
test_cases = [
    {
        "text": "According to a new study published in Nature, moderate coffee consumption reduces heart disease risk by 15%. The research followed 500,000 participants over 10 years.",
        "expected": "real",
        "description": "Legitimate scientific news with proper attribution"
    },
    {
        "text": "SHOCKING: Doctors hate this one trick to lose 20lbs in 3 days! Click here for the secret that will change your life forever! Amazing results guaranteed!",
        "expected": "fake",
        "description": "Classic clickbait with unrealistic claims"
    },
    {
        "text": "The Federal Reserve announced a 0.25% increase in interest rates today, citing concerns about inflation. The decision was unanimous among board members.",
        "expected": "real",
        "description": "Standard financial news reporting"
    },
    {
        "text": "BREAKING: Aliens have landed in New York City! Government officials are hiding the truth from the public! Exclusive footage shows UFOs over Manhattan!",
        "expected": "fake",
        "description": "Sensational fake news with conspiracy elements"
    },
    {
        "text": "Local community center opens new after-school program for children. The program will provide tutoring and recreational activities Monday through Friday.",
        "expected": "real",
        "description": "Simple local news story"
    },
    {
        "text": "Scientists HATE him! This man discovered the secret to eternal youth using this ONE WEIRD TRICK! Doctors are FURIOUS! Click to see what Big Pharma doesn't want you to know!",
        "expected": "fake",
        "description": "Multiple clickbait patterns and conspiracy language"
    }
]

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return False

def test_single_predictions():
    """Test single text predictions"""
    print("\n🔍 Testing single predictions...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['description']} ---")
        print(f"Expected: {test_case['expected']}")
        print(f"Text: {test_case['text'][:100]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/predict",
                json={"text": test_case["text"], "language": "en"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                prediction = result["prediction"]
                confidence = result["confidence"]
                
                print(f"✅ Prediction: {prediction} ({confidence:.1f}% confidence)")
                print(f"   Explanation: {result['explanation']}")
                
                if result.get("factors"):
                    print("   Key factors:")
                    for factor in result["factors"][:3]:  # Show top 3 factors
                        print(f"   - {factor['name']}: {factor['description']}")
                
                # Check if prediction matches expectation
                if prediction == test_case["expected"]:
                    print("🎯 Prediction matches expectation!")
                else:
                    print(f"⚠️  Prediction differs from expectation ({test_case['expected']})")
                    
            elif response.status_code == 503:
                print("⚠️  ML model not ready (503)")
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        time.sleep(1)  # Brief pause between requests

def test_batch_prediction():
    """Test batch prediction"""
    print("\n📦 Testing batch prediction...")
    
    texts = [case["text"] for case in test_cases[:3]]  # Use first 3 test cases
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/batch-predict",
            json={"texts": texts, "language": "en"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch prediction successful")
            print(f"   Processed: {result['total_processed']} texts")
            print(f"   Total time: {result['processing_time']:.2f}s")
            
            for i, prediction in enumerate(result["predictions"]):
                expected = test_cases[i]["expected"]
                actual = prediction["prediction"]
                confidence = prediction["confidence"]
                print(f"   Text {i+1}: {actual} ({confidence:.1f}%) - Expected: {expected}")
                
        elif response.status_code == 503:
            print("⚠️  ML model not ready (503)")
        else:
            print(f"❌ Batch prediction failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_url_prediction():
    """Test URL prediction (with a placeholder)"""
    print("\n🌐 Testing URL prediction...")
    print("ℹ️  URL prediction requires a valid news article URL")
    print("   Skipping automated test - try manually with a real news URL")

def test_stats():
    """Test stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats retrieved successfully:")
            print(f"   Total predictions: {stats.get('total_predictions', 0)}")
            print(f"   Model version: {stats.get('model_version', 'unknown')}")
            print(f"   Average confidence: {stats.get('avg_confidence', 0):.1f}%")
        else:
            print(f"⚠️  Stats request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_history():
    """Test history endpoint"""
    print("\n📚 Testing history endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/history?limit=5")
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ History retrieved successfully:")
            print(f"   Total predictions in history: {history.get('total', 0)}")
            print(f"   Retrieved: {len(history.get('predictions', []))} predictions")
        else:
            print(f"❌ History request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Fake News Detection API Test Suite")
    print("=" * 50)
    
    # Test health first
    if not test_health():
        print("\n❌ Cannot proceed - API is not healthy")
        return
    
    # Run all tests
    test_single_predictions()
    test_batch_prediction()
    test_url_prediction()
    test_stats()
    test_history()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\nTo test manually:")
    print(f"- API Documentation: {BASE_URL}/docs")
    print(f"- Health Check: {BASE_URL}/health")
    print(f"- Interactive API: {BASE_URL}/docs")

if __name__ == "__main__":
    main()