/**
 * Health Check API Route for Kubernetes Probes
 * Used by Docker healthcheck and Kubernetes liveness/readiness probes
 */

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      service: 'todo-frontend',
      timestamp: new Date().toISOString(),
    },
    { status: 200 }
  );
}
