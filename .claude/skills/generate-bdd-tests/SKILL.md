---
name: generate-bdd-tests
description: Generates comprehensive BDD-style test files using pytest and pytest-mock. Use when creating tests, writing test files, generating test coverage, or when asked to test CLI commands, functions, utilities, or modules.
---

# BDD Test File Generator

Generate behavior-driven test files that focus on public API and observable behavior.

## Quick Start Workflow

1. **Read the source file** to understand what needs to be tested
2. **Identify the public API** - all exported functions, classes, CLI commands
3. **Check for existing test setup** - look for `conftest.py`, `pyproject.toml`, or existing test files
4. **Generate the test file** using patterns from `references/patterns.md`

## Core Principle

Test public API and observable behavior only, never internal implementation:

- **CLI Commands**: Test user inputs, outputs, exit codes
- **Functions/Utilities**: Test inputs → outputs, not internal algorithm steps
- **Classes**: Test public methods and properties

## Test Description Style

Use BDD-style descriptions with flexible GIVEN/WHEN/THEN/AND comments:

```python
def test_user_redirect_when_unauthenticated():
    # GIVEN an unauthenticated user
    # WHEN the protected route is accessed
    # THEN the user should be redirected
    ...

def test_profile_displays_user_info():
    # GIVEN a user is authenticated
    # WHEN the profile page loads
    # THEN the username should be displayed
    # AND the avatar should be visible
    ...

def test_empty_array_length():
    # GIVEN an empty array
    # THEN length should be zero
    ...

def test_admin_access_granted():
    # GIVEN a valid token
    # AND the user has admin role
    # WHEN accessing admin panel
    # THEN access should be granted
    ...
```

## Coverage Requirements

- Primary success paths (happy path)
- Edge cases (empty strings, None, boundaries)
- Error states (graceful error handling)
- All exported items

## References

- `references/patterns.md` - Detailed test patterns and mock handling
- `references/examples.md` - Complete example test files
