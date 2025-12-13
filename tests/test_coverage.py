"""Tests for ldf.coverage module."""

import json
import pytest
from pathlib import Path

from ldf.coverage import (
    report_coverage,
    _find_coverage_data,
    _try_generate_coverage,
    _normalize_coverage_data,
    _filter_by_service,
)


class TestFindCoverageData:
    """Tests for _find_coverage_data function."""

    def test_finds_coverage_json(self, temp_project: Path, sample_pytest_coverage_json: dict, monkeypatch):
        """Test finding coverage.json in project root."""
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(sample_pytest_coverage_json))
        monkeypatch.chdir(temp_project)

        result = _find_coverage_data(temp_project)

        assert result is not None
        assert result["format"] == "pytest-cov"
        assert result["totals"]["percent"] == 85.0

    def test_finds_ldf_coverage_json(self, temp_project: Path, sample_pytest_coverage_json: dict, monkeypatch):
        """Test finding .ldf/coverage.json."""
        coverage_file = temp_project / ".ldf" / "coverage.json"
        coverage_file.write_text(json.dumps(sample_pytest_coverage_json))
        monkeypatch.chdir(temp_project)

        result = _find_coverage_data(temp_project)

        assert result is not None
        assert result["format"] == "pytest-cov"

    def test_finds_jest_coverage(self, temp_project: Path, sample_jest_coverage_json: dict, monkeypatch):
        """Test finding Jest coverage-summary.json."""
        coverage_dir = temp_project / "coverage"
        coverage_dir.mkdir()
        coverage_file = coverage_dir / "coverage-summary.json"
        coverage_file.write_text(json.dumps(sample_jest_coverage_json))
        monkeypatch.chdir(temp_project)

        result = _find_coverage_data(temp_project)

        assert result is not None
        assert result["format"] == "jest"

    def test_returns_none_when_no_coverage(self, temp_project: Path, monkeypatch):
        """Test returning None when no coverage files exist."""
        monkeypatch.chdir(temp_project)

        result = _find_coverage_data(temp_project)

        assert result is None

    def test_skips_invalid_json(self, temp_project: Path, monkeypatch):
        """Test skipping files with invalid JSON."""
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text("not valid json {{{")
        monkeypatch.chdir(temp_project)

        result = _find_coverage_data(temp_project)

        assert result is None


class TestTryGenerateCoverage:
    """Tests for _try_generate_coverage function."""

    def test_returns_none_without_coverage_file(self, temp_project: Path, monkeypatch):
        """Test returning None when .coverage file doesn't exist."""
        monkeypatch.chdir(temp_project)

        result = _try_generate_coverage(temp_project)

        assert result is None

    def test_returns_none_without_env_var(self, temp_project: Path, monkeypatch):
        """Test returning None when LDF_COVERAGE_WRITE is not set."""
        # Create .coverage file
        (temp_project / ".coverage").touch()
        monkeypatch.chdir(temp_project)
        monkeypatch.delenv("LDF_COVERAGE_WRITE", raising=False)

        result = _try_generate_coverage(temp_project)

        assert result is None


class TestNormalizeCoverageData:
    """Tests for _normalize_coverage_data function."""

    def test_normalizes_pytest_cov_format(self, sample_pytest_coverage_json: dict, tmp_path: Path):
        """Test normalizing pytest-cov format."""
        result = _normalize_coverage_data(sample_pytest_coverage_json, tmp_path / "coverage.json")

        assert result["format"] == "pytest-cov"
        assert result["totals"]["lines_covered"] == 850
        assert result["totals"]["lines_total"] == 1000
        assert result["totals"]["percent"] == 85.0
        assert "files" in result

    def test_normalizes_jest_format(self, sample_jest_coverage_json: dict, tmp_path: Path):
        """Test normalizing Jest format."""
        result = _normalize_coverage_data(sample_jest_coverage_json, tmp_path / "coverage-summary.json")

        assert result["format"] == "jest"
        assert result["totals"]["lines_covered"] == 400
        assert result["totals"]["lines_total"] == 500
        assert result["totals"]["percent"] == 80.0

    def test_handles_unknown_format(self, tmp_path: Path):
        """Test handling unknown coverage format."""
        unknown_data = {"some": "data", "other": "fields"}
        result = _normalize_coverage_data(unknown_data, tmp_path / "unknown.json")

        assert result["format"] == "unknown"
        assert result["totals"]["percent"] == 0


