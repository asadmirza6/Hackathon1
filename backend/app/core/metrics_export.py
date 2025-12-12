"""Metrics export module for Prometheus-compatible metrics endpoint."""
from typing import Dict, Any, List
import time
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from app.core.metrics import metrics_collector


router = APIRouter()


def format_metrics_for_prometheus() -> str:
    """Format collected metrics in Prometheus text format.

    Returns:
        Metrics in Prometheus text format
    """
    output_lines = []

    # Add timestamp comment
    output_lines.append(f"# Generated at {int(time.time())}")
    output_lines.append("")

    # Process counters
    for key, value in metrics_collector._counters.items():
        # Extract metric name and labels
        if "__" in key:
            metric_name, labels_part = key.split("__", 1)
            if labels_part != 'none':
                try:
                    labels_dict = eval(labels_part)  # In production, use proper parsing
                    labels_str = ",".join([f'{k}="{v}"' for k, v in labels_dict.items()])
                    output_lines.append(f"{metric_name}{{{labels_str}}} {value}")
                except:
                    output_lines.append(f"{metric_name} {value}")
            else:
                output_lines.append(f"{metric_name} {value}")
        else:
            output_lines.append(f"{key} {value}")

    output_lines.append("")

    # Process gauges
    for key, value in metrics_collector._gauges.items():
        if "__" in key:
            metric_name, labels_part = key.split("__", 1)
            if labels_part != 'none':
                try:
                    labels_dict = eval(labels_part)
                    labels_str = ",".join([f'{k}="{v}"' for k, v in labels_dict.items()])
                    output_lines.append(f"{metric_name}{{{labels_str}}} {value}")
                except:
                    output_lines.append(f"{metric_name} {value}")
            else:
                output_lines.append(f"{metric_name} {value}")
        else:
            output_lines.append(f"{key} {value}")

    output_lines.append("")

    # Process histograms (as summaries for simplicity)
    for key in metrics_collector._histograms.keys():
        if "__" in key:
            metric_name, labels_part = key.split("__", 1)
            stats = metrics_collector.get_histogram_stats(
                metric_name,
                eval(labels_part) if labels_part != 'none' else None
            )

            if labels_part != 'none':
                try:
                    labels_dict = eval(labels_part)
                    labels_str = ",".join([f'{k}="{v}"' for k, v in labels_dict.items()])
                    output_lines.append(f"{metric_name}_count{{{labels_str}}} {stats['count']}")
                    output_lines.append(f"{metric_name}_sum{{{labels_str}}} {stats['sum']}")
                except:
                    output_lines.append(f"{metric_name}_count {stats['count']}")
                    output_lines.append(f"{metric_name}_sum {stats['sum']}")
            else:
                output_lines.append(f"{metric_name}_count {stats['count']}")
                output_lines.append(f"{metric_name}_sum {stats['sum']}")

    output_lines.append("")

    # Process summaries
    for key in metrics_collector._summaries.keys():
        if "__" in key:
            metric_name, labels_part = key.split("__", 1)
            stats = metrics_collector.get_summary_stats(
                metric_name,
                eval(labels_part) if labels_part != 'none' else None
            )

            if labels_part != 'none':
                try:
                    labels_dict = eval(labels_part)
                    labels_str = ",".join([f'{k}="{v}"' for k, v in labels_dict.items()])
                    output_lines.append(f"{metric_name}_count{{{labels_str}}} {stats['count']}")
                    output_lines.append(f"{metric_name}_sum{{{labels_str}}} {stats['sum']}")
                    output_lines.append(f"{metric_name}_avg{{{labels_str}}} {stats['avg']}")
                    output_lines.append(f"{metric_name}_min{{{labels_str}}} {stats['min']}")
                    output_lines.append(f"{metric_name}_max{{{labels_str}}} {stats['max']}")
                    output_lines.append(f"{metric_name}_p50{{{labels_str}}} {stats['p50']}")
                    output_lines.append(f"{metric_name}_p95{{{labels_str}}} {stats['p95']}")
                    output_lines.append(f"{metric_name}_p99{{{labels_str}}} {stats['p99']}")
                except:
                    output_lines.append(f"{metric_name}_count {stats['count']}")
                    output_lines.append(f"{metric_name}_sum {stats['sum']}")
            else:
                output_lines.append(f"{metric_name}_count {stats['count']}")
                output_lines.append(f"{metric_name}_sum {stats['sum']}")

    return "\n".join(output_lines)


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """Get metrics in Prometheus format.

    Returns:
        Plain text response with metrics in Prometheus format
    """
    return format_metrics_for_prometheus()


