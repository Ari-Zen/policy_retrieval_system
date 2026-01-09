#!/usr/bin/env python3
"""
Test script for Policy-Aware Knowledge Retrieval System

This script tests the end-to-end flow:
1. Seeds sample data
2. Makes test queries
3. Validates responses
"""
import requests
from datetime import date
import json


BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test that the API is running"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_seed_data():
    """Test seeding sample data"""
    print("\n=== Seeding Sample Data ===")
    response = requests.post(f"{BASE_URL}/seed-data")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Policies uploaded: {result.get('policies_uploaded')}")
    print(f"Clauses uploaded: {result.get('clauses_uploaded')}")
    return response.status_code == 200


def test_query_standard_refund():
    """Test a standard refund query"""
    print("\n=== Test Query 1: Standard Refund ===")

    request_data = {
        "query": "Can I get a refund for a product I bought 2 weeks ago?",
        "jurisdiction": "US",
        "as_of_date": "2024-06-15",
        "role": "customer"
    }

    print(f"Query: {request_data['query']}")
    print(f"Role: {request_data['role']}")
    print(f"Jurisdiction: {request_data['jurisdiction']}")

    response = requests.post(f"{BASE_URL}/answer", json=request_data)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Decision Status: {result.get('decision_status')}")
        print(f"Decision Reason: {result.get('decision_reason')}")
        print(f"Policy IDs: {result.get('policy_ids')}")
        print(f"Clause IDs: {result.get('clause_ids')}")

        if result.get('answer'):
            print(f"\nAnswer:\n{result.get('answer')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_query_premium_refund():
    """Test a premium member refund query"""
    print("\n=== Test Query 2: Premium Member Refund ===")

    request_data = {
        "query": "As a premium member, what is my refund window?",
        "jurisdiction": "US",
        "as_of_date": "2024-06-15",
        "role": "premium_customer"
    }

    print(f"Query: {request_data['query']}")
    print(f"Role: {request_data['role']}")
    print(f"Jurisdiction: {request_data['jurisdiction']}")

    response = requests.post(f"{BASE_URL}/answer", json=request_data)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Decision Status: {result.get('decision_status')}")
        print(f"Decision Reason: {result.get('decision_reason')}")
        print(f"Policy IDs: {result.get('policy_ids')}")

        if result.get('answer'):
            print(f"\nAnswer:\n{result.get('answer')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_query_digital_product():
    """Test a digital product refund query"""
    print("\n=== Test Query 3: Digital Product Refund ===")

    request_data = {
        "query": "Can I get a refund for an ebook I already downloaded?",
        "jurisdiction": "US",
        "as_of_date": "2024-06-15",
        "role": "customer"
    }

    print(f"Query: {request_data['query']}")
    print(f"Role: {request_data['role']}")
    print(f"Jurisdiction: {request_data['jurisdiction']}")

    response = requests.post(f"{BASE_URL}/answer", json=request_data)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Decision Status: {result.get('decision_status')}")
        print(f"Decision Reason: {result.get('decision_reason')}")

        if result.get('answer'):
            print(f"\nAnswer:\n{result.get('answer')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_query_eu_jurisdiction():
    """Test an EU jurisdiction query"""
    print("\n=== Test Query 4: EU Jurisdiction ===")

    request_data = {
        "query": "What are my return rights as an EU customer?",
        "jurisdiction": "EU",
        "as_of_date": "2024-06-15",
        "role": "customer"
    }

    print(f"Query: {request_data['query']}")
    print(f"Role: {request_data['role']}")
    print(f"Jurisdiction: {request_data['jurisdiction']}")

    response = requests.post(f"{BASE_URL}/answer", json=request_data)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Decision Status: {result.get('decision_status')}")
        print(f"Decision Reason: {result.get('decision_reason')}")

        if result.get('answer'):
            print(f"\nAnswer:\n{result.get('answer')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def view_audit_records():
    """View all audit records"""
    print("\n=== Viewing Audit Records ===")
    response = requests.get(f"{BASE_URL}/audit")
    if response.status_code == 200:
        result = response.json()
        print(f"Total audit records: {result.get('total_records')}")
    else:
        print(f"Error: {response.text}")


def main():
    """Run all tests"""
    print("=" * 70)
    print("POLICY-AWARE KNOWLEDGE RETRIEVAL SYSTEM - TEST SUITE")
    print("=" * 70)

    try:
        # Test health check
        if not test_health_check():
            print("\n❌ Health check failed. Is the server running?")
            print("Start the server with: uvicorn app:app --reload")
            return

        # Seed data
        if not test_seed_data():
            print("\n❌ Data seeding failed")
            return

        print("\n" + "=" * 70)
        print("RUNNING TEST QUERIES")
        print("=" * 70)

        # Run test queries
        test_query_standard_refund()
        test_query_premium_refund()
        test_query_digital_product()
        test_query_eu_jurisdiction()

        # View audit records
        view_audit_records()

        print("\n" + "=" * 70)
        print("✓ All tests completed!")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the server.")
        print("Make sure the server is running with: uvicorn app:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
