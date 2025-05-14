# Contributing to Lutron Telnet Controller

Thank you for your interest in contributing to the Lutron Telnet Controller project! This document provides guidelines and instructions for contributing to this project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your forked repository to your local machine
3. Set up the development environment:
   ```bash
   # Install in development mode
   pip install -e .
   
   # Make scripts executable
   chmod +x lutron_cli.py lutron
   ```

## Project Structure

The project is organized as follows:

- `src/` - Core library code
- `scripts/` - Individual utility scripts
- `docs/` - Documentation files
- `lutron_cli.py` - Main command-line interface

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding style guidelines below

3. Test your changes thoroughly

4. Commit your changes with a clear, descriptive commit message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a pull request against the main repository

## Coding Style Guidelines

- Follow PEP 8 style guidelines for Python code
- Use clear, descriptive variable and function names
- Include docstrings for all functions and classes
- Add type hints where appropriate
- Keep lines to a maximum of 100 characters
- Use 4 spaces for indentation (no tabs)

## Adding New Features

When adding new features:

1. Keep the core library in `src/` and add any new utility scripts to `scripts/`
2. Update the CLI in `lutron_cli.py` to expose the new functionality
3. Add proper documentation for the new feature
4. Add any new zone definitions to `src/lutron_zones.py`

## Bug Reports

When reporting bugs:

1. Describe the issue clearly
2. Provide steps to reproduce the issue
3. Include the expected behavior and actual behavior
4. Mention your environment (Python version, OS, etc.)

## Feature Requests

Feature requests are welcome! When requesting a feature:

1. Clearly describe the feature
2. Explain why it would be useful
3. Provide examples of how it might be used

## Documentation

Improvements to documentation are always welcome. This includes:

- Better explanations in comments and docstrings
- Improved README
- More examples
- Additional guides

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License). 