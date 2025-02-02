## v0.2.0 (2025-02-02)

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

- **deps-dev**: add commitizen and cz-conventional-gitmoji
- **deps**: bump advanced-alchemy from 0.27.1 to 0.30.3

### 📝💡 Documentation

- update license and project configuration
