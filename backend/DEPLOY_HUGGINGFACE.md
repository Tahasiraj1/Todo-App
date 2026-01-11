# Deploying FastAPI Backend on Hugging Face Spaces

This guide walks you through deploying your FastAPI backend to Hugging Face Spaces step by step.

## Prerequisites

Before you begin, ensure you have:

1. **Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co/join) if you don't have one
2. **Hugging Face CLI** (optional but recommended):
   ```bash
   pip install huggingface_hub
   ```
3. **Git** installed and configured
4. **Docker** (for local testing, optional)
5. **Environment Variables Ready**:
   - `DATABASE_URL` - Your Neon PostgreSQL connection string
   - `BETTER_AUTH_URL` - Your Better Auth frontend URL
   - `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
   - `DEBUG` - Optional, set to "true" for debug logging

---

## Step 1: Create a Hugging Face Space

1. **Go to Hugging Face Spaces**:
   - Navigate to [huggingface.co/spaces](https://huggingface.co/spaces)

2. **Click "Create new Space"**

3. **Configure your Space**:
   - **Space name**: Choose a unique name (e.g., `todo-backend-api`)
   - **SDK**: Select **Docker**
   - **Visibility**: Choose Public or Private
   - **Hardware**: Select **CPU Basic** (free tier) or upgrade if needed
   - Click **Create Space**

4. **Copy the repository URL**:
   - After creation, note the Git repository URL (e.g., `https://huggingface.co/spaces/yourusername/todo-backend-api`)

---

## Step 2: Prepare Your Code Structure

Your Space needs a specific structure. Since your backend code is in a `backend/` folder, you have two options:

### Option A: Deploy Only Backend (Recommended)

1. **Create a temporary deployment directory** (outside your main project):
   ```bash
   mkdir ~/todo-backend-deploy
   cd ~/todo-backend-deploy
   ```

2. **Copy only the backend files needed**:
   ```bash
   # Copy the backend folder contents
   cp -r /path/to/Todo-App/backend/* .
   
   # Or on Windows (PowerShell):
   # Copy-Item -Path "C:\Users\user\OneDrive\Desktop\Code.Taha\Projects\Quarter-4\Todo-App\backend\*" -Destination . -Recurse
   ```

3. **Verify the structure**:
   ```
   todo-backend-deploy/
   ├── Dockerfile
   ├── requirements.txt
   ├── pyproject.toml
   ├── src/
   │   ├── main.py
   │   ├── db.py
   │   └── ...
   └── .dockerignore
   ```

### Option B: Use the Backend Folder Directly (If Using Git Subtree)

Alternatively, you can push just the backend folder using Git subtree or sparse checkout.

---

## Step 3: Initialize Git Repository

1. **Initialize Git** (if not already initialized):
   ```bash
   cd ~/todo-backend-deploy  # or your backend folder
   git init
   ```

2. **Add all files**:
   ```bash
   git add .
   git commit -m "Initial commit: FastAPI backend for Hugging Face Spaces"
   ```

---

## Step 4: Connect to Hugging Face Repository

1. **Add Hugging Face as remote**:
   ```bash
   git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   ```
   
   Replace `YOUR_USERNAME` and `YOUR_SPACE_NAME` with your actual values.

2. **Set up authentication**:
   - Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Create a new token with **Write** permissions
   - Copy the token

3. **Configure Git credentials** (choose one method):

   **Method 1: Use Git Credential Helper**:
   ```bash
   git config --global credential.helper store
   ```
   When you push, use your username and the token as password.

   **Method 2: Use Hugging Face CLI**:
   ```bash
   huggingface-cli login
   ```
   Enter your token when prompted.

   **Method 3: Embed in URL** (not recommended for security):
   ```bash
   git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   ```

---

## Step 5: Push Code to Hugging Face

1. **Push to main branch**:
   ```bash
   git branch -M main
   git push -u origin main
   ```

2. **Wait for build**:
   - Hugging Face will automatically detect the Dockerfile
   - Go to your Space page and click on the "Logs" tab to watch the build progress
   - Build typically takes 3-5 minutes

---

## Step 6: Configure Environment Variables

