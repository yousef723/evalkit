
# AI Agent - Setup and Run Instructions

This is now a secure, multi-tenant application using Firebase for user authentication. Each user will have their own private data.

## Prerequisites

- You must have [Node.js](https://nodejs.org/) (version 18 or higher) installed.
- You must have a Google account to create a Firebase project.

## 1. Set Up Firebase (The Authentication Service)

This is a one-time setup that will give you all the keys you need.

### Step 1: Create a Firebase Project

1.  Go to the [Firebase Console](https://console.firebase.google.com/).
2.  Click **"Add project"** and give it a name (e.g., "AI Agent Backend").
3.  Follow the on-screen steps. You can disable Google Analytics for this project if you wish.

### Step 2: Configure Web App Credentials (for Frontend)

1.  Inside your new project, click the Web icon (`</>`) to add a web app.
2.  Give it a nickname (e.g., "AI Agent UI") and click **"Register app"**.
3.  Firebase will show you your `firebaseConfig` object. **Copy this object.**
4.  In your project code, open the `firebase-config.js` file and **paste the copied configuration object**, replacing the placeholder. Save the file.

### Step 3: Enable Authentication Methods

1.  In the Firebase Console, go to the **"Authentication"** section from the left menu.
2.  Click the **"Get started"** button.
3.  In the **"Sign-in method"** tab, enable the providers you want. For this app, enable:
    *   **Email/Password**
    *   **Google**

### Step 4: Generate a Service Account Key (for Backend)

1.  In the Firebase Console, click the gear icon next to "Project Overview" in the top-left and select **"Project settings"**.
2.  Go to the **"Service accounts"** tab.
3.  Click the **"Generate new private key"** button. A JSON file will be downloaded.
4.  Move this downloaded JSON file into the **`server/`** directory of your project.
5.  **Rename the file to `serviceAccountKey.json`**. This is important for security and for the `.gitignore` file to ignore it.

## 2. Set Up the Backend Server

### Step 1: Create Your `.env` File

1.  In the root of your project, create a new file named `.env`.
2.  Copy the content from `.env.example` into it.
3.  It should contain one line, pointing to your service account key:
    ```
    GOOGLE_APPLICATION_CREDENTIALS=./server/serviceAccountKey.json
    ```
    And another line for your Gemini API Key:
    ```
    API_KEY=YOUR_GEMINI_API_KEY_HERE
    ```

### Step 2: Install Dependencies & Run

1.  Open your terminal in the project root.
2.  Run `npm install` to install all dependencies.
3.  Run `npm start` to start the server.

You should see `Server listening on port 3000`. Leave this running.

## 3. Run the Frontend Application

1.  Open the `index.html` file in your web browser.
2.  You will now see a login screen. Sign up or log in.
3.  Once authenticated, you will have access to the AI agent, and all your data will be private to your account.
