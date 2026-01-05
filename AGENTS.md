# AGENTS.md

This document provides essential information for agents working on the ansible-collection-inventory-sacloud repository.

## Project Overview

This is an Ansible Collection that provides a dynamic inventory plugin for Sakura Cloud (Sacloud). The collection allows Ansible to automatically discover and inventory Sakura Cloud resources.

### Structure
```
/
├── README.md                 # Project documentation (in Japanese)
├── galaxy.yml               # Ansible Galaxy collection metadata
└── plugins/
    └── inventory/
        └── sacloud.py       # Main inventory plugin implementation
```

## Essential Commands

### Build and Package
```bash
ansible-galaxy collection build
```
Builds the collection into a tarball for distribution.

### Installation (for development)
```bash
ansible-galaxy collection install git+https://github.com/tokuhirom/ansible-collection-inventory-sacloud.git
```

### Testing the Plugin
```bash
# Test inventory generation (requires valid API credentials)
ansible-inventory -i inventory.yml --list

# Where inventory.yml contains:
# plugin: tokuhirom.sacloud.sacloud
# access_token: <your_token>
# access_token_secret: <your_secret>
# zones:
#   - tk1b
#   - is1a
```

## Code Patterns and Conventions

### Ansible Plugin Structure
- The plugin inherits from `BaseInventoryPlugin` and `Constructable`
- Uses Ansible's plugin documentation format with `DOCUMENTATION` and `EXAMPLES` constants
- Follows Ansible naming conventions: `InventoryModule` class with `NAME = 'sacloud'`

### API Integration
- Uses `ansible.module_utils.urls.open_url` for HTTP requests
- Implements Sakura Cloud API authentication with username/password (token/secret)
- API endpoint pattern: `{api_root}/{zone}/api/cloud/1.1/server`

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

## Dependencies

- Python 3.8+
- Ansible 2.9+
- Valid Sakura Cloud API credentials

## Development Notes

- The plugin is written in a single file (`sacloud.py`)
- No external dependencies beyond Ansible standard library
- No test suite currently present in the repository
- No linting configuration files (tox.ini, etc.) present
