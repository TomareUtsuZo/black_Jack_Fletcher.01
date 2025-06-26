# Game Project

## Important: Development Standards

⚠️ **Before starting development, please read our [Development Guide](DEVELOPMENT_GUIDE.md) thoroughly.** ⚠️

The Development Guide covers critical standards including:
- Strict feature implementation policy
- SOLID principles adherence
- Code atomization and statement-like functions
- Comprehensive type hints and static checking
- Self-commenting code principles
- CI pipeline configuration

These standards are non-negotiable and form the foundation of our development process.

## Development Tasks

This project uses [Task](https://taskfile.dev/) for managing development tasks. Here are the available commands:

### Setup and Running
- `task setup` - Set up the development environment for a coding session
  - Creates Python virtual environment
  - Runs setup script
  - Activates virtual environment

- `task run-flask` - Run the Flask application
  - Activates virtual environment
  - Starts the backend server

### Testing
- `task test-backend` - Run all backend tests
  - Comprehensive test suite for all backend functionality
  - Runs in verbose mode

- `task test-functional` - Run functional tests
  - Tests that verify feature behavior without implementation details
  - Focuses on feature requirements and outcomes

- `task test-gamestate` - Run only game state related tests
  - Tests state management functionality
  - Includes:
    - State manager
    - Game state services (singleton and modular)
    - Faction functionality

- `task test-gamelogic` - Run only game logic related tests
  - Tests core game mechanics
  - Includes:
    - Unit tests
    - Game time functionality

## Development Guidelines

For detailed development guidelines, coding standards, and project architecture, please refer to:
- [Development Guide](DEVELOPMENT_GUIDE.md)
- [Type Checking Configuration](mypy.ini)

## Getting Started

1. **Read the Documentation**:
   - Review [Development Guide](DEVELOPMENT_GUIDE.md) thoroughly
   - Understand our [type checking requirements](mypy.ini)
   - Note the feature implementation policy:
     ```
     No functionality will be implemented without explicit request and approval.
     Related features will be documented as recommendations only.
     ```

2. Install Task (if not already installed):
   - Windows: `choco install go-task`
   - Mac: `brew install go-task`
   - Linux: `sh -c "$(curl --location https://taskfile.dev/install.sh)"`

3. Set up the development environment:
   ```bash
   task setup
   ```

4. Run the application:
   ```bash
   task run-flask
   ```

5. Run tests:
   ```bash
   task test-backend  # Run all tests
   # or
   task test-functional  # Run functional tests only
   ```

## Development Workflow

1. **Before Writing Code**:
   - Ensure the feature is explicitly requested
   - Review relevant sections in [Development Guide](DEVELOPMENT_GUIDE.md)
   - Plan your implementation according to our SOLID principles

2. **During Development**:
   - Follow the code atomization principles
   - Include comprehensive type hints
   - Write self-documenting code
   - Run mypy checks frequently

3. **Before Committing**:
   - Run all relevant tests
   - Ensure type checking passes
   - Verify code meets our style guidelines

## Project Structure

Our project follows the principles outlined in the [Development Guide](DEVELOPMENT_GUIDE.md):
- Clear separation of concerns
- Feature-based organization
- Interface-first design
- Test organization mirrors source code

For detailed information about:
- Code style and formatting → See [Development Guide: Code Style](DEVELOPMENT_GUIDE.md#3-code-style-and-readability)
- Type checking → See [Development Guide: Type Hints](DEVELOPMENT_GUIDE.md#type-hints-and-static-checking)
- Testing strategy → See [Development Guide: Testing](DEVELOPMENT_GUIDE.md#testing-strategy)
