import React, { useState, useEffect } from 'react';
import { Toaster } from './components/ui/sonner';
import { Button } from './components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { NewsInput } from './components/NewsInput';
import { ResultDisplay } from './components/ResultDisplay';
import { HistoryPanel } from './components/HistoryPanel';
import { FeedbackDialog } from './components/FeedbackDialog';
import { Dashboard } from './components/Dashboard';
import { AboutPage } from './components/AboutPage';
import { predictFakeNews, PredictionResult } from '../services/api';
import { Moon, Sun, Shield, Activity, Info, History } from 'lucide-react';

// Simple theme context without next-themes
const ThemeContext = React.createContext<{
  theme: string;
  setTheme: (theme: string) => void;
}>({
  theme: 'light',
  setTheme: () => {},
});

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.className = savedTheme;
  }, []);

  const updateTheme = (newTheme: string) => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.className = newTheme;
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme: updateTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

function useTheme() {
  return React.useContext(ThemeContext);
}

function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <Button variant="ghost" size="icon" disabled />;
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      {theme === 'dark' ? (
        <Sun className="size-5" />
      ) : (
        <Moon className="size-5" />
      )}
    </Button>
  );
}

function AppContent() {
  const [currentResult, setCurrentResult] = useState<PredictionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('analyze');
  const [historyKey, setHistoryKey] = useState(0);

  const handleAnalyze = async (text: string, url?: string, isFileUpload?: boolean) => {
    setIsAnalyzing(true);
    setCurrentResult(null);
    
    try {
      // Determine analysis type
      const analysisType = url ? 'url' : (isFileUpload ? 'file' : 'text');
      
      const result = await predictFakeNews(text, url, analysisType);
      
      // Add analysis type to the result
      const enhancedResult = {
        ...result,
        analysis_type: analysisType
      };
      
      setCurrentResult(enhancedResult);
      
      // Save to localStorage as backup (the backend also stores it)
      const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
      history.unshift(enhancedResult);
      // Keep only last 50 predictions in localStorage
      if (history.length > 50) {
        history.pop();
      }
      localStorage.setItem('predictionHistory', JSON.stringify(history));
      
      // Force history panel to reload
      setHistoryKey(prev => prev + 1);
    } catch (error) {
      console.error('Analysis failed:', error);
      // Show user-friendly error message
      setCurrentResult({
        id: 'error-' + Date.now(),
        prediction: 'inconclusive',
        confidence: 0,
        explanation: error instanceof Error ? error.message : 'Analysis failed. Please check if the backend server is running.',
        factors: [],
        sources: [],
        timestamp: new Date().toISOString(),
        inputText: text || 'URL analysis failed',
        inputUrl: url,
        modelVersion: 'unknown',
        analysis_type: url ? 'url' : (isFileUpload ? 'file' : 'text')
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleViewHistoryResult = (result: PredictionResult) => {
    setCurrentResult(result);
    setActiveTab('analyze');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center size-10 rounded-lg bg-primary text-primary-foreground">
                <Shield className="size-6" />
              </div>
              <div>
                <h1 className="text-xl">Fake News Detector</h1>
                <p className="text-sm text-muted-foreground">AI-Powered Misinformation Analysis</p>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="analyze">
              <Shield className="mr-2 size-4" />
              Analyze
            </TabsTrigger>
            <TabsTrigger value="history">
              <History className="mr-2 size-4" />
              History
            </TabsTrigger>
            <TabsTrigger value="dashboard">
              <Activity className="mr-2 size-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="about">
              <Info className="mr-2 size-4" />
              About
            </TabsTrigger>
          </TabsList>

          <TabsContent value="analyze" className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-2">
              <div>
                <NewsInput onAnalyze={handleAnalyze} isLoading={isAnalyzing} />
              </div>
              <div>
                {currentResult ? (
                  <ResultDisplay
                    result={currentResult}
                    onFeedback={() => setFeedbackDialogOpen(true)}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full min-h-[400px] border-2 border-dashed rounded-lg">
                    <div className="text-center space-y-2 p-6">
                      <Shield className="size-12 mx-auto text-muted-foreground" />
                      <h3 className="text-xl">No Analysis Yet</h3>
                      <p className="text-muted-foreground max-w-sm">
                        Enter some text, paste a URL, or upload a file to get started with fake news detection
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="history">
            <HistoryPanel key={historyKey} onViewResult={handleViewHistoryResult} />
          </TabsContent>

          <TabsContent value="dashboard">
            <Dashboard />
          </TabsContent>

          <TabsContent value="about">
            <AboutPage />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p>
              This is a demonstration of AI-powered fake news detection. Always verify important information through multiple trusted sources.
            </p>
            <p className="mt-2">
              Built with React, TypeScript, and Machine Learning • Not for collecting PII or sensitive data
            </p>
          </div>
        </div>
      </footer>

      {/* Feedback Dialog */}
      {currentResult && (
        <FeedbackDialog
          open={feedbackDialogOpen}
          onOpenChange={setFeedbackDialogOpen}
          predictionId={currentResult.timestamp}
          currentPrediction={currentResult.prediction}
        />
      )}

      <Toaster />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
