# Firebase Deployment Guide for SubscriptionPro

This guide provides comprehensive, step-by-step instructions for deploying the SubscriptionPro platform using Firebase. This includes deploying the React frontend applications to Firebase Hosting and the Flask backend API to Google Cloud Run, which can then be seamlessly integrated with Firebase Hosting for a unified domain. We will assume your PostgreSQL database remains external (e.g., hosted on a cloud provider like Supabase, AWS RDS, or Google Cloud SQL).

## 1. Firebase Project Setup

1.  **Create a Firebase Project**: Go to the [Firebase Console](https://console.firebase.google.com/) and sign in with your Google account. Click "Add project" and follow the prompts to create a new Firebase project. Choose a unique Project ID.
2.  **Install Firebase CLI**: If you haven't already, install the Firebase CLI globally:
    ```bash
    npm install -g firebase-tools
    ```
3.  **Login to Firebase CLI**: Authenticate your Firebase CLI with your Google account:
    ```bash
    firebase login
    ```
4.  **Initialize Firebase in Project Root**: Navigate to the root of your `subscription-platform` directory and initialize Firebase. This will create a `firebase.json` and `.firebaserc` file.
    ```bash
    cd /home/ubuntu/subscription-platform
    firebase init
    ```
    *   When prompted, select "Hosting" and "Functions" (if you plan to use Cloud Functions directly, otherwise just Hosting is fine for Cloud Run integration).
    *   Choose your newly created Firebase project.
    *   For Hosting, specify your public directory (e.g., `frontend/user-portal/dist` for the user portal and `frontend/admin-portal/dist` for the admin portal, you'll configure redirects later).
    *   For Functions, select Python as the language if prompted, and choose a region.
    *   Do NOT overwrite `package.json` or `index.js` if they exist.

## 2. Backend Deployment (Flask API to Google Cloud Run)

Deploying your Flask API to Google Cloud Run is the recommended approach for a full-fledged API, as it provides better performance and scalability than wrapping the entire Flask app within a single Firebase Cloud Function. Firebase Hosting can then proxy requests to your Cloud Run service.

### 2.1. Prepare Flask Application for Cloud Run

1.  **Ensure `Dockerfile` Exists**: Your Flask backend (`backend/subscription-api/Dockerfile`) should be correctly configured to build your Flask application. Ensure it exposes port `8080` (Cloud Run's default).
    *   Example `Dockerfile` (already present in your codebase):
        ```dockerfile
        # backend/subscription-api/Dockerfile
        FROM python:3.11-slim

        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        COPY . .

        CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app
        ```
    *   **Note**: The `main:app` refers to `app` object in `main.py`. Ensure your `main.py` has `app = Flask(__name__)` and that `app` is the Flask application instance.
2.  **Update `main.py` for Gunicorn**: Ensure your `main.py` is structured to be run by Gunicorn. The current `main.py` in your codebase is already suitable for this, as it exposes `app` directly.

### 2.2. Deploy to Google Cloud Run

1.  **Enable Cloud Run API**: In your Google Cloud Project (linked to your Firebase project), ensure the Cloud Run API is enabled.
2.  **Build and Push Docker Image**: From the `backend/subscription-api` directory:
    ```bash
    cd /home/ubuntu/subscription-platform/backend/subscription-api
    gcloud auth configure-docker
    gcloud builds submit --tag gcr.io/<YOUR_GCP_PROJECT_ID>/subscription-api
    ```
    *Replace `<YOUR_GCP_PROJECT_ID>` with your Google Cloud Project ID (same as Firebase Project ID).* 
3.  **Deploy to Cloud Run**: 
    ```bash
    gcloud run deploy subscription-api --image gcr.io/<YOUR_GCP_PROJECT_ID>/subscription-api --platform managed --region <YOUR_REGION> --allow-unauthenticated --set-env-vars DATABASE_URL="postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>",JWT_SECRET_KEY="<YOUR_JWT_SECRET>",RAZORPAY_KEY_ID="<YOUR_RAZORPAY_KEY_ID>",RAZORPAY_KEY_SECRET="<YOUR_RAZORPAY_KEY_SECRET>"
    ```
    *Replace placeholders with your actual values. `<YOUR_REGION>` should be a Google Cloud region (e.g., `us-central1`). `--allow-unauthenticated` is for initial setup; for production, configure authentication and use Firebase Hosting rewrites for secure access. The `DATABASE_URL` should point to your external PostgreSQL database.*
4.  **Note Cloud Run Service URL**: After successful deployment, Cloud Run will provide a service URL (e.g., `https://subscription-api-<hash>-<region>.run.app`). Note this URL, as you will use it in Firebase Hosting rewrites.

## 3. Frontend Deployment (React Applications to Firebase Hosting)

Your React applications (User Portal and Admin Portal) will be built and deployed as static assets to Firebase Hosting.

### 3.1. Configure `firebase.json` for Hosting

Modify your `firebase.json` file (located in `/home/ubuntu/subscription-platform`) to host both frontends and rewrite API requests to your Cloud Run backend.

```json
{
  "hosting": [
    {
      "target": "user-portal",
      "public": "frontend/user-portal/dist",
      "ignore": [
        "firebase.json",
        "**/.*",
        "**/node_modules/**"
      ],
      "rewrites": [
        {
          "source": "/api/**",
          "destination": "https://subscription-api-<hash>-<region>.run.app/api"
        },
        {
          "source": "**",
          "destination": "/index.html"
        }
      ]
    },
    {
      "target": "admin-portal",
      "public": "frontend/admin-portal/dist",
      "ignore": [
        "firebase.json",
        "**/.*",
        "**/node_modules/**"
      ],
      "rewrites": [
        {
          "source": "/api/**",
          "destination": "https://subscription-api-<hash>-<region>.run.app/api"
        },
        {
          "source": "**",
          "destination": "/index.html"
        }
      ]
    }
  ],
  "functions": {
    "source": "backend/subscription-api",
    "runtime": "python311"
  }
}
```

*   **Important**: Replace `https://subscription-api-<hash>-<region>.run.app` with the actual URL of your deployed Cloud Run service.
*   **Targets**: You need to define hosting targets in `.firebaserc` for this to work. Add the following to your `.firebaserc` in the root directory:
    ```json
    {
      "projects": {
        "default": "<YOUR_FIREBASE_PROJECT_ID>"
      },
      "targets": {
        "hosting": {
          "user-portal": [
            "<YOUR_FIREBASE_PROJECT_ID>"
          ],
          "admin-portal": [
            "<YOUR_FIREBASE_PROJECT_ID>"
          ]
        }
      }
    }
    ```

### 3.2. Prepare Frontend Applications

1.  **Configure Frontend Environment Variables**: For each frontend application, update the `VITE_BACKEND_API_URL` to point to the relative path `/api` which will be rewritten by Firebase Hosting.
    *   **User Portal**: In `/home/ubuntu/subscription-platform/frontend/user-portal/.env`, set:
        ```
        VITE_BACKEND_API_URL="/api"
        ```
    *   **Admin Portal**: In `/home/ubuntu/subscription-platform/frontend/admin-portal/.env`, set:
        ```
        VITE_BACKEND_API_URL="/api"
        ```
2.  **Build Frontend Applications**: Navigate into each frontend directory and build the applications for production:
    ```bash
    cd /home/ubuntu/subscription-platform/frontend/user-portal
    pnpm install
    pnpm build

    cd /home/ubuntu/subscription-platform/frontend/admin-portal
    pnpm install
    pnpm build
    ```
    *This will create `dist` directories containing the production-ready static assets.*

### 3.3. Deploy Frontends to Firebase Hosting

1.  **Deploy to Firebase Hosting**: From the root of your `subscription-platform` directory:
    ```bash
    firebase deploy --only hosting
    ```
    *This command will deploy both `user-portal` and `admin-portal` targets as configured in `firebase.json`.*

## 4. Database Connection

Your Flask backend (deployed to Cloud Run) will connect to your external PostgreSQL database using the `DATABASE_URL` environment variable configured during Cloud Run deployment. Ensure your PostgreSQL database is accessible from Google Cloud (e.g., public IP, VPC Peering, Cloud SQL Proxy).

## 5. Environment Variables and Security

*   **Backend (Cloud Run)**: Environment variables are set directly during `gcloud run deploy` or via the Cloud Run console. **NEVER commit sensitive keys to your repository.**
*   **Frontend (Firebase Hosting)**: Frontend environment variables (e.g., `VITE_BACKEND_API_URL`) are baked into the build process. Sensitive keys should generally NOT be exposed in the frontend.
*   **CORS**: Ensure your Flask backend has CORS configured to allow requests from your Firebase Hosting domains (e.g., `https://<YOUR_FIREBASE_PROJECT_ID>.web.app`).

## 6. Post-Deployment Steps

1.  **Custom Domains**: In the Firebase Console, navigate to "Hosting" to add and configure custom domains for your deployed applications.
2.  **Monitoring and Logging**: Utilize Google Cloud Logging and Monitoring for your Cloud Run service, and Firebase Analytics for your frontend applications.
3.  **Security Rules**: Implement Firebase Security Rules if you decide to use Firebase Firestore or Realtime Database in the future.
4.  **Authentication**: If you plan to use Firebase Authentication, you will need to integrate it with your Flask backend (e.g., verifying Firebase ID Tokens).

This guide provides a robust and scalable deployment strategy for SubscriptionPro on Firebase, leveraging Cloud Run for the backend API. Remember to replace all placeholder values with your actual project-specific credentials and URLs.


