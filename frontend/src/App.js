import React, { useState } from 'react';
import { Layout, FileText, PieChart, Presentation, Send, CheckCircle, AlertCircle, Download } from 'lucide-react';
import axios from 'axios';

const API_BASE = "http://localhost:8000";

function App() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // Stocke le diagnostic et le plan PPT

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      // Appel à l'endpoint que nous avons créé dans le backend
      const response = await axios.post(`${API_BASE}/api/v1/ai/diagnose-financials/1/101`);
      setResult(response.data);
    } catch (error) {
      alert("Erreur de connexion au serveur Backend");
    }
    setLoading(false);
  };

  return (
    <div className="flex h-screen bg-slate-900 text-white font-sans">
      {/* SIDEBAR - Gestion des Projets (ISO 27001) */}
      <div className="w-64 bg-slate-800 p-4 flex flex-col border-r border-slate-700">
        <h1 className="text-xl font-bold mb-8 flex items-center gap-2">
          <Layout className="text-blue-400" /> AI Office Hub
        </h1>
        
        <div className="space-y-4">
          <p className="text-xs text-slate-400 uppercase font-semibold">Mes Projets</p>
          <div className="p-2 bg-blue-600 rounded-lg cursor-pointer flex items-center gap-2">
            <FileText size={16} /> Audit Financier Q3
          </div>
          <div className="p-2 hover:bg-slate-700 rounded-lg cursor-pointer flex items-center gap-2 text-slate-300">
            <FileText size={16} /> Rapport Annuel 2023
          </div>
        </div>

        <div className="mt-auto p-4 bg-slate-700 rounded-xl text-xs text-slate-300">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={14} className="text-green-400" /> SOC 2 Compliant
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle size={14} className="text-green-400" /> ISO 27001 Active
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-8">
          <h2 className="text-lg font-medium">Diagnostic Financier Intelligent</h2>
          <div className="flex gap-4">
            <span className="text-sm text-slate-400">Utilisateur: Admin_Finance</span>
          </div>
        </header>

        <div className="flex-1 p-6 overflow-auto flex gap-6">
          {/* Zone Chat & Diagnostic */}
          <div className="flex-1 flex flex-col gap-4">
            <div className="flex-1 bg-slate-800 rounded-2xl p-6 border border-slate-700 overflow-auto">
              {!result ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 italic">
                  <PieChart size={48} className="mb-4 opacity-20" />
                  <p>En attente de données pour analyse...</p>
                </div>
              ) : (
                <div className="space-y-6 animate-in fade-in duration-500">
                  <div className="bg-blue-900/30 border-l-4 border-blue-500 p-4 rounded">
                    <h3 className="font-bold text-blue-400 flex items-center gap-2">
                      <PieChart size={18} /> Diagnostic de l'IA
                    </h3>
                    <p className="mt-2 text-slate-200">{result.diagnostic.summary}</p>
                    <ul className="mt-2 list-disc list-inside text-sm text-slate-300">
                      {result.diagnostic.details && result.diagnostic.details.map((detail, idx) => (
                        <li key={idx}>{detail}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-red-900/20 border-l-4 border-red-500 p-4 rounded">
                    <h3 className="font-bold text-red-400 flex items-center gap-2">
                      <AlertCircle size={18} /> Alerte Critique
                    </h3>
                    <p className="mt-2 text-slate-200 italic">"{result.diagnostic.critical_alert}"</p>
                  </div>
                </div>
              )}
            </div>

            {/* Input Chat */}
            <div className="relative">
              <input 
                type="text" 
                className="w-full bg-slate-800 border border-slate-700 rounded-full px-6 py-4 pr-16 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Demandez à l'IA d'analyser un document..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
              <button 
                onClick={handleAnalyze}
                disabled={loading}
                className="absolute right-2 top-2 bg-blue-600 p-2 rounded-full hover:bg-blue-500 transition-all"
              >
                {loading ? <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-white"></div> : <Send size={20} />}
              </button>
            </div>
          </div>

          {/* ZONE ATELIER PPT (L'ORIENTATION) */}
          <div className="w-96 bg-slate-800 rounded-2xl border border-slate-700 flex flex-col">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h3 className="font-bold flex items-center gap-2"><Presentation size={18} /> Orientation PPT</h3>
              <button className="bg-green-600 p-2 rounded-lg text-xs flex items-center gap-1 hover:bg-green-500">
                <Download size={14} /> Export ODP
              </button>
            </div>
            
            <div className="p-4 space-y-4 overflow-auto">
              {!result ? (
                <p className="text-slate-500 text-center text-sm mt-10">Aucun plan généré</p>
              ) : (
                result.ppt_plan.map((slide, index) => (
                  <div key={index} className="bg-slate-700 p-3 rounded-lg border border-slate-600 hover:border-blue-400 transition-all cursor-pointer">
                    <p className="text-xs font-bold text-blue-400 uppercase">Slide {slide.slide}</p>
                    <p className="font-semibold text-sm mb-1">{slide.title}</p>
                    <p className="text-xs text-slate-400">{slide.content}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;