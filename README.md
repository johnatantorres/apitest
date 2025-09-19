# AI API Project

A simple web service that uses Artificial Intelligence to answer questions about fixtures and perform tasks.

## Project Description

This project is a backend API for a conversational chatbot about fixtures and odds. It is built using Python, FastAPI, and leverages the power of Large Language Models (LLMs) through the LangChain framework. The application is containerized with Docker for easy setup and deployment.

The core functionality is to provide a chat endpoint that can maintain a conversation with a user, remember context, and provide helpful and relevant responses.

### Technologies Used

-   **Backend**: Python, FastAPI
-   **LLM Framework**: LangChain
-   **Database**: PostgreSQL
-   **Database Migrations**: Alembic
-   **Containerization**: Docker, Docker Compose
-   **LLM Provider**: Gemini

## What You Need Before You Start

Before you begin, you need to have a few things installed on your computer. Don't worry, I'll guide you!

1.  **Docker Desktop:** This is a tool that makes it very easy to run our entire project (both the application and the database) in a self-contained way.
    *   [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
    *   API key created in Google AI Studio
    *   API key created in LangSmith (optional)

## Setup Instructions

Follow these steps carefully to get the project running.

### Step 1: Get the Project and Configure It

1.  First, get the project files onto your computer (e.g., by unzipping the provided archive).

2.  Open a "terminal" or "command prompt" window.
    *   **On Windows:** Press the `Windows key`, type `cmd`, and press `Enter`.
    *   **On Mac:** Open the "Terminal" app from your `Applications/Utilities` folder.

3.  Navigate into the project folder. You can do this by typing `cd` followed by the path to the folder.
    *   *Example for Windows:* `cd C:\Users\YourName\Desktop\apitest`
    *   *Example for Mac:* `cd /Users/YourName/Desktop/apitest`

4.  In the project folder, find the file named `.env.example`. Make a copy of this file and rename the copy to `.env`.

5.  Open the new `.env` file with a text editor. You will see something like this:

    ```
    DATABASE_URL=postgresql://user:password@db:5432/mydatabase
    GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY"
    LANGSMITH_TRACING=true
    LANGSMITH_API_KEY="YOUR_LANGSMITH_API_KEY"
    LANGSMITH_PROJECT="YOUR_LANGSMITH_PROJECT_NAME"
    ```
    NOTE: langsmith tracing, api key and project are optional for tracing you can remove if you want.

6.  **You must make a change:**
    *   **Add your API keys:** Replace the placeholder values for `GOOGLE_API_KEY` and `LANGSMITH_API_KEY` with your actual keys.

## How to Run the Application

You're all set! To build the containers and start the entire application (API and database), run this single command in your terminal:

```bash
docker compose up --build
```
You should see output in your terminal indicating the server is running. You can now access the API:

*   **API Documentation:** Open your web browser and go to `http://127.0.0.1:8000/docs`. You'll see an interactive documentation page where you can explore and test the API.

## How to Stop the Application

1.  **To stop the API server:** Go back to your terminal window where the server is running and press `Ctrl + C` on your keyboard.
2.  **To stop and remove the containers:** Run this command in the project folder:
    ```bash
    docker compose down
    ```

### Usage Examples & Sample Interactions

You can interact with the chatbot via a chat endpoint (e.g., `/initiate_chat/{thread_id}`). You'll need to provide a `thread_id` to maintain conversation context and a `query` to get a response.

**Example `curl` request:**

```bash
# Start a new thread
curl -X 'POST' \'http://127.0.0.1:8000/initiate_thread/{user_id}' \
  -H 'accept: application/json' \
  -d ''
```
Users available can be get by:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/get_users/' \
  -H 'accept: application/json'
```
Then execute `initiate_chat` endpoint

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/initiate_chat/5' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "Hello"
}'
```

**Sample Interaction:**

>**User**: "Which team has the best odds tomorrow?"
>
>**ChatBet**: (uses tool to check_odd_by_dates)
>
>**ChatBet**: The term "best odds" can mean two different things:
>
>The Highest Potential Payout: The biggest number, which represents the riskiest bet but offers the largest reward.
The Most Likely Outcome: The smallest number, which represents the safest bet with the highest probability of happening, but offers the smallest reward.
>
>Let's break it down based on the data we found for tomorrow:
>
>...
>
>**User**: Give me a recommendation for Sunday
>
>**ChatBet**: (uses tool to check_odd_by_date)
>
>**ChatBet**: Based on the fixtures and odds available for Sunday, here are some recommendations based on risk levels:
>1. Conservative Option: (details of low-risk bets)
>2. Moderate Value Option: (details of medium-risk bets)
>3. Risky Option -Higher Payout: (details of high-risk bets)

## Technical Decisions & Explanations

This FastAPI application has been designed to run code operations, save data to a database for persistent storage, and retrieve this data for use in subsequent operations. The database used is PostgreSQL, which stores users, threads, and history that can later be recovered within the LangChain context.

The chatbot architecture is based on the ReAct (Reasoning and Acting) framework, which enables the LLM to have extended capabilities through the use of tools. In this project, the tools check fixtures and odds by teams, individual team, date, or date ranges.

The prompt contain all the behaviour about how the system will behave, including contextual information such as the user's name, their favorite sport, and the current date to easily understand when users ask about events "tomorrow," "this weekend," etc.

Database tables are set up using SQLAlchemy models, and seed data is inserted into the database once the Docker project is initialized and running.

For monitoring the operations of the tools it's used the langsmith, which allow us to know what is happening in each step of a call and identify bottle necks in the executions.

Error manager modules it centralized in a module and then imported to not overcharge the service.py as well as tools was define in other module as their logic is long.