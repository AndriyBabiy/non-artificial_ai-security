"use client";

import { useState } from "react";
import axios from "axios";

interface ScanResult {
  results: {
    ssl?: any;
    vulnerabilities?: any;
    security_headers?: any;
  };
  summary: string;
}

export default function ScanForm() {
  const [url, setUrl] = useState("");
  const [prompt, setPrompt] = useState(
    "Check for security breaches and vulnerabilities"
  );
  const [result, setResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const validateUrl = (url: string) => {
    try {
      new URL(url.startsWith("http") ? url : `https://${url}`);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim()) {
      setError("Please enter a URL");
      return;
    }

    if (!validateUrl(url)) {
      setError("Please enter a valid URL");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const backendUrl =
        process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
      const response = await axios.post(
        `${backendUrl}/scan`,
        {
          url: url.replace(/^https?:\/\//, ""),
          prompt,
        },
        {
          timeout: 60000, // 60 second timeout
        }
      );
      setResult(response.data);
    } catch (err: any) {
      console.error("Scan error:", err);
      if (err.code === "ECONNABORTED") {
        setError("Request timed out. The scan is taking longer than expected.");
      } else if (err.response?.data?.detail) {
        setError(`Error: ${err.response.data.detail}`);
      } else {
        setError("An error occurred during the scan. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="url"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Website URL
          </label>
          <input
            id="url"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="example.com or https://example.com"
            className="input-field"
            disabled={loading}
          />
        </div>

        <div>
          <label
            htmlFor="prompt"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Scan Instructions
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe what you want to check for..."
            rows={3}
            className="input-field resize-none"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          className={`btn-primary w-full ${
            loading ? "opacity-50 cursor-not-allowed" : ""
          }`}
          disabled={loading}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Scanning...
            </div>
          ) : (
            "Start Security Scan"
          )}
        </button>
      </form>

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {result && (
        <div className="mt-8 space-y-6">
          <div className="border-t pt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Scan Results
            </h2>

            {/* AI Summary */}
            <div className="card bg-blue-50 border border-blue-200 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">
                AI Analysis Summary
              </h3>
              <p className="text-blue-800 whitespace-pre-wrap">
                {result.summary}
              </p>
            </div>

            {/* Detailed Results */}
            <div className="grid gap-4">
              {result.results.ssl && (
                <div className="card">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    SSL Certificate
                  </h3>
                  <pre className="text-sm text-gray-700 bg-gray-50 p-3 rounded overflow-x-auto">
                    {JSON.stringify(result.results.ssl, null, 2)}
                  </pre>
                </div>
              )}

              {result.results.vulnerabilities && (
                <div className="card">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Vulnerabilities
                  </h3>
                  <pre className="text-sm text-gray-700 bg-gray-50 p-3 rounded overflow-x-auto">
                    {JSON.stringify(result.results.vulnerabilities, null, 2)}
                  </pre>
                </div>
              )}

              {result.results.security_headers && (
                <div className="card">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Security Headers
                  </h3>
                  <pre className="text-sm text-gray-700 bg-gray-50 p-3 rounded overflow-x-auto">
                    {JSON.stringify(result.results.security_headers, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
