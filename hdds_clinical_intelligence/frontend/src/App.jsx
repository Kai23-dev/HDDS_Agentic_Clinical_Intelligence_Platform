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
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import UploadView from './components/UploadView';
import ProcessingView from './components/ProcessingView';
import ResultsView from './components/ResultsView';
import LoginView from './components/LoginView';
import { API_URL } from './config';

function App() {
  // 'login' | 'upload' | 'processing' | 'results' | 'error'
  const [view, setView] = useState('login');
  const [resultsData, setResultsData] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [authData, setAuthData] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogin = (data) => {
    setAuthData(data);
    setView('upload');
  };

  const handleLogout = () => {
    setAuthData(null);
    setResultsData(null);
    setView('login');
  };

  const handleNavigate = (key) => {
    setSidebarOpen(false);
    if (key === 'results' && resultsData) {
      setView('results');
    } else {
      setView('upload');
    }
  };

  const handleProcessStart = async (input) => {
    setView('processing');
    setErrorMsg('');

    try {
      let response;

      const headers = {
        'Authorization': `Bearer ${authData?.access_token}`
      };

      if (input.type === 'sample') {
        response = await axios.post(`${API_URL}/api/run-sample`, null, { headers });
      } else if (input.type === 'synthea') {
        response = await axios.post(`${API_URL}/api/load-synthea`, null, { headers });
      } else if (input.type === 'upload' && input.file) {
        const formData = new FormData();
        formData.append('file', input.file);
        response = await axios.post(`${API_URL}/api/upload`, formData, {
          headers: { ...headers, 'Content-Type': 'multipart/form-data' },
        });
      } else if (input.type === 'dictate' && input.file) {
        const formData = new FormData();
        formData.append('file', input.file);
        response = await axios.post(`${API_URL}/api/dictate`, formData, {
          headers: { ...headers, 'Content-Type': 'multipart/form-data' },
        });
        if (response.data && response.data.metadata && response.data.metadata.transcript) {
          window.alert("Audio Transcription Complete (Azure AI Speech):\n\n" + response.data.metadata.transcript);
        }
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

  if (view === 'login') {
    return <LoginView onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-ey-light font-sans text-ey-dark flex">
      <Sidebar
        view={view === 'results' ? 'results' : 'upload'}
        onNavigate={handleNavigate}
        mobileOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex-1 min-w-0 flex flex-col">
        <TopBar
          view={view}
          onMenuClick={() => setSidebarOpen(true)}
          userName={authData?.name}
          role={authData?.role}
          onLogout={handleLogout}
        />

        <main className="flex-1 min-w-0">
          {view === 'upload' && (
            <UploadView onProcessStart={handleProcessStart} />
          )}

          {view === 'processing' && (
            <ProcessingView />
          )}

          {view === 'results' && resultsData && (
            <ResultsView
              data={resultsData}
              onBack={handleBack}
              token={authData?.access_token}
              role={authData?.role}
            />
          )}

          {view === 'error' && (
            <div className="max-w-lg mx-auto px-6 py-16 text-center animate-fade-in">
              <div className="glass-panel rounded-2xl p-8 border-red-200/50 shadow-xl shadow-red-900/5">
                <div className="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm border border-red-100">
                  <span className="text-3xl font-light">!</span>
                </div>
                <h2 className="text-2xl font-bold text-ey-dark mb-3">Something went wrong</h2>
                <p className="text-base text-gray-600 mb-6 font-medium">{errorMsg}</p>
                <p className="text-xs text-gray-400 mb-8 px-4">
                  Make sure the FastAPI server is running: <code className="bg-gray-100 text-gray-700 px-2 py-1 rounded border border-gray-200">python api.py</code>
                </p>
                <button
                  onClick={handleBack}
                  className="premium-button px-8 py-3 bg-ey-yellow text-ey-dark rounded-xl font-bold text-sm shadow-md"
                >
                  Try Again
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
