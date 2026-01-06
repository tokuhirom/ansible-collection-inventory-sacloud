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
├── .tagpr                   # tagpr configuration file
├── .github/
│   ├── workflows/
│   │   ├── ci.yml          # GitHub Actions CI (lint tests)
│   │   ├── release.yml     # Release workflow (triggers on tag push)
│   │   └── tagpr.yml       # tagpr workflow (creates release PRs)
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
- **tagpr** - Automated release PR creation and version management
- **GitHub Actions** for CI/CD
- **Semantic versioning** with `v` prefix
- **Automated changelogs** from commit messages

#### How to Release with tagpr

1. **Update version in galaxy.yml**
   ```bash
   # Edit galaxy.yml and bump the version
   # Example: version: "0.0.5" → version: "0.0.6"
   ```

2. **Commit and push to main**
   ```bash
   git add galaxy.yml
   git commit -m "Bump version to 0.0.6"
   git push origin main
   ```

3. **tagpr automatically creates a release PR**
   - The tagpr workflow detects the version change
   - Creates a PR titled "Release v0.0.6" (or similar)
   - Generates changelog from commit messages
   - PR includes all changes since last release

4. **Review and merge the release PR**
   - Review the changelog and changes
   - Merge the PR (can use auto-merge if configured)

5. **Tag and release are created automatically**
   - When the PR is merged, tagpr automatically:
     - Creates a git tag (e.g., `v0.0.6`)
     - The tag push triggers the release workflow
     - Release workflow builds the collection tarball
     - Uploads the tarball to GitHub Releases

#### Version Management
- Version is tracked in `galaxy.yml`
- Use semantic versioning: `MAJOR.MINOR.PATCH`
- Version in galaxy.yml should NOT have `v` prefix (e.g., `"0.0.6"`)
- Git tags will have `v` prefix (e.g., `v0.0.6`)

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
- **tagpr.yml**: Monitors version changes and creates release PRs
  - Triggers on push to main branch
  - Detects version bump in galaxy.yml
  - Creates release PR with changelog
  - Creates git tag when PR is merged
- **release.yml**: Builds and publishes releases
  - Triggers on tag push (from tagpr)
  - Builds collection tarball with `make build`
  - Uploads tarball to GitHub Releases
  - Generates release notes automatically

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
