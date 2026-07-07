/*
  UploadView - The main landing/upload screen.
  Users can upload their medical documents (PDF/JSON)
  or run the pipeline on sample data.
*/
import { useState, useRef } from 'react';
import { Upload, FileText, Database, ArrowRight, AlertTriangle, Mic } from 'lucide-react';

export default function UploadView({ onProcessStart }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const audioInputRef = useRef(null);

  const handleAudioSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      onProcessStart({ type: 'dictate', file });
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) validateAndSet(file);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) validateAndSet(file);
  };

  const validateAndSet = (file) => {
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'pdf' && ext !== 'zip') {
      setError('Please upload a .pdf or .zip file only');
      return;
    }
    setError(null);
    setSelectedFile(file);
  };

  const handleUpload = () => {
    if (selectedFile) {
      onProcessStart({ type: 'upload', file: selectedFile });
    }
  };

  const handleSampleData = () => {
    onProcessStart({ type: 'sample' });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
      {/* Intro section */}
      <div className="text-center mb-10">
        <h2 className="text-2xl sm:text-3xl font-bold text-ey-dark mb-3">
          Upload Patient Documents
        </h2>
        <p className="text-gray-500 max-w-xl mx-auto text-sm sm:text-base">
          Upload hospital discharge summaries, lab results, medication lists, or
          medical history documents. Our AI agents will extract and analyze the
          data to generate clinical insights.
        </p>
      </div>

      {/* Architecture flow diagram */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-8 result-card">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          How It Works
        </h3>
        <div className="flex items-center justify-between gap-2 text-center">
          <div className="flex-1">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <Upload className="w-5 h-5 text-gray-600" />
            </div>
            <p className="text-xs font-medium text-gray-600">Upload Documents</p>
            <p className="text-[10px] text-gray-400 mt-0.5">PDF or ZIP bundle</p>
          </div>
          <ArrowRight className="w-4 h-4 text-gray-300 flex-shrink-0" />
          <div className="flex-1">
            <div className="w-12 h-12 bg-ey-yellow/20 rounded-full flex items-center justify-center mx-auto mb-2">
              <Database className="w-5 h-5 text-[#b8a800]" />
            </div>
            <p className="text-xs font-medium text-gray-600">AI Extraction</p>
            <p className="text-[10px] text-gray-400 mt-0.5">Harmonization</p>
          </div>
          <ArrowRight className="w-4 h-4 text-gray-300 flex-shrink-0" />
          <div className="flex-1">
            <div className="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-2">
              <FileText className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-xs font-medium text-gray-600">Clinical Insights</p>
            <p className="text-[10px] text-gray-400 mt-0.5">Risk, Recs, Detection</p>
          </div>
        </div>
      </div>

      {/* Upload area */}
      <div
        className={`upload-zone rounded-xl p-8 sm:p-10 text-center cursor-pointer mb-6 ${dragOver ? 'dragging' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".pdf,.zip"
          className="hidden"
        />

        {selectedFile ? (
          <div>
            <FileText className="w-12 h-12 text-green-500 mx-auto mb-3" />
            <p className="font-semibold text-ey-dark">{selectedFile.name}</p>
            <p className="text-sm text-gray-400 mt-1">
              {(selectedFile.size / 1024).toFixed(1)} KB - Ready to process
            </p>
          </div>
        ) : (
          <div>
            <Upload className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="font-medium text-gray-500">
              Drag & drop your patient document here
            </p>
            <p className="text-sm text-gray-400 mt-1">
              Supports .PDF or .ZIP (Multi-document bundles)
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-500 text-sm mb-4 justify-center">
          <AlertTriangle className="w-4 h-4" /> {error}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          onClick={handleUpload}
          disabled={!selectedFile}
          className={`premium-button px-6 py-3 rounded-xl font-semibold text-sm flex items-center gap-2 justify-center ${
            selectedFile
              ? 'bg-ey-yellow text-ey-dark hover:bg-[#e6cf00] shadow-sm'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          <ArrowRight className="w-4 h-4" /> Process Uploaded File
        </button>

        <button
          onClick={handleSampleData}
          className="premium-button px-6 py-3 rounded-xl font-semibold text-sm border border-gray-300 bg-white text-gray-600 hover:bg-gray-50 flex items-center gap-2 justify-center"
        >
          <Database className="w-4 h-4" /> Use Sample Data
        </button>

        <button
          onClick={() => onProcessStart({ type: 'synthea' })}
          className="premium-button px-6 py-3 rounded-xl font-semibold text-sm border border-gray-300 bg-white text-blue-600 hover:bg-blue-50 flex items-center gap-2 justify-center"
        >
          <Database className="w-4 h-4" /> Load Synthea Dataset
        </button>

        <button
          onClick={() => audioInputRef.current?.click()}
          className="premium-button px-6 py-3 rounded-xl font-semibold text-sm border border-gray-300 bg-white text-purple-600 hover:bg-purple-50 flex items-center gap-2 justify-center"
        >
          <Mic className="w-4 h-4" /> Upload Audio Dictation
        </button>
        <input
          type="file"
          ref={audioInputRef}
          onChange={handleAudioSelect}
          accept=".wav,.mp3"
          className="hidden"
        />
      </div>

      {/* Disclaimer */}
      <div className="mt-10 bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
        <p className="text-xs text-amber-700">
          <strong>Disclaimer:</strong> This is a prototype using synthetic data only.
          All outputs are for clinician review purposes and do not constitute a medical diagnosis.
        </p>
      </div>
    </div>
  );
}
