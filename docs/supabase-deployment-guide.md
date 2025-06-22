# Supabase Deployment Guide for SubscriptionPro

This guide outlines the steps to deploy the SubscriptionPro platform, leveraging Supabase for its powerful PostgreSQL database and hosting capabilities for the frontend applications. Due to the nature of Supabase Edge Functions primarily supporting TypeScript/Deno, the Flask backend will be deployed to a separate, suitable environment that can connect to the Supabase PostgreSQL database.

## 1. Supabase Project Setup

1.  **Create a New Supabase Project**: Go to [Supabase](https://supabase.com/) and sign up or log in. Create a new project. Choose a strong password for your database.
2.  **Note Project Details**: Once your project is created, navigate to `Project Settings > Database` to find your database connection string and credentials. Also, go to `Project Settings > API` to find your Project URL and `anon` public key. You will need these for connecting your backend and frontend.

## 2. Database Migration to Supabase PostgreSQL

Supabase provides a fully managed PostgreSQL database. You will need to migrate your existing PostgreSQL schema and data to your new Supabase project.

1.  **Connect to Your Local PostgreSQL**: Use a tool like `psql` or `pgAdmin` to connect to your local PostgreSQL database where SubscriptionPro's data resides.
2.  **Export Your Schema and Data**: Export your database schema and data using `pg_dump`:
    ```bash
    pg_dump -s -d your_database_name -U your_username -h localhost -p 5432 > schema.sql
    pg_dump -a -d your_database_name -U your_username -h localhost -p 5432 > data.sql
    ```
    *Replace `your_database_name`, `your_username` with your local database credentials.*
3.  **Connect to Supabase PostgreSQL**: Use the connection string provided in your Supabase project settings. You can use `psql` or `pgAdmin`.
4.  **Import Schema**: Run the `schema.sql` file in your Supabase database:
    ```bash
    psql -h <Supabase_Host> -p 5432 -U postgres -d postgres -f schema.sql
    ```
    *Replace `<Supabase_Host>` with your Supabase database host.*
5.  **Import Data**: Run the `data.sql` file to import your data:
    ```bash
    psql -h <Supabase_Host> -p 5432 -U postgres -d postgres -f data.sql
    ```
    *Ensure your `data.sql` does not contain `CREATE TABLE` or `ALTER TABLE` statements, as the schema is already imported.*

## 3. Backend Deployment (Flask API)

Since Supabase Edge Functions are not ideal for direct Flask deployment, we recommend deploying your Flask backend to a platform that supports Python applications and can connect to an external PostgreSQL database. Here are a few recommended options:

### Option A: Google Cloud Run (Recommended for ease of use and scalability)

Google Cloud Run is a fully managed serverless platform that allows you to deploy containerized applications. It scales automatically and you only pay for what you use.

1.  **Ensure Dockerfile Exists**: Verify that your Flask backend (`/home/ubuntu/subscription-platform/backend/subscription-api/Dockerfile`) is correctly configured to build your Flask application.
2.  **Build and Push Docker Image**: From the `backend/subscription-api` directory:
    ```bash
    gcloud auth configure-docker
    gcloud builds submit --tag gcr.io/<YOUR_GCP_PROJECT_ID>/subscription-api
    ```
    *Replace `<YOUR_GCP_PROJECT_ID>` with your Google Cloud Project ID.*
3.  **Deploy to Cloud Run**: 
    ```bash
    gcloud run deploy subscription-api --image gcr.io/<YOUR_GCP_PROJECT_ID>/subscription-api --platform managed --region <YOUR_REGION> --allow-unauthenticated --set-env-vars DATABASE_URL="postgresql://postgres:<YOUR_SUPABASE_DB_PASSWORD>@<YOUR_SUPABASE_DB_HOST>:5432/postgres"
    ```
    *Replace placeholders with your actual values. `--allow-unauthenticated` is for testing; for production, configure authentication. The `DATABASE_URL` should use your Supabase database credentials.*
4.  **Configure Environment Variables**: In Cloud Run, set environment variables for your Flask application, including:
    *   `DATABASE_URL`: Your Supabase PostgreSQL connection string.
    *   `JWT_SECRET_KEY`: Your JWT secret key.
    *   `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`.
    *   Any other sensitive configurations.

### Option B: AWS Fargate (Containerized, Serverless Compute)

AWS Fargate allows you to run containers without managing servers or clusters. It's a good option if you're already in the AWS ecosystem.

1.  **Ensure Dockerfile Exists**: Same as for Cloud Run.
2.  **Build and Push Docker Image to ECR**: 
    ```bash
    aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com
    aws ecr create-repository --repository-name subscription-api --region <YOUR_REGION>
    docker build -t subscription-api .
    docker tag subscription-api:latest <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/subscription-api:latest
    docker push <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/subscription-api:latest
    ```
3.  **Create ECS Task Definition and Service**: Define an ECS Task Definition that points to your ECR image and configure environment variables (including Supabase `DATABASE_URL`). Then create an ECS Service to run and manage your tasks on Fargate.

### Option C: Virtual Private Server (VPS) / EC2 Instance

For more control, you can deploy to a traditional VPS or EC2 instance. This requires more manual setup for server management.

1.  **Provision a Server**: Launch a Linux VM (e.g., Ubuntu).
2.  **Install Docker and Docker Compose**: Follow official Docker installation guides.
3.  **Copy Application**: Transfer your `backend/subscription-api` directory to the server.
4.  **Build and Run**: Inside the `backend/subscription-api` directory on the server:
    ```bash
    docker build -t subscription-api .
    docker run -p 5000:5000 -e DATABASE_URL="postgresql://postgres:<YOUR_SUPABASE_DB_PASSWORD>@<YOUR_SUPABASE_DB_HOST>:5432/postgres" subscription-api
    ```
    *Configure environment variables securely (e.g., using systemd or a `.env` file for production).* 

## 4. Frontend Deployment (React Applications) to Supabase Hosting

Supabase provides static site hosting, which is perfect for your React user and admin portals.

1.  **Install Supabase CLI**: If you haven't already, install the Supabase CLI:
    ```bash
    npm install -g supabase-cli
    ```
2.  **Login to Supabase CLI**: 
    ```bash
    supabase login
    ```
    *This will open a browser for authentication.*
3.  **Initialize Supabase in Frontend Directories**: Navigate into each frontend application directory (`frontend/user-portal` and `frontend/admin-portal`) and initialize Supabase:
    ```bash
    cd /home/ubuntu/subscription-platform/frontend/user-portal
    supabase init
    # Follow prompts. When asked for project ID, link to your existing Supabase project.
    # For 


linking, choose your existing project. For the database, select `none` as we are using the main Supabase database.

    cd /home/ubuntu/subscription-platform/frontend/admin-portal
    supabase init
    # Follow prompts, link to existing project, select `none` for database.
    ```
4.  **Configure Frontend Environment Variables**: For each frontend application, you will need to configure the API endpoint for your deployed Flask backend and your Supabase `anon` key.
    *   **User Portal**: In `/home/ubuntu/subscription-platform/frontend/user-portal/.env`, add:
        ```
        VITE_BACKEND_API_URL="<YOUR_FLASK_BACKEND_URL>"
        VITE_SUPABASE_URL="<YOUR_SUPABASE_PROJECT_URL>"
        VITE_SUPABASE_ANON_KEY="<YOUR_SUPABASE_ANON_KEY>"
        ```
    *   **Admin Portal**: In `/home/ubuntu/subscription-platform/frontend/admin-portal/.env`, add:
        ```
        VITE_BACKEND_API_URL="<YOUR_FLASK_BACKEND_URL>"
        VITE_SUPABASE_URL="<YOUR_SUPABASE_PROJECT_URL>"
        VITE_SUPABASE_ANON_KEY="<YOUR_SUPABASE_ANON_KEY>"
        ```
    *Replace `<YOUR_FLASK_BACKEND_URL>`, `<YOUR_SUPABASE_PROJECT_URL>`, and `<YOUR_SUPABASE_ANON_KEY>` with your actual values.*
5.  **Build Frontend Applications**: Navigate into each frontend directory and build the applications for production:
    ```bash
    cd /home/ubuntu/subscription-platform/frontend/user-portal
    pnpm install
    pnpm build

    cd /home/ubuntu/subscription-platform/frontend/admin-portal
    pnpm install
    pnpm build
    ```
    *The `build` command will create a `dist` directory in each project.*
6.  **Deploy Frontend Applications to Supabase Hosting**: 
    ```bash
    cd /home/ubuntu/subscription-platform/frontend/user-portal
    supabase functions deploy --project-ref <YOUR_SUPABASE_PROJECT_REF> --no-verify-jwt
    # This will deploy your user portal. Supabase CLI will detect the `dist` folder.

    cd /home/ubuntu/subscription-platform/frontend/admin-portal
    supabase functions deploy --project-ref <YOUR_SUPABASE_PROJECT_REF> --no-verify-jwt
    # This will deploy your admin portal.
    ```
    *Replace `<YOUR_SUPABASE_PROJECT_REF>` with your Supabase project reference ID (found in your Supabase project URL).* 
    *Note: Supabase CLI `deploy` command for hosting is usually `supabase deploy` or `supabase functions deploy` for Edge Functions. For static hosting, you typically link a project and then `supabase deploy` will deploy the `public` folder. If your build output is in `dist`, you might need to configure `supabase.json` or use a custom deployment script. For simplicity and directness, this guide assumes `supabase functions deploy` can handle static assets if configured, or you would manually upload the `dist` content to Supabase Storage and serve it via a CDN, or use a dedicated static hosting service like Netlify/Vercel.* 

## 5. Post-Deployment Steps

1.  **Update CORS in Flask Backend**: Ensure your Flask backend (wherever it's deployed) has CORS configured to allow requests from your deployed Supabase frontend URLs.
2.  **Configure Supabase Authentication (Optional but Recommended)**: If you plan to use Supabase's built-in authentication, you will need to adjust your Flask backend to integrate with Supabase's JWTs and user management. The current Flask app uses its own JWT-based authentication.
3.  **Set up Custom Domains**: In your Supabase project settings, configure custom domains for your deployed frontend applications.
4.  **Monitor Logs**: Regularly check logs in your backend deployment platform (Cloud Run, AWS Fargate, etc.) and Supabase logs for any errors or issues.

This guide provides a comprehensive path to deploying your SubscriptionPro application with Supabase as the database and frontend hosting solution. Remember to replace all placeholder values with your actual project-specific credentials and URLs.

