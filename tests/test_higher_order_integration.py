import unittest
import sys
import os
import logging
from unittest.mock import MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import the higher-order function utilities
from fp_decorators.higher_order import (
    compose, pipe, curry, partial, memoize, higher_order
)

class TestHigherOrderMinimal(unittest.TestCase):
    """
    simple integration test that proves the higher-order functions work correctly
    when used with functions similar to those in the codebase.
    """
    
    def setUp(self):
        # Setup test data - mock endpoint objects
        self.endpoints = []
        for i in range(5):
            endpoint = MagicMock()
            endpoint.ip = f"192.168.1.{i+1}"
            endpoint.port = 8080 + i
            endpoint.delay = 10 * (i + 1)  # 10, 20, 30...
            endpoint.loss = 0.01 * (i + 1)  # 0.01, 0.02, 0.03...
            self.endpoints.append(endpoint)
    
    def test_curry_for_filtering(self):
        """Test using curry with filter functions similar to your codebase."""
        # Define a curried filter function similar to your codebase
        @curry
        def filter_by_delay(max_delay, endpoints):
            return [e for e in endpoints if e.delay <= max_delay]
        
        # Create a specialized version
        low_delay_filter = filter_by_delay(25)
        
        # Apply it to our test data
        filtered = low_delay_filter(self.endpoints)
        
        # Verify it works as expected
        self.assertEqual(len(filtered), 2)  # Only first 2 have delay <= 25
        self.assertEqual(filtered[0].ip, "192.168.1.1")
        self.assertEqual(filtered[1].ip, "192.168.1.2")
    
    def test_memoize_for_caching(self):
        """Test using memoize to cache function results."""
        call_count = 0
        
        # Define a function similar to getEntrypoints
        def get_test_endpoints(ipv6=False):
            nonlocal call_count
            call_count += 1
            # Return different data based on ipv6 flag
            if ipv6:
                return self.endpoints[:2]  # Just first 2 for IPv6
            return self.endpoints
        
        # Create memoized version
        memoized_get = memoize(get_test_endpoints)
        
        # Call it multiple times with same args
        result1 = memoized_get(ipv6=False)
        result2 = memoized_get(ipv6=False)
        
        # Verify caching worked
        self.assertEqual(call_count, 1)  # Only called once
        self.assertEqual(len(result1), 5)
        self.assertEqual(result1, result2)
        
        # Call with different args
        result3 = memoized_get(ipv6=True)
        
        # Verify it executed again
        self.assertEqual(call_count, 2)
        self.assertEqual(len(result3), 2)
    
    def test_pipe_for_data_processing(self):
        """Test using pipe to create a data processing pipeline."""
        # Define filter functions that take data as input
        def filter_delay(data, max_delay=30):
            return [e for e in data if e.delay <= max_delay]
            
        def filter_loss(data, max_loss=0.03):
            return [e for e in data if e.loss <= max_loss]
            
        def sort_quality(data):
            return sorted(data, key=lambda x: (x.loss, x.delay))
            
        def limit_results(data, count=2):
            return data[:count]
        
        # Create partial applications that take a single data argument
        delay_filter = lambda data: filter_delay(data, max_delay=25)
        loss_filter = lambda data: filter_loss(data, max_loss=0.02)
        result_limiter = lambda data: limit_results(data, count=2)
        
        # Create a pipeline that starts with the data
        pipeline = pipe(
            delay_filter,       # Filter by delay
            loss_filter,        # Filter by loss
            sort_quality,       # Sort by quality
            result_limiter      # Limit to top 2
        )
        
        # Execute the pipeline with the initial data
        results = pipeline(self.endpoints)
        
        # Verify the pipeline works correctly
        self.assertEqual(len(results), 2)
        for endpoint in results:
            self.assertTrue(endpoint.delay <= 25)
            self.assertTrue(endpoint.loss <= 0.02)
    
    def test_higher_order_decorator(self):
        """Test the higher-order decorator enhances functions."""
        # Define a function using the decorator
        @higher_order(enhanced=True)
        def get_best_endpoints(num=2, max_delay=None, max_loss=None):
            # Get all endpoints
            data = self.endpoints
            
            # Apply filters if specified
            if max_delay is not None:
                data = [e for e in data if e.delay <= max_delay]
            
            if max_loss is not None:
                data = [e for e in data if e.loss <= max_loss]
            
            # Sort by quality
            data = sorted(data, key=lambda x: (x.loss, x.delay))
            
            # Return limited results
            return data[:num]
        
        # Test the function directly
        normal_results = get_best_endpoints(max_delay=25, max_loss=0.02)
        self.assertEqual(len(normal_results), 2)
        
        # Test the enhanced capabilities - partial application
        get_low_latency = get_best_endpoints.partial(max_delay=15)
        low_latency_results = get_low_latency(max_loss=0.01)
        
        # Verify the partial application worked
        self.assertEqual(len(low_latency_results), 1)
        self.assertEqual(low_latency_results[0].ip, "192.168.1.1")

if __name__ == '__main__':
    unittest.main()