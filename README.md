# ZED Backup

A simple utility to automatically backup and sync files to a private GitHub Gist.

## Description

ZED Backup is a Python-based tool that allows you to backup a text file to a GitHub Gist. It creates a new private Gist on the first run and updates the same Gist on subsequent runs, providing a simple way to backup and version your text content online.

## Features

- Creates a private GitHub Gist for secure storage
- Automatically updates the same Gist on subsequent runs
- Simple configuration through environment variables or .env file
- Tracks the Gist ID for continuous updates

## Prerequisites

- Python 3.12+
- A GitHub account
- A GitHub personal access token with the `gist` scope

## Installation

1. Clone this repository or download the script:

```bash
git clone https://github.com/yourusername/zed_backup.git
cd zed_backup
```

2. Install the required dependencies:

```bash
uv sync
```

## Setup

1. Create a GitHub personal access token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Click "Generate new token"
   - Give it a name and select the `gist` scope
   - Copy the generated token

2. Set up the environment variables:

   Create a `.env` file in the same directory as the script with the following content:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

   Alternatively, set the environment variable directly in your shell:
   ```bash
   export GITHUB_TOKEN=your_github_token_here
   ```

3. Configure the file to backup:

   By default, the script backs up a file named `~/.config/zed/settings.json` in the same directory. To change this, modify the `FILE_TO_UPLOAD` variable in the script.

## Usage

1. Ensure your file to backup (default: `~/.config/zed/settings.json`) exists and contains the content you want to backup.

2. Run the script:

```bash
python zed_backup.py
```

3. On the first run, the script will create a new Gist and store the Gist ID in `gist_id.txt`. On subsequent runs, it will update the existing Gist.

## How It Works

1. The script checks if a `gist_id.txt` file exists
2. If it doesn't exist, the script creates a new private Gist with your file content
3. If it exists, the script updates the Gist specified by the ID in the file
4. The script stores the Gist ID in `gist_id.txt` for future updates

## Customization

You can modify the following variables in the script to customize its behavior:

- `GIST_ID_FILE`: The file where the Gist ID is stored (default: `gist_id.txt`)
- `FILE_TO_UPLOAD`: The file to backup (default: `~/.config/zed/settings.json`)

## Troubleshooting

- **"GITHUB_TOKEN is not set"**: Make sure you've set up the GitHub token correctly in the .env file or as an environment variable.
- **Error creating/updating Gist**: Check your GitHub token permissions and ensure it has the `gist` scope.
- **File not found**: Ensure the file specified in `FILE_TO_UPLOAD` exists in the same directory as the script.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
