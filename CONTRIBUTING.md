# Contributing to Trakt Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, LLM model)

### Suggesting Enhancements

Feature requests are welcome! Please include:

- Clear use case
- Why this would be valuable
- Potential implementation approach (if applicable)

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**:
   - Follow existing code style
   - Add docstrings to new functions
   - Update README if adding features
   - Test your changes thoroughly
4. **Commit**: `git commit -m 'Add amazing feature'`
5. **Push**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/trakt_agent.git
cd trakt_agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up Trakt API
cp secrets.json.example secrets.json
# Edit secrets.json with your API keys
```

## Code Style

- Follow PEP 8 guidelines
- Use descriptive variable names
- Add type hints where possible
- Write docstrings for functions
- Keep functions focused and concise

## Testing

Before submitting:

- Test with multiple LLM models if possible
- Verify error handling works correctly
- Ensure no secrets are committed
- Test the full workflow end-to-end

## Questions?

Feel free to open an issue for questions or discussions!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
