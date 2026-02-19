# Task Management Application

This project provides a basic backend API for user authentication and task management, built with FastAPI.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Backend](#running-the-backend)
- [API Endpoints](#api-endpoints)

## Features

- User Registration
- User Login
- Task Creation (authenticated)
- Task Retrieval (authenticated, user-specific)

## Project Structure


.gitignore
README.md
backend/
├── main.py
└── requirements.txt


## Setup Instructions

### Prerequisites

- Python 3.8+

### Installation

1.  **Clone the repository:**

    bash
    git clone <repository-url>
    cd <repository-directory>
    

2.  **Create and activate a virtual environment:**

    bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    

3.  **Install backend dependencies:**

    Navigate to the `backend` directory and install the required packages:

    bash
    cd backend
    pip install -r requirements.txt
    cd .. # Go back to project root
    

## Running the Backend

Once the dependencies are installed, you can start the FastAPI application from the project root:

bash
# Ensure your virtual environment is activated
uvicorn backend.main:app --reload --port 8000


The API will be accessible at `http://127.0.0.1:8000`.

You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs` and ReDoc at `http://127.0.0.1:8000/redoc`.

## API Endpoints

The backend application provides the following endpoints:

### User Authentication

-   **`POST /users/register`**
    -   Registers a new user.
    -   **Request Body**: `{"email": "string", "password": "string"}`

-   **`POST /users/login`**
    -   Logs in a user and returns an access token.
    -   **Request Body**: `{"username": "string", "password": "string"}` (Note: `username` refers to the user's email here)

### Task Management

-   **`POST /tasks/`**
    -   Creates a new task for the authenticated user.
    -   **Requires Authentication**: Pass the `access_token` in the `Authorization: Bearer <token>` header.
    -   **Request Body**: `{"title": "string", "description": "string | None = None"}`

-   **`GET /tasks/`**
    -   Retrieves all tasks for the authenticated user.
    -   **Requires Authentication**: Pass the `access_token` in the `Authorization: Bearer <token>` header.