class TestFilterByService:
    """Tests for _filter_by_service function."""

    def test_filters_files_by_service_name(self, sample_pytest_coverage_json: dict, tmp_path: Path):
        """Test filtering coverage to specific service."""
        coverage_data = _normalize_coverage_data(sample_pytest_coverage_json, tmp_path / "coverage.json")

        result = _filter_by_service(coverage_data, "auth")

        assert len(result["files"]) == 1
        assert "auth" in list(result["files"].keys())[0]

    def test_recalculates_totals(self, sample_pytest_coverage_json: dict, tmp_path: Path):
        """Test that totals are recalculated after filtering."""
        coverage_data = _normalize_coverage_data(sample_pytest_coverage_json, tmp_path / "coverage.json")

        result = _filter_by_service(coverage_data, "billing")

        # billing.py has 70% coverage
        assert result["totals"]["percent"] == 70.0

    def test_handles_no_matching_files(self, sample_pytest_coverage_json: dict, tmp_path: Path):
        """Test handling when no files match service."""
        coverage_data = _normalize_coverage_data(sample_pytest_coverage_json, tmp_path / "coverage.json")

        result = _filter_by_service(coverage_data, "nonexistent")

        assert len(result["files"]) == 0
        assert result["totals"]["percent"] == 0


class TestReportCoverage:
    """Tests for report_coverage function."""

    def test_fails_without_ldf_directory(self, tmp_path: Path, monkeypatch):
        """Test error when .ldf directory doesn't exist."""
        monkeypatch.chdir(tmp_path)

        result = report_coverage()

        assert result.get("error") == "LDF not initialized"

    def test_reports_coverage_from_json(
        self, temp_project: Path, sample_pytest_coverage_json: dict, monkeypatch
    ):
        """Test reporting coverage from coverage.json."""
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(sample_pytest_coverage_json))
        monkeypatch.chdir(temp_project)

        result = report_coverage(project_root=temp_project)

        assert "coverage_percent" in result
        assert result["coverage_percent"] == 85.0
        assert result["status"] == "PASS"  # 85% >= 80% threshold

    def test_uses_config_thresholds(
        self, temp_project: Path, sample_pytest_coverage_json: dict, monkeypatch
    ):
        """Test that configured thresholds are used."""
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(sample_pytest_coverage_json))
        monkeypatch.chdir(temp_project)

        result = report_coverage(project_root=temp_project)

        assert result["threshold_default"] == 80
        assert result["threshold_critical"] == 90

    def test_handles_no_coverage_data(self, temp_project: Path, monkeypatch):
        """Test handling when no coverage data exists."""
        monkeypatch.chdir(temp_project)

        result = report_coverage(project_root=temp_project)

        assert result.get("error") == "No coverage data"

    def test_handles_config_not_found(self, tmp_path: Path, monkeypatch, capsys):
        """Test handling when config file is missing."""
        # Create .ldf directory but no config.yaml
        ldf_dir = tmp_path / ".ldf"
        ldf_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        result = report_coverage(project_root=tmp_path)

        assert result.get("error") == "Config not found"

    def test_filters_by_service(self, temp_project: Path, sample_pytest_coverage_json: dict, monkeypatch, capsys):
        """Test filtering coverage by service."""
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(sample_pytest_coverage_json))
        monkeypatch.chdir(temp_project)

        result = report_coverage(project_root=temp_project, service="auth")

        captured = capsys.readouterr()
        assert "Filtered to service: auth" in captured.out


