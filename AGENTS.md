# AGENTS.md

This document provides essential information for agents working on the ansible-collection-inventory-sacloud repository.

## Project Overview

This is an Ansible Collection that provides a dynamic inventory plugin for Sakura Cloud (Sacloud). The collection allows Ansible to automatically discover and inventory Sakura Cloud resources.

### Structure
```
/
├── README.md                 # Project documentation (in Japanese)
├── LICENSE                   # MIT License file
├── galaxy.yml               # Ansible Galaxy collection metadata
├── Makefile                 # Build, test, and development commands
├── AGENTS.md                # This file
├── pyproject.toml           # Python project configuration (ruff, Python 3.13+)
├── .github/
│   ├── workflows/
│   │   ├── ci.yml          # GitHub Actions CI (lint tests)
│   │   └── release.yml     # Manual release workflow (workflow_dispatch)
└── plugins/
    └── inventory/
        └── sacloud.py       # Main inventory plugin implementation
└── tests/
    ├── conftest.py          # pytest fixtures for testing
    ├── test_inventory.py    # pytest-based test suite
    ├── mock_server.py       # Mock HTTP server for API simulation
    ├── test_inventory_basic_sacloud.yml      # Basic test config
    ├── test_inventory_constructed_sacloud.yml # Constructed features test
    ├── test_inventory_empty_sacloud.yml      # Single zone test
    └── data/
        └── mock_api_response.json            # Test data
```

## Essential Commands

### Build and Package
```bash
make build
# or
ansible-galaxy collection build
```
Builds the collection into a tarball for distribution.

### Testing
```bash
make test          # Run pytest-based test suite
make test-verbose  # Run tests with detailed output
```

### Code Quality
```bash
make lint          # Run ruff checks
make format        # Auto-format code with ruff
```

### Local Development Installation
```bash
make build
ansible-galaxy collection install -p ~/.ansible/collections/ --force tokuhirom-sacloud-*.tar.gz
```

## Code Patterns and Conventions

### Ansible Plugin Structure
- The plugin inherits from `BaseInventoryPlugin` and `Constructable`
- Uses Ansible's plugin documentation format with `DOCUMENTATION` and `EXAMPLES` constants
- Follows Ansible naming conventions: `InventoryModule` class with `NAME = 'sacloud'`
- File names MUST end with `sacloud.yml` or `sacloud.yaml` for `verify_file()` recognition

### API Integration
- Uses `ansible.module_utils.urls.open_url` for HTTP requests
- Implements Sakura Cloud API authentication with username/password (token/secret)
- API endpoint pattern: `{api_root}/{zone}/api/cloud/1.1/server`
- Handles pagination with `{From:0,To:0}` parameter

### Inventory Processing
1. Verify file with `verify_file()` - only accepts files ending in `sacloud.yml` or `sacloud.yaml`
2. Parse configuration and fetch server data for each zone
3. Create inventory hosts from server names
4. Set host variables for IP addresses
5. Create groups based on server tags (excluding tags in `skip_group_tags`)
6. Apply constructed features (compose, groups, keyed_groups)

### Host Variables Set
- `ip_address`: Array of interface IP addresses
- `user_ip_address`: Array of user IP addresses
- Additional variables from constructed features

## Configuration