@router.get("/health/metrics")
async def get_metrics_status():
    """Get metrics collection status.

    Returns:
        Dictionary with metrics collection status
    """
    all_metrics = metrics_collector.get_all_metrics()

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "metrics_collected": {
            "counters": len(all_metrics["counters"]),
            "gauges": len(all_metrics["gauges"]),
            "histograms": len(all_metrics["histograms"]),
            "summaries": len(all_metrics["summaries"]),
        },
        "total_metrics": sum([
            len(all_metrics["counters"]),
            len(all_metrics["gauges"]),
            len(all_metrics["histograms"]),
            len(all_metrics["summaries"]),
        ])
    }


@router.post("/metrics/reset")
async def reset_metrics():
    """Reset all collected metrics.

    Returns:
        Dictionary confirming reset
    """
    metrics_collector.reset_metrics()
    return {
        "status": "reset",
        "message": "All metrics have been reset",
        "timestamp": time.time()
    }


@router.get("/metrics/overview")
async def get_metrics_overview():
    """Get a human-readable overview of metrics.

    Returns:
        Dictionary with metrics overview
    """
    all_metrics = metrics_collector.get_all_metrics()

    overview = {
        "timestamp": time.time(),
        "summary": {
            "total_requests": all_metrics["counters"].get("rag_query_total__none", 0),
            "total_errors": all_metrics["counters"].get("rag_query_errors_total__none", 0),
            "success_rate": 0,
        },
        "performance": {
            "query_duration_avg": 0,
            "retrieval_duration_avg": 0,
            "generation_duration_avg": 0,
        },
        "details": all_metrics
    }

    # Calculate success rate
    total_requests = overview["summary"]["total_requests"]
    total_errors = overview["summary"]["total_errors"]
    if total_requests > 0:
        overview["summary"]["success_rate"] = (total_requests - total_errors) / total_requests

    # Calculate average durations if available
    query_duration_stats = all_metrics["histograms"].get("rag_query_duration_seconds__none", {})
    if query_duration_stats and query_duration_stats["count"] > 0:
        overview["performance"]["query_duration_avg"] = query_duration_stats["avg"]

    retrieval_duration_stats = all_metrics["histograms"].get("rag_retrieval_duration_seconds__none", {})
    if retrieval_duration_stats and retrieval_duration_stats["count"] > 0:
        overview["performance"]["retrieval_duration_avg"] = retrieval_duration_stats["avg"]

    generation_duration_stats = all_metrics["histograms"].get("rag_generation_duration_seconds__none", {})
    if generation_duration_stats and generation_duration_stats["count"] > 0:
        overview["performance"]["generation_duration_avg"] = generation_duration_stats["avg"]

    return overview


# Additional utility functions for metrics
def increment_error_counter(operation: str, service: str = "unknown"):
    """Increment the error counter for a specific operation.

    Args:
        operation: The operation that failed
        service: The service where the error occurred
    """
    metrics_collector.increment_counter(
        "rag_operation_errors_total",
        {"operation": operation, "service": service}
    )


def record_operation_duration(operation: str, duration: float, service: str = "unknown"):
    """Record the duration of an operation.

    Args:
        operation: The operation being measured
        duration: Duration in seconds
        service: The service performing the operation
    """
    metrics_collector.observe_histogram(
        "rag_operation_duration_seconds",
        duration,
        {"operation": operation, "service": service}
    )


def set_service_status(service: str, status: str):
    """Set the status of a service.

    Args:
        service: Name of the service
        status: Status of the service (e.g., "up", "down", "degraded")
    """
    status_map = {"up": 1, "down": 0, "degraded": 0.5}
    metrics_collector.set_gauge(
        "rag_service_status",
        status_map.get(status, 0),
        {"service": service}
    )