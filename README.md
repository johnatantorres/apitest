# AI API Project

A simple web service that uses Artificial Intelligence to answer questions about fixtures and perform tasks.

## What You Need Before You Start

Before you begin, you need to have a few things installed on your computer. Don't worry, I'll guide you!

1.  **Docker Desktop:** This is a tool that makes it very easy to run our entire project (both the application and the database) in a self-contained way.
    *   [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Setup Instructions

Follow these steps carefully to get the project running.

### Step 1: Get the Project and Configure It

3.  Open a "terminal" or "command prompt" window.
    *   **On Windows:** Press the `Windows key`, type `cmd`, and press `Enter`.
    *   **On Mac:** Open the "Terminal" app from your `Applications/Utilities` folder.
4.  Navigate into the project folder you just unzipped. You can do this by typing `cd` followed by the path to the folder.
    *   *Example for Windows:* `cd C:\Users\YourName\Desktop\apitest`
    *   *Example for Mac:* `cd /Users/YourName/Desktop/apitest`

2.  In the project folder, find the file named `.env.example`. Make a copy of this file and rename the copy to `.env`.

3.  Open the new `.env` file with a text editor. You will see something like this:

    ```
    DATABASE_URL=postgresql://user:password@db:5432/mydatabase
    GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY"
    LANGCHAIN_TRACING_V2="true"
    LANGCHAIN_API_KEY="YOUR_LANGSMITH_API_KEY"
    ```

4.  **You must make a change:**
    *   **Add your API keys:** Replace the placeholder values for `GOOGLE_API_KEY` and `LANGCHAIN_API_KEY` with your actual keys.

## How to Run the Application

You're all set! To build the containers and start the entire application (API and database), run this single command in your terminal:

```bash
docker compose up --build
```
*(This command assumes the main application file is `main.py` and the FastAPI instance is named `app`)*

You should see output in your terminal indicating the server is running. You can now access the API:

*   **API Documentation:** Open your web browser and go to `http://127.0.0.1:8000/docs`. You'll see an interactive documentation page where you can explore and test the API.

## How to Stop the Application

1.  **To stop the API server:** Go back to your terminal window where the server is running and press `Ctrl + C` on your keyboard.
2.  **To stop the database:** Run this command in the project folder:
    ```bash
    docker-compose down
    ```