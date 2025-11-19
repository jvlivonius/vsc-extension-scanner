# ANTIGRAVITY.md

## 🚀 Project Context
This project uses **`CLAUDE.md`** as the central source of truth.
**You MUST read `CLAUDE.md`** to understand:
- Architecture (3-Layer Strict)
- Security Guidelines (Validation & Sanitization)
- Build & Test Commands
- Project Structure

## ⚠️ Critical Constraints
1. **Security:** Use `validate_path()` and `sanitize_string()` for ALL inputs.
2. **Architecture:** Presentation → Application → Infrastructure. Never import backwards.
3. **Testing:** Maintain 0 vulnerabilities and high coverage.

## 🛠️ Agent Workflow
- **Task Tracking:** Use your internal `task.md` (in `.gemini/antigravity/...`).
- **Planning:** Create `implementation_plan.md` before complex changes.
- **Verification:** Run `python3 -m pytest tests/` after changes.

## 🔗 Key References
- [CLAUDE.md](CLAUDE.md) (Main Entry Point)
- [ARCHITECTURE.md](docs/guides/ARCHITECTURE.md)
- [SECURITY.md](docs/guides/SECURITY.md)
- [PRD.md](docs/project/PRD.md)
