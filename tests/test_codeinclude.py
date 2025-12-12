"""Tests for the CodeInclude markdown extension."""

from __future__ import annotations

from pathlib import Path
import tempfile

import markdown
import pytest

from mknodes.mdext import makeCodeIncludeExtension


def test_basic_file_include():
    """Test basic file inclusion with code block wrapping."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "example.py"
        test_file.write_text("def hello():\n    return 'world'\n")

        md_content = '@@@codeinclude "example.py"'
        md = markdown.Markdown(
            extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
        )
        result = md.convert(md_content)

        assert "python" in result
        assert "example.py" in result
        assert "def hello():" in result


def test_multiple_file_types():
    """Test automatic language detection for different file types."""
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "script.py"
        py_file.write_text("print('hello')")

        js_file = Path(tmpdir) / "script.js"
        js_file.write_text("console.log('hello');")

        yaml_file = Path(tmpdir) / "config.yml"
        yaml_file.write_text("key: value")

        md_content = """
@@@codeinclude "script.py"

@@@codeinclude "script.js"

@@@codeinclude "config.yml"
"""

        md = markdown.Markdown(
            extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
        )
        result = md.convert(md_content)

        assert "python" in result
        assert "javascript" in result
        assert "yaml" in result
        assert "script.py" in result
        assert "script.js" in result
        assert "config.yml" in result


def test_missing_file_no_check():
    """Test that missing files are silently ignored when check_paths=False."""
    md_content = '@@@codeinclude "nonexistent.py"'
    md = markdown.Markdown(extensions=["fenced_code", makeCodeIncludeExtension(check_paths=False)])
    result = md.convert(md_content)

    # Should not raise and return empty or minimal content
    assert isinstance(result, str)


def test_missing_file_with_check():
    """Test that missing files raise error when check_paths=True."""
    from mknodes.mdext.codeinclude import CodeIncludeError

    md_content = '@@@codeinclude "nonexistent.py"'
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            makeCodeIncludeExtension(base_path=["."], check_paths=True),
        ]
    )

    with pytest.raises(CodeIncludeError, match="could not be found"):
        md.convert(md_content)


def test_language_detection():
    """Test language detection from various file extensions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        extensions_map = {
            "test.py": "python",
            "test.js": "javascript",
            "test.ts": "typescript",
            "test.rs": "rust",
            "test.go": "go",
            "test.java": "java",
            "test.rb": "ruby",
            "test.sh": "bash",
            "test.yaml": "yaml",
            "test.json": "json",
            "test.html": "html",
            "test.css": "css",
        }

        for filename, expected_lang in extensions_map.items():
            file_path = Path(tmpdir) / filename
            file_path.write_text("content")

            md_content = f'@@@codeinclude "{filename}"'
            md = markdown.Markdown(
                extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
            )
            result = md.convert(md_content)

            assert expected_lang in result, f"Expected {expected_lang} for {filename}"
            assert filename in result


def test_file_with_title():
    """Test that included files get title attribute."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "myfile.py"
        test_file.write_text("# content")

        md_content = '@@@codeinclude "myfile.py"'
        md = markdown.Markdown(
            extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
        )
        result = md.convert(md_content)

        assert 'title="myfile.py"' in result


def test_integration_with_markdown():
    """Test integration with regular markdown content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = Path(tmpdir) / "code.py"
        code_file.write_text("def test():\n    pass")

        md_content = """
# Documentation

Regular text here.

@@@codeinclude "code.py"

More text after.
"""

        md = markdown.Markdown(
            extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
        )
        result = md.convert(md_content)

        assert "<h1>Documentation</h1>" in result
        assert "Regular text" in result
        assert "python" in result
        assert "def test():" in result
        assert "More text after" in result


def test_multiple_base_paths():
    """Test that multiple base paths are searched."""
    with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
        file1 = Path(tmpdir1) / "first.py"
        file1.write_text("# first")

        file2 = Path(tmpdir2) / "second.py"
        file2.write_text("# second")

        md_content = """
@@@codeinclude "first.py"

@@@codeinclude "second.py"
"""

        md = markdown.Markdown(
            extensions=[
                "fenced_code",
                makeCodeIncludeExtension(base_path=[tmpdir1, tmpdir2]),
            ]
        )
        result = md.convert(md_content)

        # Check that files were found and content is present
        assert "first" in result
        assert "second" in result
        assert "first.py" in result
        assert "second.py" in result


def test_empty_file():
    """Test handling of empty files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        empty_file = Path(tmpdir) / "empty.py"
        empty_file.write_text("")

        md_content = '@@@codeinclude "empty.py"'
        md = markdown.Markdown(
            extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
        )
        result = md.convert(md_content)

        assert "python" in result
        assert "empty.py" in result


def test_fallback_to_text_language():
    """Test that unknown extensions fall back to 'text' language."""
    with tempfile.TemporaryDirectory() as tmpdir:
        unknown_file = Path(tmpdir) / "file.unknown"
        unknown_file.write_text("some content")

        md_content = '@@@codeinclude "file.unknown"'
        md = markdown.Markdown(
            extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
        )
        result = md.convert(md_content)

        assert "text" in result
        assert "file.unknown" in result


def test_url_support():
    """Test that UPath handles URLs (if accessible)."""
    # This test just verifies the syntax doesn't break with URL-like paths
    # Actual URL fetching depends on network/file availability
    md_content = '@@@codeinclude "https://example.com/file.py"'
    md = markdown.Markdown(extensions=["fenced_code", makeCodeIncludeExtension(check_paths=False)])

    try:
        result = md.convert(md_content)
        # Should not raise
        assert isinstance(result, str)
    except ImportError:
        # UPath HTTP support requires aiohttp/requests which may not be installed
        pytest.skip("HTTP support dependencies not available")


def test_absolute_path():
    """Test that absolute paths work."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "absolute.py"
        test_file.write_text("# absolute path")
        abs_path = str(test_file.resolve())

        md_content = f'@@@codeinclude "{abs_path}"'
        md = markdown.Markdown(extensions=["fenced_code", makeCodeIncludeExtension()])
        result = md.convert(md_content)

        assert "python" in result
        assert "absolute.py" in result
        assert "absolute path" in result
