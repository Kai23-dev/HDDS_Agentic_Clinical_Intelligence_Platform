/*
  HDDS Clinical Intelligence Platform - Main App
  ================================================
  Manages the 3 main views:
    1. Upload  -> User uploads documents or picks sample data
    2. Processing -> Shows agent pipeline progress
    3. Results -> Displays the AI-generated clinical insights
*/
import { useState } from 'react';
import axios from 'axios';
import Header from './components/Header';
import UploadView from './components/UploadView';
import ProcessingView from './components/ProcessingView';
import ResultsView from './components/ResultsView';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  // 'upload' | 'processing' | 'results' | 'error'
  const [view, setView] = useState('upload');
  const [resultsData, setResultsData] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleProcessStart = async (input) => {
    setView('processing');
    setErrorMsg('');

    try {
      let response;

      if (input.type === 'sample') {
        // Use sample data endpoint
        response = await axios.post(`${API_URL}/api/run-sample`);
      } else if (input.type === 'upload' && input.file) {
        // Upload file
        const formData = new FormData();
        formData.append('file', input.file);
        response = await axios.post(`${API_URL}/api/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      if (response && response.data) {
        setResultsData(response.data);
        setView('results');
      }
    } catch (err) {
      console.error('API Error:', err);
      const detail = err.response?.data?.detail || err.message || 'Something went wrong';
      setErrorMsg(detail);
      setView('error');
    }
  };

  const handleBack = () => {
    setView('upload');
    setResultsData(null);
  };

  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      <Header />

      {view === 'upload' && (
        <UploadView onProcessStart={handleProcessStart} />
      )}

      {view === 'processing' && (
        <ProcessingView />
      )}

      {view === 'results' && resultsData && (
        <ResultsView data={resultsData} onBack={handleBack} />
      )}

      {view === 'error' && (
        <div className="max-w-lg mx-auto px-6 py-16 text-center">
          <div className="bg-white rounded-lg border border-red-200 p-8">
            <div className="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">!</span>
            </div>
            <h2 className="text-xl font-bold text-[#2e2e38] mb-2">Something went wrong</h2>
            <p className="text-sm text-gray-500 mb-4">{errorMsg}</p>
            <p className="text-xs text-gray-400 mb-6">
              Make sure the FastAPI server is running: <code className="bg-gray-100 px-1 py-0.5 rounded">python api.py</code>
            </p>
            <button
              onClick={handleBack}
              className="px-5 py-2.5 bg-[#ffe600] text-[#2e2e38] rounded-lg font-semibold text-sm hover:bg-[#e6cf00]"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
