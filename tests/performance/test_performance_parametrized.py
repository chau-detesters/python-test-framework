# test_performance_parametrized.py
"""
Parametric performance tests for different scenarios and loads.
"""
import pytest
import time
import asyncio
import statistics
from typing import List, Tuple

class TestPerformanceParametrized:
    """Parametrized performance testing"""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("concurrent_requests", [1, 5, 10, 25, 50])
    async def test_concurrent_load(self, http_client, concurrent_requests):
        """Test API under different concurrent loads"""
        
        async def make_request():
            start_time = time.time()
            response = await http_client.get("/users")
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        # Execute concurrent requests
        tasks = [make_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        status_codes = [result[0] for result in results]
        response_times = [result[1] for result in results]
        
        # All requests should succeed
        assert all(status == 200 for status in status_codes)
        
        # Calculate detailed metrics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        median_response_time = statistics.median(response_times)
        
        # Calculate 95th percentile only if we have enough data points
        if len(response_times) >= 20:
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        else:
            p95_response_time = max_response_time  # Use max as approximation
        
        # Calculate standard deviation only if we have enough data points
        if len(response_times) >= 2:
            std_dev = statistics.stdev(response_times)
        else:
            std_dev = 0.0
        
        print(f"\n=== CONCURRENT LOAD TEST ===")
        print(f"Concurrent requests: {concurrent_requests}")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Median response time: {median_response_time:.3f}s")
        print(f"Min response time: {min_response_time:.3f}s")
        print(f"Max response time: {max_response_time:.3f}s")
        print(f"95th percentile: {p95_response_time:.3f}s")
        print(f"Standard deviation: {std_dev:.3f}s")
        print(f"===============================")
        
        # Dynamic thresholds based on load
        if concurrent_requests <= 5:
            assert avg_response_time < 1.0
            assert max_response_time < 2.0
        elif concurrent_requests <= 25:
            assert avg_response_time < 2.0
            assert max_response_time < 5.0
        else:  # 50+ concurrent requests
            assert avg_response_time < 5.0
            assert max_response_time < 10.0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint,max_response_time", [
        ("/users", 2.0),
        ("/posts", 3.0),
        ("/albums", 2.5),
        ("/todos", 3.5),
    ])
    async def test_endpoint_performance_thresholds(self, http_client, endpoint, max_response_time):
        """Test performance thresholds for different endpoints"""
        start_time = time.time()
        response = await http_client.get(endpoint)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < max_response_time, \
            f"Endpoint {endpoint} took {response_time:.3f}s, expected < {max_response_time}s"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("load_scenario", [
        {"name": "Light Load", "concurrent": 3, "expected_avg": 0.5},
        {"name": "Medium Load", "concurrent": 10, "expected_avg": 1.0},
        {"name": "Heavy Load", "concurrent": 25, "expected_avg": 2.0},
        {"name": "Stress Load", "concurrent": 50, "expected_avg": 3.0},
        {"name": "Peak Load", "concurrent": 100, "expected_avg": 5.0},
    ])
    async def test_load_scenarios(self, http_client, load_scenario):
        """Test different load scenarios with detailed analysis"""
        
        async def make_request():
            start_time = time.time()
            response = await http_client.get("/users")
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        print(f"\n=== LOAD SCENARIO: {load_scenario['name']} ===")
        print(f"Target concurrent requests: {load_scenario['concurrent']}")
        
        # Execute concurrent requests
        tasks = [make_request() for _ in range(load_scenario['concurrent'])]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        status_codes = [result[0] for result in results]
        response_times = [result[1] for result in results]
        
        # Calculate metrics
        success_rate = sum(1 for code in status_codes if code == 200) / len(status_codes) * 100
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Calculate 95th percentile only if we have enough data points
        if len(response_times) >= 20:
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
        else:
            p95_response_time = max_response_time  # Use max as approximation
        
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Average response time: {avg_response_time:.3f}s (expected: {load_scenario['expected_avg']}s)")
        print(f"95th percentile: {p95_response_time:.3f}s")
        print(f"Max response time: {max_response_time:.3f}s")
        
        # Assertions
        assert success_rate >= 95.0, f"Success rate {success_rate}% below 95% threshold"
        assert avg_response_time < load_scenario['expected_avg'] * 2, \
            f"Average response time {avg_response_time:.3f}s exceeds {load_scenario['expected_avg'] * 2}s"
        
        print(f"=== END: {load_scenario['name']} ===\n")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("endpoint", ["/users", "/posts", "/albums", "/todos"])
    @pytest.mark.parametrize("concurrent_load", [5, 15, 30])
    async def test_endpoint_concurrent_load(self, http_client, endpoint, concurrent_load):
        """Test concurrent load on different endpoints"""
        
        async def make_request():
            start_time = time.time()
            response = await http_client.get(endpoint)
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        print(f"\n=== ENDPOINT CONCURRENT TEST ===")
        print(f"Endpoint: {endpoint}")
        print(f"Concurrent load: {concurrent_load}")
        
        # Execute concurrent requests
        tasks = [make_request() for _ in range(concurrent_load)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        status_codes = [result[0] for result in results]
        response_times = [result[1] for result in results]
        
        success_count = sum(1 for code in status_codes if code == 200)
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        print(f"Successful requests: {success_count}/{concurrent_load}")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Max response time: {max_response_time:.3f}s")
        
        # Assertions
        assert success_count >= concurrent_load * 0.95, f"Success rate too low: {success_count}/{concurrent_load}"
        
        # Endpoint-specific thresholds
        if endpoint == "/users":
            assert avg_response_time < 1.5
        elif endpoint == "/posts":
            assert avg_response_time < 2.0
        elif endpoint == "/albums":
            assert avg_response_time < 1.8
        elif endpoint == "/todos":
            assert avg_response_time < 2.2
        
        print(f"=== END: {endpoint} ===\n")

    @pytest.mark.asyncio
    async def test_burst_load(self, http_client):
        """Test burst load pattern - sudden spike in requests"""
        
        async def make_request():
            start_time = time.time()
            response = await http_client.get("/users")
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        print(f"\n=== BURST LOAD TEST ===")
        
        # Simulate burst pattern: 5 requests, then 50, then 5 again
        burst_patterns = [5, 50, 5]
        all_results = []
        
        for i, burst_size in enumerate(burst_patterns):
            print(f"Burst {i+1}: {burst_size} concurrent requests")
            
            tasks = [make_request() for _ in range(burst_size)]
            results = await asyncio.gather(*tasks)
            all_results.extend(results)
            
            # Brief pause between bursts
            if i < len(burst_patterns) - 1:
                await asyncio.sleep(1)
        
        # Analyze overall results
        status_codes = [result[0] for result in all_results]
        response_times = [result[1] for result in all_results]
        
        success_rate = sum(1 for code in status_codes if code == 200) / len(status_codes) * 100
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        print(f"Total requests: {len(all_results)}")
        print(f"Overall success rate: {success_rate:.1f}%")
        print(f"Overall average response time: {avg_response_time:.3f}s")
        print(f"Overall max response time: {max_response_time:.3f}s")
        
        # Assertions
        assert success_rate >= 90.0, f"Overall success rate {success_rate}% below 90% threshold"
        assert avg_response_time < 3.0, f"Overall average response time {avg_response_time:.3f}s too high"
        
        print(f"=== END: BURST LOAD ===\n") 