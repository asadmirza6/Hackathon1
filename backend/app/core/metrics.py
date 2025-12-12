"""Metrics collection module for the RAG Chatbot Backend.

Provides Prometheus-compatible metrics for monitoring and observability.
"""
import time
import functools
from typing import Callable, Dict, Any
from collections import defaultdict, Counter
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetricData:
    """Data structure for metric values."""
    value: float
    labels: Dict[str, str]
    timestamp: float


class MetricsCollector:
    """Centralized metrics collector for the application."""

    def __init__(self):
        """Initialize the metrics collector."""
        self._counters = defaultdict(int)
        self._gauges = {}
        self._histograms = defaultdict(list)
        self._summaries = defaultdict(list)

    def increment_counter(self, name: str, labels: Dict[str, str] = None, amount: int = 1) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name
            labels: Optional labels for the metric
            amount: Amount to increment by
        """
        key = f"{name}__{str(sorted(labels.items()) if labels else 'none')}"
        self._counters[key] += amount

    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name
            value: Value to set
            labels: Optional labels for the metric
        """
        key = f"{name}__{str(sorted(labels.items()) if labels else 'none')}"
        self._gauges[key] = value

    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Observe a value in a histogram.

        Args:
            name: Metric name
            value: Value to observe
            labels: Optional labels for the metric
        """
        key = f"{name}__{str(sorted(labels.items()) if labels else 'none')}"
        self._histograms[key].append(value)

    def observe_summary(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Observe a value in a summary.

        Args:
            name: Metric name
            value: Value to observe
            labels: Optional labels for the metric
        """
        key = f"{name}__{str(sorted(labels.items()) if labels else 'none')}"
        self._summaries[key].append(value)

    def get_counter_value(self, name: str, labels: Dict[str, str] = None) -> int:
        """Get the current value of a counter.

        Args:
            name: Metric name
            labels: Optional labels for the metric

        Returns:
            Current counter value
        """
        key = f"{name}__{str(sorted(labels.items()) if labels else 'none')}"
        return self._counters.get(key, 0)

    def get_gauge_value(self, name: str, labels: Dict[str, str] = None) -> float:
        """Get the current value of a gauge.

        Args:
            name: Metric name
            labels: Optional labels for the metric

        Returns:
            Current gauge value
        """
        key = f"{name}__{str(sorted(labels.items()) if labels else 'none')}"
        return self._gauges.get(key, 0.0)

    def get_histogram_stats(self, name: str, labels: Dict[str, str] = None) -> Dict[str, float]:
        """Get statistics for a histogram.

        Args:
            name: Metric name
            labels: Optional labels for the metric

        Returns:
            Dictionary with histogram statistics (count, sum, avg, min, max)
        """
        key = f"{name}__{str(sorted(labels.items()) if labels else 'none')}"
        values = self._histograms.get(key, [])
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}

        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }

    def get_summary_stats(self, name: str, labels: Dict[str, str] = None) -> Dict[str, float]:
        """Get statistics for a summary.

        Args:
            name: Metric name
            labels: Optional labels for the metric

        Returns:
            Dictionary with summary statistics
        """
        key = f"{name}__{str(sorted(labels.items()) if labels else 'none')}"
        values = self._summaries.get(key, [])
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}

        sorted_values = sorted(values)
        n = len(sorted_values)
        p50_idx = int(0.5 * n)
        p95_idx = int(0.95 * n)
        p99_idx = int(0.99 * n)

        return {
            "count": n,
            "sum": sum(sorted_values),
            "avg": sum(sorted_values) / n if n > 0 else 0,
            "min": sorted_values[0] if n > 0 else 0,
            "max": sorted_values[-1] if n > 0 else 0,
            "p50": sorted_values[p50_idx] if p50_idx < n else 0,
            "p95": sorted_values[p95_idx] if p95_idx < n else 0,
            "p99": sorted_values[p99_idx] if p99_idx < n else 0
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics.

        Returns:
            Dictionary containing all metrics
        """
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: self.get_histogram_stats(k.split("__")[0],
                dict(eval(k.split("__", 1)[1])) if "__" in k and k.split("__", 1)[1] != 'none' else None)
                for k in self._histograms.keys()},
            "summaries": {k: self.get_summary_stats(k.split("__")[0],
                dict(eval(k.split("__", 1)[1])) if "__" in k and k.split("__", 1)[1] != 'none' else None)
                for k in self._summaries.keys()}
        }

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._summaries.clear()


# Global metrics collector instance
metrics_collector = MetricsCollector()


def measure_duration(metric_name: str, labels: Dict[str, str] = None) -> Callable:
    """Decorator to measure the duration of a function call.

    Args:
        metric_name: Name of the metric to record duration
        labels: Optional labels for the metric

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.observe_histogram(metric_name, duration, labels)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.observe_histogram(metric_name, duration, labels)
                raise e
        return wrapper
    return decorator


def count_calls(metric_name: str, labels: Dict[str, str] = None) -> Callable:
    """Decorator to count function calls.

    Args:
        metric_name: Name of the metric to count calls
        labels: Optional labels for the metric

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            metrics_collector.increment_counter(metric_name, labels)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def record_error(metric_name: str, labels: Dict[str, str] = None) -> Callable:
    """Decorator to record errors.

    Args:
        metric_name: Name of the metric to record errors
        labels: Optional labels for the metric

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                metrics_collector.increment_counter(metric_name, labels)
                raise e
        return wrapper
    return decorator


# Predefined metric names for common operations
QUERY_DURATION_HISTOGRAM = "rag_query_duration_seconds"
RETRIEVAL_DURATION_HISTOGRAM = "rag_retrieval_duration_seconds"
GENERATION_DURATION_HISTOGRAM = "rag_generation_duration_seconds"
QUERY_TOTAL_COUNTER = "rag_query_total"
QUERY_ERROR_COUNTER = "rag_query_errors_total"
SUCCESS_RATE_GAUGE = "rag_success_rate"