# GPTonRoids

## Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/GPTonRoids.git
   cd GPTonRoids
   ```

2. **Create and Activate Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Copy the example environment file and update the necessary variables.
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to set `API_KEY`, `GITHUB_TOKEN`, and other required variables.

5. **Start the Application:**
   ```bash
   ./start_all.sh
   ```

6. **Run Tests:**
   ```bash
   pytest
   ```

## API Documentation

Once the server is running, navigate to `/docs` to access the interactive API documentation provided by FastAPI's Swagger UI.

## Security Recommendations

- **Protect Your API Key:** Ensure that the `API_KEY` is kept secret and not exposed in version control systems.
- **Limit GitHub Token Permissions:** The `GITHUB_TOKEN` should have the minimal required permissions to perform necessary actions.

## License

MIT