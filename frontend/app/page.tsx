import ScanForm from "../components/ScanForm";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Website Security Scanner
            </h1>
            <p className="text-lg text-gray-600">
              AI-powered security analysis for your websites
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-xl p-8">
            <ScanForm />
          </div>

          <div className="mt-8 text-center text-sm text-gray-500">
            <p>
              Powered by AI • Scans SSL, vulnerabilities, and security headers
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
