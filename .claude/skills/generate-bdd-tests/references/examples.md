# Complete Test File Examples

## Example 1: CLI Command Tests

Tests a CLI application with commands, options, and file operations.

```python
"""Tests for CLI commands."""

import pytest
from pathlib import Path

from myapp.cli import app
from myapp import __version__


class TestCLIHelp:
    """Test help output."""

    def test_help_shows_all_commands(self, capsys, console):
        """Help should list all available commands."""
        # GIVEN the CLI app
        # WHEN help is requested
        with pytest.raises(SystemExit) as exc_info:
            app(["--help"], console=console)

        # THEN exit code should be 0
        assert exc_info.value.code == 0
        # AND all commands should be listed
        output = capsys.readouterr().out
        assert "configure" in output
        assert "generate" in output
        assert "update" in output

    def test_version_output(self, capsys, console):
        """Version flag should print current version."""
        # GIVEN the CLI app
        # WHEN version is requested
        with pytest.raises(SystemExit) as exc_info:
            app(["--version"], console=console)

        # THEN version should be displayed
        assert exc_info.value.code == 0
        output = capsys.readouterr().out
        assert __version__ in output


class TestGenerateCommand:
    """Test generate command."""

    def test_requires_api_key(self, tmp_path, capsys, console):
        """Generate should fail without API key."""
        # GIVEN a text file exists
        text_file = tmp_path / "test.txt"
        text_file.write_text("Hello world")

        # WHEN generate is called without API key
        with pytest.raises(SystemExit) as exc_info:
            app(["generate", str(text_file), "--id", "test"], console=console)

        # THEN it should fail with error
        assert exc_info.value.code == 1
        output = capsys.readouterr().out
        assert "API_KEY" in output

    def test_processes_single_file(self, tmp_path, monkeypatch, mocker, capsys, console):
        """Generate should process a single text file."""
        # GIVEN a text file and API key
        text_file = tmp_path / "hello.txt"
        text_file.write_text("Hello, this is a test.")
        output_dir = tmp_path / "output"

        monkeypatch.setenv("API_KEY", "test-key")

        # AND API client is mocked
        mock_client = mocker.MagicMock()
        mock_client.convert.return_value = b"fake-data"
        mocker.patch("myapp.common.get_client", return_value=mock_client)

        # WHEN generate is called
        app([
            "generate", str(text_file),
            "--id", "voice-123",
            "--output-dir", str(output_dir),
        ], console=console, result_action="return_value")

        # THEN API should be called correctly
        mock_client.convert.assert_called_once_with(
            text="Hello, this is a test.",
            id="voice-123",
        )
        # AND output file should be created
        assert (output_dir / "hello.out").exists()

    def test_skips_empty_files(self, tmp_path, monkeypatch, mocker, capsys, console):
        """Generate should skip empty text files."""
        # GIVEN an empty file
        text_file = tmp_path / "empty.txt"
        text_file.write_text("")

        monkeypatch.setenv("API_KEY", "test-key")
        mock_client = mocker.MagicMock()
        mocker.patch("myapp.get_client", return_value=mock_client)

        # WHEN generate is called
        app([
            "generate", str(text_file),
            "--id", "voice-123",
        ], console=console, result_action="return_value")

        # THEN API should not be called
        mock_client.convert.assert_not_called()
        # AND skip message should be shown
        output = capsys.readouterr().out
        assert "Skipping" in output


class TestConfigureCommand:
    """Test configure command."""

    def test_saves_api_key(self, temp_config_dir, capsys, console):
        """Configure should save API key to credentials file."""
        # GIVEN the config directory exists
        # WHEN configure is called
        app(["configure", "my-test-key"], console=console, result_action="return_value")

        # THEN credentials file should be created
        creds_file = temp_config_dir / "credentials"
        assert creds_file.exists()
        # AND it should contain the key
        assert "API_KEY=my-test-key" in creds_file.read_text()

    def test_sets_secure_permissions(self, temp_config_dir, console):
        """Credentials file should have restricted permissions."""
        # GIVEN configure is called
        app(["configure", "secret"], console=console, result_action="return_value")

        # THEN file should be owner-only readable
        creds_file = temp_config_dir / "credentials"
        assert (creds_file.stat().st_mode & 0o777) == 0o600
```

## Example 2: Utility Function Tests

Tests pure functions with various input scenarios and edge cases.

