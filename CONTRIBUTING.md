# Contributing to Travel A2A Agents

Thank you for your interest in contributing to `travel-a2a-agents`.

This project demonstrates how specialized travel agents can collaborate through an Agent-to-Agent (A2A) protocol to produce complete itineraries, recommendations, and travel guidance. Contributions that improve reliability, developer experience, architecture clarity, and end-user value are all welcome.

## What We Value

We want contributions to keep the project:

- Clear for new contributors to understand.
- Practical enough to serve as a real portfolio-quality reference.
- Easy to run locally with minimal setup friction.
- Safe to extend without breaking the multi-agent workflow.

## Contribution Areas

Some especially valuable ways to contribute:

- Improve agent coordination and routing logic.
- Add stronger validation and error handling across agent boundaries.
- Expand support for real travel APIs and provider adapters.
- Improve the Flask UI and frontend experience.
- Add automated tests for protocol, agent behavior, and integration flows.
- Improve docs, examples, and onboarding for developers.
- Tighten code quality, formatting, and maintainability.

## Before You Start

Please review the repository structure and current workflow before making changes:

- `main.py` runs the CLI experience.
- `app.py` runs the Flask web app.
- `agents/` contains the coordinator and specialized travel agents.
- `a2a_protocol/` contains the protocol and message abstractions.
- `templates/` and `static/` power the browser UI.

If you are planning a larger change, open an issue first so the direction can be aligned before implementation begins.

## Local Development Setup

### 1. Fork and clone

```bash
git clone https://github.com/hardikrathod777/travel-a2a-agents.git
cd travel-a2a-agents
```

### 2. Create a virtual environment

```bash
py -3.12 -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

Notes:

- `OPENAI_API_KEY` is required for AI-powered responses.
- `SERPAPI_API_KEY` is optional if you are working with mocked or fallback data paths.
- Never commit secrets, tokens, or personal credentials.

## Running the Project

### CLI mode

```bash
python main.py
```

### Web app

```bash
python app.py
```

Then open `http://localhost:5000`.

## Code Quality Expectations

Please keep changes production-minded and easy for others to maintain.

### General guidelines

- Keep functions focused and names explicit.
- Prefer readability over cleverness.
- Preserve existing project structure unless there is a strong reason to change it.
- Keep agent responsibilities separated and predictable.
- Handle failures gracefully, especially where agents exchange data.
- Avoid introducing unrelated refactors in the same pull request.

### Python guidelines

- Follow PEP 8 style conventions.
- Add docstrings where they improve maintainability.
- Keep public method contracts stable unless the change is intentional and documented.
- Validate external inputs and API responses before using them.

### Frontend guidelines

- Keep UI changes consistent with the current Flask + static asset approach.
- Favor simple, accessible interfaces over overly complex interactions.
- Test layout and behavior in the browser after changing templates or assets.

## Recommended Checks

Run these checks before opening a pull request:

```bash
python -m black .
python -m flake8 .
python -m pytest
```

If you add or change behavior, include or update tests whenever practical.

## Branch and Commit Guidance

Use small, focused branches and commits.

Recommended branch naming:

- `feature/add-amadeus-flight-search`
- `fix/hotel-agent-date-validation`
- `docs/improve-contributor-guide`

Recommended commit style:

- `feat: add hotel result normalization`
- `fix: handle invalid departure dates in travel agent`
- `docs: improve setup and contribution guidance`

## Pull Request Checklist

Before submitting a pull request, make sure:

- The change has a clear purpose.
- The branch is up to date with the target base branch.
- Code is formatted and linted.
- Tests pass locally, or any gaps are explained in the PR.
- New behavior is documented where necessary.
- Screenshots are included for UI changes.
- Secrets, temporary files, and machine-specific config are not included.

## Pull Request Description Template

Use a PR description that makes review easy:

```md
## Summary
- What changed
- Why it changed

## Testing
- `python -m pytest`
- `python -m flake8 .`
- Manual testing performed

## Notes
- Tradeoffs, follow-ups, or known limitations
```

## Documentation Standards

Documentation contributions are welcome and important.

Good documentation updates usually:

- Explain the why, not just the what.
- Match the current codebase behavior.
- Include exact commands where useful.
- Help a new developer get productive quickly.

## Reporting Bugs

When reporting a bug, please include:

- A short, descriptive title.
- Expected behavior.
- Actual behavior.
- Steps to reproduce.
- Relevant logs or screenshots.
- Environment details such as Python version and operating system.

## Suggesting Features

Feature requests are most helpful when they include:

- The problem being solved.
- Why the current behavior is insufficient.
- A proposed approach, if you have one.
- Any expected tradeoffs or implementation notes.

## Review Philosophy

We aim for reviews that are:

- Respectful and direct.
- Focused on correctness, maintainability, and clarity.
- Helpful to both experienced and first-time contributors.

Feedback should improve the project and help contributors move faster, not slow them down unnecessarily.

## Security and Sensitive Data

Please do not include:

- API keys or secrets in code, screenshots, or logs.
- Private endpoints or credentials in examples.
- Sensitive personal travel or account data in issues or PRs.

If you discover a security issue, report it responsibly and avoid posting exploit details publicly until it can be addressed.

## First Contribution Ideas

If you want a strong first contribution, consider:

- Adding tests for agent response handling.
- Improving error messages in API or protocol flows.
- Fixing setup inconsistencies in docs.
- Polishing the web UI for clarity and accessibility.
- Adding input validation for request parameters.

## Thanks

Thoughtful contributions make this repository more useful as both a learning resource and a production-style reference project. Thanks for helping improve it.