### Required Parameters
- `access_token`: Sakura Cloud API access token
- `access_token_secret`: Sakura Cloud API access token secret`
- `zones`: List of zones to query (e.g., ["tk1b", "is1a"])

### Optional Parameters
- `url`: API base URL (default: "https://secure.sakura.ad.jp/cloud/zone")
- `skip_group_tags`: Tags to skip when creating groups (default: ["@auto-reboot", "__with_sacloud_inventory"])
- Constructed features: `compose`, `groups`, `keyed_groups`

### Environment Variables
- `SAKURA_API_ROOT_URL`: Alternative way to set API base URL
- `SAKURA_ACCESS_TOKEN`: Alternative way to set access token
- `SAKURA_ACCESS_TOKEN_SECRET`: Alternative way to set access token secret

## Collection Metadata

The collection is defined in `galaxy.yml`:
- Namespace: `tokuhirom`
- Name: `sacloud`
- Version: `1.0.0`
- License: MIT
- Tags: inventory, sacloud, dynamic

## Development

### Tools and Dependencies
- **Python 3.13+** (required)
- **uv** - Python package manager (preferred)
- **pytest** - Test framework
- **ruff** - Linting and formatting
- **Ansible 2.9+** - Runtime requirement

### Testing Strategy
- **pytest-based** test suite with fixtures
- **Mock HTTP server** simulates Sakura Cloud API
- **Dynamic port allocation** prevents conflicts
- **Environment variable support** for flexible configuration in tests

### Test Structure
- `conftest.py`: pytest fixtures (`mock_server`, `run_inventory`)
- `test_inventory.py`: Main test suite (6 tests covering basic, constructed, and edge cases)
- `mock_server.py`: HTTP server that serves mock API responses
- Test configurations use environment variables (`SAKURA_API_ROOT_URL`)

### Code Quality standards
- **ruff** for linting and formatting
- **MIT license** - all code must be MIT compatible
- **Standard Ansible patterns** for plugin development

### Release Process
- **Manual workflow dispatch** - Releases are triggered manually via GitHub Actions
- **Semantic versioning** with `v` prefix (e.g., v0.0.2, v1.0.0)
- **GitHub Actions** for CI/CD
- **Automated release notes** generated from commits

#### How to Release

1. **Navigate to Actions tab** on GitHub
   - Go to: https://github.com/tokuhirom/ansible-collection-inventory-sacloud/actions

2. **Select the Release workflow**
   - Click on "Release" workflow in the left sidebar

3. **Trigger workflow manually**
   - Click "Run workflow" button
   - Enter the version number in semver format with `v` prefix (e.g., `v0.0.2`, `v1.0.0`)
   - Click "Run workflow" to start

4. **The workflow will automatically:**
   - Update the version in `galaxy.yml` (removes `v` prefix)
   - Commit the version change to main branch
   - Create a git tag with the specified version
   - Create a GitHub release with auto-generated release notes
   - Build the collection tarball (`tokuhirom-sacloud-*.tar.gz`)
   - Upload the tarball as a release asset

5. **Verify the release**
   - Check the Releases page: https://github.com/tokuhirom/ansible-collection-inventory-sacloud/releases
   - Confirm the tarball is attached to the release
   - Verify the version in `galaxy.yml` matches (without `v` prefix)

#### Version Format
- Use semantic versioning: `MAJOR.MINOR.PATCH`
- Always include `v` prefix when triggering the workflow: `v1.0.0`
- The `galaxy.yml` file will store the version without `v` prefix: `1.0.0`

## Gotchas and Important Notes

### File Naming
- Inventory configuration files MUST end with `sacloud.yml` or `sacloud.yaml` to be recognized
- Plugin verification is strict about file extensions

### API Authentication
- Uses HTTP basic authentication with token as username and secret as password
- No additional authentication headers or signatures required

### Zone Handling
- Each zone is queried independently via separate API calls
- Zone codes are short identifiers (e.g., "tk1b", "is1a")

### Tag-based Grouping
- All server tags become inventory groups except those in `skip_group_tags`
- Special tags like "@auto-reboot" and "__with_sacloud_inventory" are skipped by default
- Host with tag "web" will be added to group "web"

### Constructed Features
- Plugin supports Ansible's constructed inventory features
- Can compose new variables, create conditional groups, and keyed groups
- Host variables are available for constructed expression evaluation

### Testing Gotchas
- Tests use **dynamic port allocation** (port 0) - don't assume fixed ports
- Tests set/read **environment variables** (`SAKURA_API_ROOT_URL`)
- **Cached test results** may interfere - clear `~/.ansible/collections/` if needed
- **pytest fixtures** handle setup/teardown automatically

### Development Environment
- **uv tool** recommended: `uv tool install pytest ruff`
- **Makefile** provides consistent commands across environments
- **Python 3.13** minimum - enforced by `pyproject.toml`

## CI/CD and Automation

### GitHub Actions
- **ci.yml**: Lint checks and test execution on pull requests
- **release.yml**: Manual release workflow triggered via workflow_dispatch
  - Accepts version input (e.g., `v0.0.2`)
  - Updates `galaxy.yml` version
  - Creates git tag and GitHub release
  - Builds and uploads collection tarball

## Support and Contributing

### Issue Reporting
- Check existing issues before creating new ones
- Include configuration examples when reporting bugs
- Provide test inventory files that reproduce issues

### Contributing
- Follow existing code style (enforced by ruff)
- Add tests for new functionality
- Update documentation (AGENTS.md, README.md)
- Use semantic versioning for changes