```python
"""Tests for validation utilities."""

import pytest

from myapp.validators import (
    validate_email,
    validate_password,
    validate_username,
    validate_form,
)


class TestValidateEmail:
    """Tests for email validation."""

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "name.surname@company.co.uk",
        "user+tag@gmail.com",
    ])
    def test_accepts_valid_emails(self, email):
        """Valid email formats should pass."""
        # GIVEN a valid email format
        # THEN validation should pass
        assert validate_email(email) == {"valid": True}

    @pytest.mark.parametrize("email,expected_error", [
        ("notanemail", "Invalid email format"),
        ("@missing-local.com", "Invalid email format"),
        ("missing@domain", "Invalid email format"),
    ])
    def test_rejects_invalid_formats(self, email, expected_error):
        """Invalid email formats should fail with message."""
        # GIVEN an invalid email
        # THEN validation should fail
        result = validate_email(email)
        assert result["valid"] is False
        assert result["error"] == expected_error

    def test_handles_empty_input(self):
        """Empty string should return required error."""
        # GIVEN empty string
        # THEN should return required error
        result = validate_email("")
        assert result == {"valid": False, "error": "Email is required"}


class TestValidatePassword:
    """Tests for password validation."""

    def test_accepts_strong_password(self):
        """Password meeting all requirements should pass."""
        # GIVEN a strong password
        # THEN validation should pass
        assert validate_password("SecureP@ss123") == {"valid": True}

    def test_rejects_without_uppercase(self):
        """Password without uppercase should fail."""
        # GIVEN password without uppercase
        # THEN should require uppercase letter
        result = validate_password("lowercase123!")
        assert result["valid"] is False
        assert "uppercase" in result["error"].lower()

    def test_rejects_short_password(self):
        """Password shorter than minimum should fail."""
        # GIVEN short password
        # THEN should require minimum length
        result = validate_password("Ab1!")
        assert result["valid"] is False
        assert "8 characters" in result["error"]

    def test_rejects_without_special_char(self):
        """Password without special character should fail."""
        # GIVEN password without special char
        # THEN should require special character
        result = validate_password("SecurePass123")
        assert result["valid"] is False
        assert "special" in result["error"].lower()


class TestValidateForm:
    """Tests for full form validation."""

    def test_returns_all_errors_when_invalid(self):
        """Multiple invalid fields should return all errors."""
        # GIVEN form with multiple invalid fields
        form = {
            "email": "invalid",
            "password": "weak",
            "username": "a",
        }

        # WHEN validating entire form
        result = validate_form(form)

        # THEN should return errors for each field
        assert result["valid"] is False
        assert "email" in result["errors"]
        assert "password" in result["errors"]
        assert "username" in result["errors"]

    def test_returns_valid_when_all_pass(self):
        """All valid fields should return valid."""
        # GIVEN form with all valid fields
        form = {
            "email": "user@example.com",
            "password": "SecureP@ss123",
            "username": "validuser",
        }

        # WHEN validating entire form
        result = validate_form(form)

        # THEN should be valid with no errors
        assert result["valid"] is True
        assert result["errors"] == {}
```

## Example 3: Async/API Function Tests

Tests functions with external API calls and error handling.

```python
"""Tests for API service functions."""

import pytest

from myapp.services import fetch_products, create_order


class TestFetchProducts:
    """Tests for product fetching."""

    def test_returns_products_on_success(self, mocker):
        """Successful API call should return products."""
        # GIVEN API returns products
        mock_products = [
            {"id": "1", "name": "Laptop", "price": 999},
            {"id": "2", "name": "Mouse", "price": 29},
        ]
        mock_get = mocker.patch("myapp.services.http_get")
        mock_get.return_value = {"data": mock_products}

        # WHEN fetching products
        result = fetch_products()

        # THEN products should be returned
        assert result == mock_products
        mock_get.assert_called_once_with("/api/products")

    def test_returns_empty_on_404(self, mocker):
        """404 response should return empty list."""
        # GIVEN API returns 404
        mock_get = mocker.patch("myapp.services.http_get")
        mock_get.side_effect = NotFoundError("Products not found")

        # WHEN fetching products
        result = fetch_products()

        # THEN empty list should be returned
        assert result == []

    def test_raises_on_server_error(self, mocker):
        """Server error should raise exception."""
        # GIVEN API returns 500
        mock_get = mocker.patch("myapp.services.http_get")
        mock_get.side_effect = ServerError("Internal error")

        # WHEN fetching products
        # THEN exception should propagate
        with pytest.raises(ServerError):
            fetch_products()

    def test_filters_by_category(self, mocker):
        """Category filter should be passed to API."""
        # GIVEN API is available
        mock_get = mocker.patch("myapp.services.http_get")
        mock_get.return_value = {"data": []}

        # WHEN fetching with category filter
        fetch_products(category="electronics")

        # THEN filter should be in request
        mock_get.assert_called_once_with(
            "/api/products",
            params={"category": "electronics"}
        )


class TestCreateOrder:
    """Tests for order creation."""

    def test_creates_order_successfully(self, mocker):
        """Valid order should be created."""
        # GIVEN valid order data
        order_data = {"items": [{"id": "1", "qty": 2}], "total": 100}
        mock_post = mocker.patch("myapp.services.http_post")
        mock_post.return_value = {"order_id": "ord_123", "status": "created"}

        # WHEN creating order
        result = create_order(order_data)

        # THEN order should be created
        assert result["order_id"] == "ord_123"
        mock_post.assert_called_once_with("/api/orders", json=order_data)

    def test_validates_empty_items(self):
        """Empty items should raise validation error."""
        # GIVEN order with no items
        order_data = {"items": [], "total": 0}

        # WHEN creating order
        # THEN validation error should be raised
        with pytest.raises(ValueError, match="at least one item"):
            create_order(order_data)
```

