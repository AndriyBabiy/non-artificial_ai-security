"use client";

import UrlScanBox from "../components/UrlScanBox";
import ScanResult from "../components/ScanResult";
import { useState } from "react";

export default function Home() {
  const handleScan = (url: string) => {};

  return (
    <main className="hero-bg">
      <div className="center-container">
        <h1 className="hero-title">AI Injection Detector</h1>
        <p className="hero-subtitle">Check if a website is vulnerable to AI prompt injection attacks that could steal your information!</p>
        <div className="url-card">
          <UrlScanBox onScan={handleScan} />
        </div>
      </div>
    </main>
  );
}
