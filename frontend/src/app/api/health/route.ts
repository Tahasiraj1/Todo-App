// [Task]: T017 [From]: spec.md FR-005, data-model.md §2
// Health check endpoint for Kubernetes liveness and readiness probes

import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json(
    {
      status: "ok",
      timestamp: new Date().toISOString(),
      service: "todo-frontend",
    },
    { status: 200 }
  );
}
