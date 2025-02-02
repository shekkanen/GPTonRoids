# GPTonRoids

GPTonRoids is a powerful and flexible application that bridges the capabilities of ChatGPT with your local environment and various third-party services through GPT Actions. By leveraging FastAPI and a suite of custom endpoints, GPTonRoids enables seamless interaction between natural language commands and system-level operations, enhancing productivity and extending the functionality of ChatGPT for specific use cases.

## Table of Contents
- [Features](#features)
- [How It Works](#how-it-works)
- [Setup](#setup)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Security](#security)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

GPTonRoids offers a comprehensive set of features that allow users to interact with their local system and third-party services using natural language through ChatGPT:

### File Management:
- Create, read, update, and delete files and directories.
- Append content or lines to existing files.
- Search for files by name or content.
- Retrieve file metadata.

### Command Execution:
- Run predefined safe commands (e.g., `ls`, `pwd`, `echo`) with a secure whitelist mechanism.


### GitHub Integration:
- Fetch repository information and issues.
- Create new GitHub issues directly from ChatGPT.

### Text-to-Speech:
- Convert text input into WAV audio files and play them in the background.

### Screenshot Capture:
- Capture screenshots of the local machine and retrieve the file path.

### API Extensions:
- Easily extendable with additional endpoints to integrate more services and functionalities.

### Ngrok Integration:
- Expose the local FastAPI server to the internet securely using ngrok, enabling remote access and integration with GPT Actions.

## How It Works

GPTonRoids leverages GPT Actions, a feature that allows ChatGPT to perform API calls based on natural language inputs. Here's an overview of the architecture and workflow:

### FastAPI Server:
- Serves as the backend, providing various RESTful API endpoints that perform system operations and interact with third-party services.
- Implements security measures using API keys to ensure that only authorized requests are processed.

### GPT Actions:
- Custom GPTs are configured to use GPT Actions by defining the necessary API schemas and authentication.
- When a user interacts with ChatGPT using natural language, GPT Actions translate these inputs into corresponding API calls to GPTonRoids.

### Ngrok Tunneling:
- Ngrok is used to create a secure tunnel to the local FastAPI server, making it accessible over the internet.
- This allows GPT Actions to communicate with GPTonRoids regardless of the server's local environment.

### Environment Management:
- Environment variables are managed through a `.env` file, storing sensitive information like API keys and tokens securely.

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/GPTonRoids.git
   cd GPTonRoids
Use code with caution.
Markdown
Create and Activate Virtual Environment:

python3 -m venv venv
source venv/bin/activate
Use code with caution.
Bash
Install Dependencies:

pip install -r requirements.txt
Use code with caution.
Bash
Configure Environment Variables using .env file:

Copy the example environment file and update the necessary variables.

cp .env.example .env
Use code with caution.
Bash
The .env file should contain the following variables:

GPTONROIDS_API_KEY: Your API key for securing the GPTonRoids API. Important: Keep this key secret.

GITHUB_TOKEN: Your personal GitHub access token. Required for GitHub integration features. Ensure it has the necessary permissions for the actions you intend to perform (e.g., read repository info, create issues).

WORK_DIR (Optional): The main working directory for GPTonRoids. If not set or left empty, it defaults to <project_root>/work. You can customize this to point to a different location if needed.

Example .env file:

GPTONROIDS_API_KEY=your_secret_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here
WORK_DIR=/path/to/your/custom/work_dir  # Optional, uncomment and customize if needed
Use code with caution.
Edit the .env file to set GPTONROIDS_API_KEY, GITHUB_TOKEN, and other required variables.

Start the Application:

./start_all.sh
Use code with caution.
Bash
Run Tests:

pytest
Use code with caution.
Bash
Environment Variables
GPTonRoids uses environment variables for configuration, managed through a .env file for ease of setup and security. See the "Setup" section for details on configuring these variables.

API Documentation
Once the server is running, navigate to /docs to access the interactive API documentation provided by FastAPI's Swagger UI.

Security Recommendations
Protect Your API Key: Ensure that the GPTONROIDS_API_KEY is kept secret and not exposed in version control systems.

Limit GitHub Token Permissions: The GITHUB_TOKEN should have the minimal required permissions to perform necessary actions.

License
MIT

Use code with caution.
.env.example

Use code with caution.
GPTONROIDS_API_KEY=your_secret_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here

WORK_DIR=/path/to/your/custom/work_dir # Optional, uncomment and customize if needed