1. **Go to your Space settings**:
   - Navigate to your Space page: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`
   - Click on the **Settings** tab (gear icon)

2. **Add environment variables**:
   - Scroll down to **Repository secrets** section
   - Click **Add secret** for each variable:

   | Variable Name | Value | Description |
   |--------------|-------|-------------|
   | `DATABASE_URL` | `postgresql://...` | Your Neon PostgreSQL connection string |
   | `BETTER_AUTH_URL` | `https://your-frontend.vercel.app` | Your Better Auth frontend URL |
   | `CORS_ORIGINS` | `https://your-frontend.vercel.app,https://your-frontend-2.vercel.app` | Comma-separated allowed origins |
   | `DEBUG` | `false` | Set to `true` for debug logging (optional) |
   | `PORT` | `7860` | Port number (optional, defaults to 7860) |

3. **Save the secrets**:
   - After adding each secret, click **Save**
   - The Space will automatically rebuild with the new environment variables

---

## Step 7: Verify Deployment

1. **Check build logs**:
   - Go to the **Logs** tab in your Space
   - Look for messages like:
     ```
     Application startup complete.
     Uvicorn running on http://0.0.0.0:7860
     ```

2. **Test the health endpoint**:
   - Go to your Space URL: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health`
   - You should see: `{"status":"healthy"}`

3. **Check API documentation**:
   - Visit: `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs`
   - This should show the FastAPI Swagger UI

4. **Test an API endpoint**:
   ```bash
   curl https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health
   ```

---

## Step 8: Update CORS Settings (If Needed)

Your FastAPI app reads `CORS_ORIGINS` from environment variables. Make sure to include your frontend URL:

```
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend-alias.vercel.app
```

The Space URL is automatically included, so you don't need to add it.

---

## Troubleshooting

### Build Fails

**Error: "Module not found"**
- Ensure all dependencies are in `requirements.txt`
- Check that `pyproject.toml` is present if using it

**Error: "Port already in use"**
- The Dockerfile should use `${PORT:-7860}` which is correct
- Check that you're binding to `0.0.0.0`, not `127.0.0.1`

**Error: "Database connection failed"**
- Verify `DATABASE_URL` is correctly set in Space settings
- Check that your Neon database allows connections from Hugging Face IPs
- Ensure the connection string is complete and valid

### Application Won't Start

**Check logs**:
- Go to the **Logs** tab in your Space
- Look for error messages in red
- Common issues:
  - Missing environment variables
  - Database connection errors
  - Port binding issues

**Verify environment variables**:
- All required variables are set in Space settings
- Variable names match exactly (case-sensitive)
- No trailing spaces in values

### API Returns 404

**Check routes**:
- Verify the app is accessible at `/health`
- API routes should be at `/api/*`
- Check that `app.include_router(api_router, prefix="/api")` is in `main.py`

### CORS Errors from Frontend

**Update CORS_ORIGINS**:
- Add your frontend URL to `CORS_ORIGINS` environment variable
- Use comma-separated list for multiple origins
- Include both `http://localhost:3000` (for local dev) and production URLs

---

## Updating Your Deployment

Whenever you make changes to your code:

1. **Commit your changes**:
   ```bash
   cd ~/todo-backend-deploy  # or your backend folder
   git add .
   git commit -m "Update: description of changes"
   ```

2. **Push to Hugging Face**:
   ```bash
   git push origin main
   ```

3. **Monitor the build**:
   - Check the Logs tab to see the new build progress
   - The Space will automatically restart with your new code

---

## Space Configuration (Optional)

You can create a `README.md` file in your Space to document your API:

```markdown
---
title: Todo Backend API
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
sdk_version: 20.10.9
app_port: 7860
---

# Todo Backend API

FastAPI backend for the Todo App Phase II.

## API Documentation

Visit `/docs` for interactive API documentation.

## Endpoints

- `GET /health` - Health check
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create a task
- ...
```

Place this in your repository root (same directory as Dockerfile).

---

## Quick Reference

**Space URL Format**:
```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space
```

**API Base URL**:
```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api
```

**Health Check**:
```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health
```

**API Docs**:
```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs
```

---

## Next Steps

1. ✅ Backend deployed on Hugging Face Spaces
2. 🔄 Update your frontend to use the new API URL
3. 🔄 Test the integration between frontend and backend
4. 🔄 Monitor logs and performance

---

## Additional Resources

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Docker on Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Environment Variables in Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker#environment-variables)
