# DataChat Deployment Guide

## Backend: Render

1. Push the repository to GitHub.
2. In Render, create a new Web Service.
3. Connect the GitHub repository.
4. Set the Root Directory to `datachat/backend`.
5. Set the Runtime to Python.
6. Set the Build Command:

```bash
pip install -r requirements.txt
```

7. Set the Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

8. Add environment variables:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
FRONTEND_URL=https://your-datachat-frontend.vercel.app
CORS_ORIGINS=https://your-datachat-frontend.vercel.app
```

9. Deploy the service.
10. Confirm the health endpoint works:

```text
https://your-render-service.onrender.com/health
```

Expected response:

```json
{"status":"Backend running"}
```

## Frontend: Vercel

1. In Vercel, import the same GitHub repository.
2. Set the Root Directory to `datachat/frontend`.
3. Keep the default Next.js build settings.
4. Add this environment variable:

```env
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com
```

5. Deploy the frontend.
6. Copy the Vercel production URL.
7. Update the Render backend environment variables:

```env
FRONTEND_URL=https://your-datachat-frontend.vercel.app
CORS_ORIGINS=https://your-datachat-frontend.vercel.app
```

8. Redeploy the Render backend so the production CORS domain is active.

## Final Verification

After both deployments are live:

1. Open the Vercel frontend URL.
2. Confirm backend status shows `Backend running`.
3. Upload a CSV file.
4. Ask `Show histogram of marks`.
5. Ask `Average marks by class`.
6. Confirm visual analysis renders in the chat.

The public DataChat app should support CSV upload, natural-language queries, and visual analysis.
