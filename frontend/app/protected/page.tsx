"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { refreshCache } from "@/lib/api";
import { useState } from "react";

export default function ProtectedPage() {
  const router = useRouter();
  const { token, isAuthenticated, logout } = useAuth();
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  const handleRefreshCache = async () => {
    if (!token) return;
    
    setIsLoading(true);
    setMessage(null);
    try {
      const response = await refreshCache(token);
      if (response.error) {
        setMessage(`Error: ${response.error}`);
      } else if (response.data) {
        setMessage(`Cache refreshed! ${response.data.repos_cached} repos cached.`);
      }
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to refresh cache");
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-900 border border-gray-800 rounded-lg p-8">
        <h1 className="text-2xl font-bold mb-6 text-white">Protected Page</h1>
        <p className="text-gray-400 mb-6">
          This is a protected page that requires authentication. You are logged in.
        </p>
        <div className="space-y-4">
          <button
            onClick={handleRefreshCache}
            disabled={isLoading}
            className="w-full px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded transition-colors disabled:opacity-50"
          >
            {isLoading ? "Refreshing..." : "Refresh Cache"}
          </button>
          {message && (
            <div className={`text-sm ${message.startsWith("Error") ? "text-red-400" : "text-green-400"}`}>
              {message}
            </div>
          )}
          <button
            onClick={() => {
              logout();
              router.push("/");
            }}
            className="w-full px-4 py-2 bg-red-800 hover:bg-red-700 text-white rounded transition-colors"
          >
            Logout
          </button>
          <a
            href="/"
            className="block text-center text-gray-300 hover:text-white transition-colors"
          >
            Back to Portfolio
          </a>
        </div>
      </div>
    </div>
  );
}
