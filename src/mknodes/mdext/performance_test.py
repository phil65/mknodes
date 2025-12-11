"""Performance comparison test for MkNodes markdown extension context modes.

This script demonstrates the performance difference between full context
and fallback context modes.
"""

from __future__ import annotations

import time

import markdown


def measure_performance(context: bool, iterations: int = 10) -> dict[str, float]:
    """Measure performance for a given context setting."""
    from mknodes.mdext import makeMkNodesExtension

    markdown_content = """
# Performance Test Document

/// mknodes
{{ "Performance Test" | MkHeader(level=2) }}
{{ mk.MkAdmonition(content="Testing performance with different context modes", typ="info") }}
{{ 50 | MkProgressBar }}
{{ mk.MkTable([["Mode", "Performance"], ["Full", "Complete but slower"], ["Fallback", "Fast but minimal"]]) }}
///

## Regular Markdown

This is regular markdown content that should render normally.

/// mknodes
{{ mk.MkCode(content="print('Hello from MkNodes!')", language="python") }}
{{ mk.MkList(["Item 1", "Item 2", "Item 3"]) }}
///
"""

    # Measure initialization time
    init_times = []
    render_times = []

    for _i in range(iterations):
        # Measure extension initialization
        init_start = time.perf_counter()
        md = markdown.Markdown(extensions=[makeMkNodesExtension(context=context)])
        init_end = time.perf_counter()
        init_times.append(init_end - init_start)

        # Measure rendering time
        render_start = time.perf_counter()
        result = md.convert(markdown_content)
        render_end = time.perf_counter()
        render_times.append(render_end - render_start)

        # Verify the result contains expected content
        assert len(result) > 100, f"Result too short: {len(result)} chars"  # noqa: PLR2004
        assert "Performance Test" in result, "Missing header content"

    return {
        "init_avg": sum(init_times) / len(init_times),
        "init_min": min(init_times),
        "init_max": max(init_times),
        "render_avg": sum(render_times) / len(render_times),
        "render_min": min(render_times),
        "render_max": max(render_times),
        "total_avg": sum(init_times) / len(init_times) + sum(render_times) / len(render_times),
    }


def run_performance_comparison(iterations: int = 20):
    """Run performance comparison between context settings."""
    print(f"Running performance comparison with {iterations} iterations each...\n")

    # Test with context=True (expensive)
    print("🔄 Testing with context=True...")
    context_stats = measure_performance(True, iterations)

    # Test with context=False (fast, default)
    print("🔄 Testing with context=False...")
    no_context_stats = measure_performance(False, iterations)

    # Display results
    print("=" * 80)
    print("PERFORMANCE COMPARISON RESULTS")
    print("=" * 80)

    print("\n📊 INITIALIZATION TIME")
    print("-" * 40)
    print(
        f"context=True:  {context_stats['init_avg']:.4f}s (avg) | {context_stats['init_min']:.4f}s (min) | {context_stats['init_max']:.4f}s (max)"
    )
    print(
        f"context=False: {no_context_stats['init_avg']:.4f}s (avg) | {no_context_stats['init_min']:.4f}s (min) | {no_context_stats['init_max']:.4f}s (max)"
    )

    init_speedup = context_stats["init_avg"] / no_context_stats["init_avg"]
    print(f"Speedup: {init_speedup:.2f}x faster with context=False")

    print("\n📊 RENDERING TIME")
    print("-" * 40)
    print(
        f"context=True:  {context_stats['render_avg']:.4f}s (avg) | {context_stats['render_min']:.4f}s (min) | {context_stats['render_max']:.4f}s (max)"
    )
    print(
        f"context=False: {no_context_stats['render_avg']:.4f}s (avg) | {no_context_stats['render_min']:.4f}s (min) | {no_context_stats['render_max']:.4f}s (max)"
    )

    render_speedup = context_stats["render_avg"] / no_context_stats["render_avg"]
    print(f"Speedup: {render_speedup:.2f}x faster with context=False")

    print("\n📊 TOTAL TIME")
    print("-" * 40)
    print(f"context=True:  {context_stats['total_avg']:.4f}s")
    print(f"context=False: {no_context_stats['total_avg']:.4f}s")

    total_speedup = context_stats["total_avg"] / no_context_stats["total_avg"]
    print(f"Overall speedup: {total_speedup:.2f}x faster with context=False")

    print("\n💡 RECOMMENDATIONS")
    print("-" * 40)
    if total_speedup > 2.0:  # noqa: PLR2004
        print("🚀 Significant performance improvement with context=False (default)!")
        print("   The default (context=False) is recommended for:")
        print("   - High-frequency rendering (web servers, CI/CD)")
        print("   - Simple content generation")
        print("   - Performance-critical applications")
    elif total_speedup > 1.5:  # noqa: PLR2004
        print("⚡ Notable performance improvement with context=False.")
        print("   Use the default when you don't need full project context.")
    else:
        print("📝 Minimal performance difference between context settings.")
        print("   Choose based on functionality needs rather than performance.")

    print("\n   Use context=True when you need:")
    print("   - Complete project information")
    print("   - All MkNodes features and metadata")
    print("   - Full context-dependent functionality")


def test_functionality_differences():
    """Test and document functionality differences between context modes."""
    print("\n" + "=" * 80)
    print("FUNCTIONALITY COMPARISON")
    print("=" * 80)

    # Test content that might work differently in each mode
    test_content = """
/// mknodes
{{ "Basic Components Test" | MkHeader(level=2) }}
{{ mk.MkText("This should work in both modes") }}
{{ mk.MkAdmonition(content="Testing basic functionality", typ="info") }}
{{ mk.MkCode(content="print('Hello World!')", language="python") }}
///
"""

    from mknodes.mdext import makeMkNodesExtension

    print("\n🔍 Testing functionality in both modes...")

    # Test with context=True
    try:
        md_context = markdown.Markdown(extensions=[makeMkNodesExtension(context=True)])
        result_context = md_context.convert(test_content)
        context_success = (
            "mknodes-rendered" in result_context and "Basic Components Test" in result_context
        )
        print(f"context=True:  {'✅ Success' if context_success else '❌ Failed'}")
    except Exception as e:  # noqa: BLE001
        print(f"context=True:  ❌ Error: {e}")
        context_success = False

    # Test with context=False (default)
    try:
        md_no_context = markdown.Markdown(extensions=[makeMkNodesExtension(context=False)])
        result_no_context = md_no_context.convert(test_content)
        no_context_success = (
            "mknodes-rendered" in result_no_context and "Basic Components Test" in result_no_context
        )
        print(f"context=False: {'✅ Success' if no_context_success else '❌ Failed'}")
    except Exception as e:  # noqa: BLE001
        print(f"context=False: ❌ Error: {e}")
        no_context_success = False

    if context_success and no_context_success:
        print("\n✅ Both context settings support basic MkNodes functionality")
    elif context_success:
        print("\n⚠️  Only context=True works for this content")
    elif no_context_success:
        print("\n⚠️  Only context=False works for this content")
    else:
        print("\n❌ Neither context setting works for this content")


if __name__ == "__main__":
    print("MkNodes Extension Performance Test")
    print("=" * 50)

    try:
        run_performance_comparison(iterations=10)
        test_functionality_differences()

        print("\n" + "=" * 80)
        print("✅ Performance test completed!")
        print("\nTo run with more iterations for better accuracy:")
        print("python performance_test.py --iterations 50")

    except Exception as e:  # noqa: BLE001
        print(f"\n❌ Performance test failed: {e}")
        import traceback

        traceback.print_exc()
