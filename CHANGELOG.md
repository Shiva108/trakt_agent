# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-14

### Added

- **Batch Processing**: Support for marking multiple items as watched in a single command.
- **File Input**: Support for reading titles/seeds from text files (one per line) for `mark` and `recommend` commands.
- **Improved Seeding**: Recommend command now accepts "seed" titles to guide the LLM's specific recommendations.
- **Security**: Enhanced `.gitignore` and added `CODE_OF_CONDUCT.md`.

## [1.0.0] - 2026-01-08

### Added

- Initial release of Trakt Agent
- LLM-powered recommendation engine with local model support
- Enhanced taste profile generation with 7 comprehensive sections
- Automated workflow for marking watched items and generating new recommendations
- Support for multiple LLM backends (LM Studio, Ollama)
- Interactive LLM configuration script
- Comprehensive error handling and troubleshooting guides
- Validation script for multi-model LM Studio setups

### Features

- Deep watch history analysis (500 items)
- Smart filtering to prevent duplicate recommendations
- Customizable preferences (genre exclusions, quality thresholds)
- Qwen 2.5 14B Instruct model optimized for quality recommendations
- Virtual environment auto-loading via shebangs
- Integrated workflow scripts for seamless updates

### Documentation

- Comprehensive README with setup instructions
- LM Studio configuration guide
- Troubleshooting section for common issues
- Example configuration files for security
