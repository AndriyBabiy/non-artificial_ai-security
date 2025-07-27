"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ScanResult {
  results: {
    ssl?: any;
    vulnerabilities?: any;
    security_headers?: any;
  };
  summary: string;
}

interface SecurityResultsProps {
  result: ScanResult;
  url: string;
}

export default function SecurityResults({ result, url }: SecurityResultsProps) {
  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* AI Summary */}
      <Card>
        <CardHeader>
          <CardTitle>🤖 AI Security Analysis for {url}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-blue-50 p-4 rounded-lg border">
            <pre className="whitespace-pre-wrap text-sm text-blue-900">
              {result.summary}
            </pre>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Results */}
      <div className="grid gap-4">
        {result.results.ssl && (
          <Card>
            <CardHeader>
              <CardTitle>🔒 SSL Certificate</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-sm bg-gray-50 p-3 rounded overflow-x-auto">
                {JSON.stringify(result.results.ssl, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}

        {result.results.vulnerabilities && (
          <Card>
            <CardHeader>
              <CardTitle>🛡️ Vulnerabilities</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-sm bg-gray-50 p-3 rounded overflow-x-auto">
                {JSON.stringify(result.results.vulnerabilities, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}

        {result.results.security_headers && (
          <Card>
            <CardHeader>
              <CardTitle>📋 Security Headers</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="text-sm bg-gray-50 p-3 rounded overflow-x-auto">
                {JSON.stringify(result.results.security_headers, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
