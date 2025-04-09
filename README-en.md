# Anypoint Platform Client

![](./mulesoft.jpg)

A Python program that uses MuleSoft's Anypoint Platform API to retrieve application information. It efficiently retrieves information from API Manager and CloudHub asynchronously and outputs it in JSON format.

## Overview

This tool is useful in the following cases:

- When you want to retrieve API information from Anypoint Platform in bulk
- When you want to retrieve CloudHub application information across environments
- When you want to save the retrieved information as structured JSON

## Features

### API Manager Information Retrieval

- Application list
- Policy settings
- Contracts information
- Alert information
- Tier information

### CloudHub Information Retrieval

- Application list
- Deployment information
- Status information

### Other Features

- Fast information retrieval using asynchronous processing
- Flexible output settings
- Error handling

## Requirements

- Python 3.8 or higher
- Required libraries
  - requests
  - aiohttp
  - python-dotenv

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/big-mon/mulesoft-anypoint-platform.git
cd mulesoft-anypoint-platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
```

Edit the `.env` file and set the following information:

- `ANYPOINT_CLIENT_ID`: Anypoint Platform Client ID
- `ANYPOINT_CLIENT_SECRET`: Anypoint Platform Client Secret
- `ANYPOINT_ORGANIZATION_ID`: Organization ID
- `ANYPOINT_BASE_URL`: Anypoint Platform Base URL (optional)

4. Output Configuration

You can configure whether to output various information and output file names in the `output_config.env` file.

## Usage

### Basic Usage

```bash
python src/main.py
```

### Output Files

When executed, the following files will be output to the `output/YYYYMMDD_HHMM/` directory:

- `api_manager.json`: API Manager information
- `cloudhub.json`: CloudHub information

## Troubleshooting

### Common Errors

1. Authentication Error

   - Check if Client ID, Client Secret, and Organization ID are correctly set

2. Network Error
   - Verify that you can connect to Anypoint Platform
   - If proxy settings are required, set them in environment variables

## Developer Information

### Testing

```bash
python -m pytest tests/
```

### Coding Standards

- Compliant with PEP 8
- Type hints recommended
- Google style for docstrings

## Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'add: some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## Bug Reports & Feature Requests

If you find a bug or have a feature request, please register it in GitHub Issues.

## Change Log

For detailed update history, please refer to [CHANGELOG.md](CHANGELOG.md).

## License

MIT License
