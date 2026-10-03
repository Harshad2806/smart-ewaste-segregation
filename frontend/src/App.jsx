import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import AnalyzePage from './pages/AnalyzePage';
import DashboardPage from './pages/DashboardPage';
import CameraPage from './pages/CameraPage';
import { useHistory } from './hooks/useHistory';

export default function App() {
  const { history, addEntry, clearHistory, stats } = useHistory();

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<AnalyzePage onResult={addEntry} />} />
          <Route
            path="/dashboard"
            element={
              <DashboardPage
                history={history}
                stats={stats}
                onClear={clearHistory}
              />
            }
          />
          <Route path="/camera" element={<CameraPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/40 py-4 text-center">
        <p className="text-xs text-slate-700">
          Smart E-Waste Segregation System · SIH Project · AI-Powered Recycling Intelligence
        </p>
      </footer>
    </div>
  );
}
