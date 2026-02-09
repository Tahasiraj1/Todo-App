#!/bin/bash
helm upgrade --install todo-chatbot ./k8s/helm/todo-chatbot \
  -f k8s/helm/todo-chatbot/values-oke.yaml \
  --namespace todo-app \
  --create-namespace \
  --set secrets.databaseUrl="$DB_URL" \
  --set secrets.openaiApiKey="$OPENAI_KEY" \
  --set secrets.betterAuthSecret="$AUTH_SECRET" \
  --set secrets.geminiApiKey="$GEMINI_KEY" \
  --wait --timeout 5m
