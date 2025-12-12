#!/usr/bin/env python3
"""Load testing script for the RAG chatbot API."""
import asyncio
import time
import statistics
from typing import List, Dict, Any
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
import requests  # Using requests instead of test client for actual HTTP load testing


class LoadTester:
    """Load testing class for the RAG chatbot API."""

    def __init__(self, base_url: str, num_users: int = 100, duration: int = 300):
        """
        Initialize the load tester.

        Args:
            base_url: Base URL of the API (e.g., http://localhost:8000)
            num_users: Number of concurrent users
            duration: Test duration in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.num_users = num_users
        self.duration = duration
        self.results: List[Dict[str, Any]] = []

    def make_request(self, question_id: int) -> Dict[str, Any]:
        """
        Make a single request to the API.

        Args:
            question_id: ID to identify the question

        Returns:
            Dictionary with request metrics
        """
        start_time = time.time()

        try:
            # Sample questions for load testing
            sample_questions = [
                "What is ZMP in bipedal walking?",
                "Explain the inverted pendulum model.",
                "How does dynamic walking work?",
                "What are the key principles of balance control?",
                "Describe the difference between static and dynamic balance."
            ]

            question = sample_questions[question_id % len(sample_questions)]
            session_id = f"load-test-{question_id % 1000}"  # Simulate different sessions

            response = requests.post(
                f"{self.base_url}/v1/query",
                json={
                    "question": question,
                    "session_id": session_id
                },
                timeout=30  # 30 second timeout
            )

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                "status_code": response.status_code,
                "response_time": response_time,
                "success": response.status_code == 200,
                "timestamp": start_time,
                "question_id": question_id
            }

        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            return {
                "status_code": 0,  # 0 indicates request failure
                "response_time": response_time,
                "success": False,
                "error": str(e),
                "timestamp": start_time,
                "question_id": question_id
            }

    def run_single_test(self, question_id: int) -> Dict[str, Any]:
        """Run a single test and return results."""
        return self.make_request(question_id)

    async def run_load_test(self) -> Dict[str, Any]:
        """
        Run the load test with specified parameters.

        Returns:
            Dictionary with test results and metrics
        """
        print(f"🚀 Starting load test...")
        print(f"  - Base URL: {self.base_url}")
        print(f"  - Concurrent users: {self.num_users}")
        print(f"  - Duration: {self.duration} seconds")
        print("-" * 50)

        start_time = time.time()
        completed_requests = 0
        failed_requests = 0

        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=self.num_users) as executor:
            futures = []
            question_id = 0

            # Continue making requests for the specified duration
            while (time.time() - start_time) < self.duration:
                # Submit a new request
                future = executor.submit(self.run_single_test, question_id)
                futures.append(future)
                question_id += 1

                # Process completed requests
                completed_now = 0
                for future in futures[:]:  # Create a copy to iterate safely
                    if future.done():
                        result = future.result()
                        self.results.append(result)

                        if not result["success"]:
                            failed_requests += 1
                        completed_requests += 1
                        completed_now += 1

                        # Remove completed future
                        futures.remove(future)

                        # Print progress every 10 requests
                        if completed_requests % 10 == 0:
                            print(f"  Processed {completed_requests} requests...")

                # Small delay to prevent overwhelming the executor
                await asyncio.sleep(0.01)

            # Wait for remaining requests to complete
            for future in futures:
                result = future.result()
                self.results.append(result)

                if not result["success"]:
                    failed_requests += 1
                completed_requests += 1

        total_time = time.time() - start_time

        # Calculate metrics
        successful_requests = len([r for r in self.results if r["success"]])
        response_times = [r["response_time"] for r in self.results if r["success"]]
        error_rate = (failed_requests / max(completed_requests, 1)) * 100 if completed_requests > 0 else 0

        metrics = {
            "total_requests": completed_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "error_rate_percent": error_rate,
            "total_time_seconds": total_time,
            "requests_per_second": completed_requests / total_time if total_time > 0 else 0,
            "response_times": response_times
        }

        if response_times:
            metrics.update({
                "avg_response_time_ms": statistics.mean(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "p50_response_time_ms": self._percentile(response_times, 50),
                "p95_response_time_ms": self._percentile(response_times, 95),
                "p99_response_time_ms": self._percentile(response_times, 99),
            })

        return metrics

    def _percentile(self, data: List[float], percentile: float) -> float:
        """
        Calculate percentile of response times.

        Args:
            data: List of response times
            percentile: Percentile to calculate (e.g., 50, 95, 99)

        Returns:
            Calculated percentile value
        """
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            fraction = index - int(index)
            return lower + fraction * (upper - lower)

    def print_results(self, metrics: Dict[str, Any]) -> None:
        """Print formatted test results."""
        print("\n" + "=" * 60)
        print("LOAD TEST RESULTS")
        print("=" * 60)

        print(f"Total Requests:     {metrics['total_requests']}")
        print(f"Successful:         {metrics['successful_requests']}")
        print(f"Failed:             {metrics['failed_requests']}")
        print(f"Error Rate:         {metrics['error_rate_percent']:.2f}%")
        print(f"Total Time:         {metrics['total_time_seconds']:.2f}s")
        print(f"Throughput:         {metrics['requests_per_second']:.2f} req/s")

        if metrics.get('response_times'):
            print(f"\nResponse Times:")
            print(f"  Average:          {metrics['avg_response_time_ms']:.2f}ms")
            print(f"  Minimum:          {metrics['min_response_time_ms']:.2f}ms")
            print(f"  Maximum:          {metrics['max_response_time_ms']:.2f}ms")
            print(f"  P50 (Median):     {metrics['p50_response_time_ms']:.2f}ms")
            print(f"  P95:              {metrics['p95_response_time_ms']:.2f}ms")
            print(f"  P99:              {metrics['p99_response_time_ms']:.2f}ms")

        print("=" * 60)

        # Performance assessment
        if metrics.get('p95_response_time_ms', float('inf')) < 3000:  # < 3s
            print("✅ P95 Response Time: GOOD (< 3s)")
        else:
            print("❌ P95 Response Time: POOR (>= 3s)")

        if metrics.get('error_rate_percent', 100) < 5:  # < 5% errors
            print("✅ Error Rate: GOOD (< 5%)")
        else:
            print("❌ Error Rate: POOR (>= 5%)")

        print("=" * 60)


async def main():
    """Main function to run the load test."""
    parser = argparse.ArgumentParser(description="Load test the RAG chatbot API")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--users",
        type=int,
        default=10,
        help="Number of concurrent users (default: 10)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Test duration in seconds (default: 60)"
    )

    args = parser.parse_args()

    # Validate inputs
    if args.users <= 0:
        print("Error: Number of users must be positive")
        sys.exit(1)

    if args.duration <= 0:
        print("Error: Duration must be positive")
        sys.exit(1)

    # Create load tester
    load_tester = LoadTester(
        base_url=args.base_url,
        num_users=args.users,
        duration=args.duration
    )

    try:
        # Run the load test
        metrics = await load_tester.run_load_test()

        # Print results
        load_tester.print_results(metrics)

    except KeyboardInterrupt:
        print("\n⚠️  Load test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during load test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())