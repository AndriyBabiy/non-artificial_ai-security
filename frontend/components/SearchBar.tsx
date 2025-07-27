"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";

interface SearchBarProps {
  onScan: (url: string, prompt: string) => void;
  isLoading: boolean;
}

export default function SearchBar({ onScan, isLoading }: SearchBarProps) {
  const [url, setUrl] = useState("");
  const [prompt, setPrompt] = useState(
    "Check for security breaches and vulnerabilities"
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    const cleanUrl = url.replace(/^https?:\/\//, "");
    onScan(cleanUrl, prompt);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto mb-8">
      <CardHeader>
        <CardTitle>Website Security Scanner</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="url">Website URL</Label>
            <input
              id="url"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="example.com"
              className="w-full p-3 border rounded-md"
              disabled={isLoading}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="prompt">Scan Instructions</Label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              className="w-full p-3 border rounded-md"
              disabled={isLoading}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading || !url.trim()}
          >
            {isLoading ? "Scanning..." : "Start Security Scan"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
