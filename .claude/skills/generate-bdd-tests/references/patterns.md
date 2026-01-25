# BDD Test Patterns for Python

## Test File Structure

```python
"""Tests for feature_name module."""

import pytest
from unittest.mock import MagicMock, patch

from module_under_test import function_to_test


class TestFeatureName:
    """Test suite for FeatureName."""

    @pytest.fixture
    def mock_dependency(self, mocker):
        """Mock external dependency."""
        return mocker.patch("module_under_test.dependency")

    def test_observable_behavior(self):
        # Use flexible GIVEN/WHEN/THEN/AND combinations
        ...
```

## BDD Comment Combinations

Use the combination that best fits the test:

```python
def test_add_item_to_cart():
    # GIVEN an empty shopping cart
    # WHEN a product is added
    # THEN the cart should contain one item
    ...

def test_wallet_starts_with_zero_balance():
    # GIVEN a new wallet instance
    # THEN balance should be zero
    ...

def test_order_summary_after_checkout():
    # GIVEN a cart with items
    # WHEN checkout is completed
    # THEN order confirmation should appear
    # AND cart should be emptied
    ...

def test_premium_member_discount():
    # GIVEN a cart total over $100
    # AND the user is a premium member
    # WHEN calculating final price
    # THEN 15% discount should be applied
    ...

def test_draft_saved_after_editing():
    # GIVEN an existing document
    # WHEN the user modifies content
    # AND triggers auto-save
    # THEN draft should be persisted
    ...
```

## Mock Handling with pytest-mock

### Basic Mocking

```python
def test_with_mock(mocker):
    # Mock a module function
    mock_fetch = mocker.patch("myapp.services.fetch_user")
    mock_fetch.return_value = {"id": "123", "name": "Alice"}

    result = get_user_profile("123")

    mock_fetch.assert_called_once_with("123")
    assert result["name"] == "Alice"
```

### Mock as Fixture

```python
@pytest.fixture
def mock_api_client(mocker):
    """Mock the API client."""
    mock = mocker.patch("myapp.client.APIClient")
    mock.return_value.fetch.return_value = {"status": "ok"}
    return mock


def test_api_call(mock_api_client):
    # GIVEN a mocked API client
    # WHEN making a request
    result = make_request()

    # THEN the client should be called
    mock_api_client.return_value.fetch.assert_called_once()
```

### Different Return Values

```python
def test_success_scenario(mocker):
    # Success scenario
    mock_fetch = mocker.patch("myapp.fetch_user")
    mock_fetch.return_value = {
        "id": "usr_123",
        "name": "Alice",
        "email": "alice@example.com",
    }

def test_error_scenario(mocker):
    # Error scenario
    mock_fetch = mocker.patch("myapp.fetch_user")
    mock_fetch.side_effect = ConnectionError("Network timeout")

def test_conditional_behavior(mocker):
    # Conditional behavior
    def fetch_impl(user_id):
        if user_id == "invalid":
            raise ValueError("Not found")
        return {"id": user_id, "name": "User"}

    mock_fetch = mocker.patch("myapp.fetch_user", side_effect=fetch_impl)
```

## CLI Testing Patterns (cyclopts)

### Basic CLI Test

```python
import pytest
from myapp.cli import app


def test_help_shows_commands(capsys, console):
    # GIVEN the CLI app
    # WHEN help is requested
    with pytest.raises(SystemExit) as exc_info:
        app(["--help"], console=console)

    # THEN exit code should be 0
    assert exc_info.value.code == 0
    # AND commands should be listed
    output = capsys.readouterr().out
    assert "generate" in output
```

### Testing CLI with Mocked Dependencies

```python
def test_command_calls_api(mocker, tmp_path, monkeypatch):
    # GIVEN API key is set
    monkeypatch.setenv("API_KEY", "test-key")

    # AND API client is mocked
    mock_client = mocker.MagicMock()
    mock_client.process.return_value = b"result"
    mocker.patch("myapp.common.get_client", return_value=mock_client)

    # WHEN command is executed
    input_file = tmp_path / "input.txt"
    input_file.write_text("test content")

    app(["process", str(input_file)], result_action="return_value")

    # THEN API should be called
    mock_client.process.assert_called_once()
```

### Testing File Operations

```python
def test_output_file_created(tmp_path, mocker, monkeypatch):
    # GIVEN input file exists
    input_file = tmp_path / "input.txt"
    input_file.write_text("Hello world")
    output_dir = tmp_path / "output"

    monkeypatch.setenv("API_KEY", "test-key")
    mock_client = mocker.MagicMock()
    mock_client.convert.return_value = b"converted-data"
    mocker.patch("myapp.get_client", return_value=mock_client)

    # WHEN command runs
    app([
        "convert",
        str(input_file),
        "--output-dir", str(output_dir),
    ], result_action="return_value")

    # THEN output file should exist
    assert (output_dir / "input.out").exists()
    assert (output_dir / "input.out").read_bytes() == b"converted-data"
```

## Utility Function Patterns

```python
class TestFormatCurrency:
    """Tests for format_currency function."""

    def test_formats_number_with_symbol(self):
        # GIVEN a numeric amount
        # WHEN format_currency is called
        # THEN it should return formatted string
        assert format_currency(1234.5) == "$1,234.50"

    def test_handles_zero(self):
        # GIVEN zero
        # THEN it should display as currency
        assert format_currency(0) == "$0.00"

    def test_handles_negative(self):
        # GIVEN a negative number
        # THEN it should preserve the negative sign
        assert format_currency(-50) == "-$50.00"

    @pytest.mark.parametrize("amount,expected", [
        (100, "$100.00"),
        (1000.5, "$1,000.50"),
        (0.01, "$0.01"),
    ])
    def test_various_amounts(self, amount, expected):
        # GIVEN various amounts
        # THEN each should format correctly
        assert format_currency(amount) == expected
```

## Constants Testing

```python
class TestFeatureFlags:
    """Tests for feature flag constants."""

    def test_has_required_flags(self):
        # GIVEN feature flags
        # THEN all required flags should exist
        assert hasattr(FEATURE_FLAGS, "DARK_MODE")
        assert hasattr(FEATURE_FLAGS, "BETA_FEATURES")
        assert hasattr(FEATURE_FLAGS, "ANALYTICS")

    def test_values_are_boolean(self):
        # GIVEN all flag values
        # THEN each should be boolean
        for key, value in vars(FEATURE_FLAGS).items():
            if not key.startswith("_"):
                assert isinstance(value, bool), f"{key} should be bool"
```

## Fixtures in conftest.py

```python
# tests/conftest.py
import pytest
from rich.console import Console


@pytest.fixture
def console():
    """Console with fixed width for consistent output."""
    return Console(width=80, force_terminal=True, color_system=None)


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Override config directory to temp path."""
    config_dir = tmp_path / ".config" / "myapp"
    config_dir.mkdir(parents=True)
    monkeypatch.setattr("myapp.common.CONFIG_DIR", config_dir)
    return config_dir


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Ensure sensitive env vars are not set."""
    monkeypatch.delenv("API_KEY", raising=False)
```

## BDD Description Guidelines

**Good descriptions** - behavior-focused:

- `test_adds_item_to_cart_when_button_clicked`
- `test_displays_error_for_invalid_email`
- `test_persists_selection_after_refresh`
- `test_disables_submit_while_loading`

**Avoid** - implementation-focused:

- `test_add_to_cart_function` (not descriptive)
- `test_calls_internal_method` (testing internals)
- `test_works_correctly` (too vague)
- `test_sets_internal_flag` (exposes internals)
