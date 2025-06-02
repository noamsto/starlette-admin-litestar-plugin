## v0.3.2 (2025-06-02)

### 🐛🚑️ Fixes

- update development environment configuration

### 📝💡 Documentation

- add changelog URL to project metadata

## v0.3.1 (2025-02-19)

### 🐛🚑️ Fixes

- update starlette-admin dependency and remove custom source

## v0.3.0 (2025-02-19)

### ✨ Features

- add starlette-admin git source to uv config

## v0.2.1 (2025-02-12)

### ♻️ Refactorings

- rename exclude_audit_columns_create_edit to read_only_audit_columns

## v0.2.0 (2025-02-10)

### ✨ Features

- add local environment file support

### 🐛🚑️ Fixes

- **ci**: update tag name variable in release workflow

### 💚👷 CI & Build

- update project configuration and metadata
- add git user configuration for version bump workflow
- update PyPI publish token name in bumpversion workflow
- remove Nix badge and Hatch build configuration
- update project configuration and package metadata
- add package build configuration and author info
- update release workflow to use uv package manager

### 📝💡 Documentation

- update README and add basic example

### 🧹 chore

- remove CHANGELOG.md file

## v0.1.0 (2025-02-06)

### ✨ Features

- add advanced alchemy example and model view
- **advanced-alchemy**: add DateTimeUTC field support and improve field exclusions
- **advanced-alchemy**: exclude sentinel field from all views
- **admin**: add support for GUID/UUID fields in advanced-alchemy models
- initial project setup and implementation

### 🐛🚑️ Fixes

- **build**: correct uv lock upgrade command in commitizen config

### ♻️ Refactorings

- enhance ModelView and field handling for advanced alchemy
- **advanced-alchemy**: simplify DateTimeUTCField handling and display
- rename src directory to starlette_admin_litestar_plugin
- reorganize project structure and improve config handling

### 💚👷 CI & Build

- add GitHub release creation to version bump workflow
- **bumpversion**: update authentication method to use SSH key
- update GitHub token references in bumpversion workflow
- add version bump workflow and update dependencies
- **deps-dev**: add commitizen and cz-conventional-gitmoji
- **deps**: bump advanced-alchemy from 0.27.1 to 0.30.3

### 📝💡 Documentation

- update license and project configuration

### 🧹 chore

- revert version number to 0.1.0
