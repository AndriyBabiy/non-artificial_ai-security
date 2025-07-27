"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface LoadingStepsProps {
  url: string;
}

const scanSteps = [
  {
    id: 1,
    name: "Initializing scan",
    description: "Preparing security analysis",
  },
  {
    id: 2,
    name: "SSL Certificate Check",
    description: "Validating certificate and chain",
  },
  {
    id: 3,
    name: "Vulnerability Scanning",
    description: "Checking for common vulnerabilities",
  },
  {
    id: 4,
    name: "Security Headers Analysis",
    description: "Analyzing HTTP security headers",
  },
  {
    id: 5,
    name: "AI Analysis",
    description: "Generating comprehensive security report",
  },
];

export default function LoadingSteps({ url }: LoadingStepsProps) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < scanSteps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="w-full max-w-2xl mx-auto mb-8">
      <CardHeader>
        <CardTitle>Scanning {url}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {scanSteps.map((step, index) => {
            const isCompleted = index < currentStep;
            const isActive = index === currentStep;

            return (
              <div
                key={step.id}
                className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                  isActive ? "bg-blue-50 border border-blue-200" : ""
                }`}
              >
                <div className="flex-shrink-0">
                  {isCompleted ? (
                    <span className="text-green-500">✓</span>
                  ) : isActive ? (
                    <span className="text-blue-500">⟳</span>
                  ) : (
                    <span className="text-gray-400">○</span>
                  )}
                </div>
                <div className="flex-1">
                  <div
                    className={`font-medium ${
                      isCompleted
                        ? "text-green-700"
                        : isActive
                        ? "text-blue-700"
                        : "text-gray-500"
                    }`}
                  >
                    {step.name}
                  </div>
                  <div className="text-sm text-gray-500">
                    {step.description}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
