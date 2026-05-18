import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@hdm/db", "@hdm/types"],
};

export default nextConfig;
