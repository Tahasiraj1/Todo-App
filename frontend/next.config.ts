// [Task]: T013 [From]: spec.md FR-001, FR-004
// Next.js configuration with standalone output for Docker deployment
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for smaller Docker images
  output: "standalone",
};

export default nextConfig;