## Example 4: Configuration Constants Tests

Tests exported constants for correctness.

```python
"""Tests for application constants."""

import pytest

from myapp.constants import (
    API_CONFIG,
    ROUTE_PATHS,
    BREAKPOINTS,
    DEFAULT_PAGINATION,
)


class TestAPIConfig:
    """Tests for API configuration."""

    def test_has_required_properties(self):
        """Config should have all required properties."""
        # GIVEN API config
        # THEN required properties should exist
        assert hasattr(API_CONFIG, "BASE_URL")
        assert hasattr(API_CONFIG, "TIMEOUT")
        assert hasattr(API_CONFIG, "RETRY_ATTEMPTS")

    def test_base_url_is_https(self):
        """Base URL should use HTTPS."""
        # GIVEN the API config
        # THEN base URL should be secure
        assert API_CONFIG.BASE_URL.startswith("https://")

    def test_timeout_is_reasonable(self):
        """Timeout should be between 5-30 seconds."""
        # GIVEN timeout configuration
        # THEN should be in reasonable range
        assert 5000 <= API_CONFIG.TIMEOUT <= 30000


class TestRoutePaths:
    """Tests for route path constants."""

    def test_defines_main_routes(self):
        """All main routes should be defined."""
        # GIVEN route paths
        # THEN main routes should exist
        assert ROUTE_PATHS.HOME == "/"
        assert ROUTE_PATHS.LOGIN == "/login"
        assert ROUTE_PATHS.DASHBOARD == "/dashboard"

    def test_routes_are_absolute(self):
        """All routes should start with forward slash."""
        # GIVEN all route paths
        # THEN each should be absolute
        for name in dir(ROUTE_PATHS):
            if not name.startswith("_"):
                path = getattr(ROUTE_PATHS, name)
                assert path.startswith("/"), f"{name} should start with /"


class TestBreakpoints:
    """Tests for responsive breakpoints."""

    def test_ascending_order(self):
        """Breakpoints should increase progressively."""
        # GIVEN breakpoint values
        # THEN they should be in ascending order
        assert BREAKPOINTS.SM < BREAKPOINTS.MD
        assert BREAKPOINTS.MD < BREAKPOINTS.LG
        assert BREAKPOINTS.LG < BREAKPOINTS.XL

    def test_values_are_positive_numbers(self):
        """All breakpoints should be positive numbers."""
        # GIVEN all breakpoints
        # THEN each should be a positive number
        for name in ["SM", "MD", "LG", "XL"]:
            value = getattr(BREAKPOINTS, name)
            assert isinstance(value, int)
            assert value > 0


class TestDefaultPagination:
    """Tests for pagination defaults."""

    def test_has_sensible_defaults(self):
        """Pagination should have sensible default values."""
        # GIVEN pagination config
        # THEN defaults should be reasonable
        assert DEFAULT_PAGINATION.PAGE == 1
        assert DEFAULT_PAGINATION.PAGE_SIZE == 20
        assert DEFAULT_PAGINATION.MAX_PAGE_SIZE == 100

    def test_page_size_within_max(self):
        """Default page size should not exceed max."""
        # GIVEN pagination limits
        # THEN default should not exceed max
        assert DEFAULT_PAGINATION.PAGE_SIZE <= DEFAULT_PAGINATION.MAX_PAGE_SIZE
```