class TestTryGenerateCoverageAdvanced:
    """Advanced tests for _try_generate_coverage function."""

    def test_returns_none_without_coverage_tool(self, temp_project: Path, monkeypatch):
        """Test returning None when coverage tool is not installed."""
        (temp_project / ".coverage").touch()
        monkeypatch.setenv("LDF_COVERAGE_WRITE", "1")
        # Mock shutil.which to return None (tool not found)
        monkeypatch.setattr("shutil.which", lambda x: None)
        monkeypatch.chdir(temp_project)

        result = _try_generate_coverage(temp_project)

        assert result is None

    def test_returns_none_without_ldf_dir(self, tmp_path: Path, monkeypatch):
        """Test returning None when .ldf directory doesn't exist."""
        (tmp_path / ".coverage").touch()
        monkeypatch.setenv("LDF_COVERAGE_WRITE", "1")
        monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/coverage")
        monkeypatch.chdir(tmp_path)

        result = _try_generate_coverage(tmp_path)

        assert result is None


class TestFilterByServiceAdvanced:
    """Advanced tests for _filter_by_service function."""

    def test_handles_no_files_key(self):
        """Test handling coverage data without files key."""
        coverage_data = {
            "format": "unknown",
            "totals": {"percent": 50}
        }

        result = _filter_by_service(coverage_data, "auth")

        assert result == coverage_data  # Returns unchanged

    def test_handles_jest_format_lines(self):
        """Test handling Jest format with lines data."""
        coverage_data = {
            "format": "jest",
            "totals": {"percent": 80},
            "files": {
                "/src/auth.ts": {"lines": {"covered": 80, "total": 100}},
                "/src/billing.ts": {"lines": {"covered": 50, "total": 100}},
            }
        }

        result = _filter_by_service(coverage_data, "auth")

        assert result["totals"]["lines_covered"] == 80
        assert result["totals"]["lines_total"] == 100
        assert result["totals"]["percent"] == 80.0


class TestGenerateReportAdvanced:
    """Advanced tests for report generation."""

    def test_report_with_jest_file_format(self, temp_project: Path, monkeypatch):
        """Test report with Jest coverage format files."""
        coverage_data = {
            "total": {"lines": {"covered": 400, "total": 500, "pct": 80.0}},
            "/src/auth.ts": {"lines": {"total": 100, "covered": 95, "pct": 95.0}},
            "/src/utils.ts": {"lines": {"total": 100, "covered": 50, "pct": 50.0}},
        }
        coverage_file = temp_project / "coverage" / "coverage-summary.json"
        coverage_file.parent.mkdir()
        coverage_file.write_text(json.dumps(coverage_data))
        monkeypatch.chdir(temp_project)

        result = report_coverage(project_root=temp_project)

        assert result["coverage_percent"] == 80.0

    def test_report_with_many_files(self, temp_project: Path, monkeypatch, capsys):
        """Test report with more than 10 files shows truncation message."""
        # Create coverage data with many files
        coverage_data = {
            "totals": {
                "covered_lines": 800,
                "num_statements": 1000,
                "percent_covered": 80.0
            },
            "files": {
                f"src/module{i}.py": {
                    "summary": {
                        "covered_lines": 70,
                        "num_statements": 100,
                        "percent_covered": 70.0
                    }
                }
                for i in range(15)
            }
        }
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        monkeypatch.chdir(temp_project)

        result = report_coverage(project_root=temp_project)

        captured = capsys.readouterr()
        assert "more files" in captured.out

    def test_report_fail_status(self, temp_project: Path, monkeypatch, capsys):
        """Test report with failing coverage."""
        coverage_data = {
            "totals": {
                "covered_lines": 500,
                "num_statements": 1000,
                "percent_covered": 50.0  # Below 80% threshold
            },
            "files": {}
        }
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        monkeypatch.chdir(temp_project)

        result = report_coverage(project_root=temp_project)

        assert result["status"] == "FAIL"
        captured = capsys.readouterr()
        assert "NOT SATISFIED" in captured.out
        assert "more coverage" in captured.out
