import { useState } from 'react';
import { Toaster } from './components/ui/sonner';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { NewsInput } from './components/NewsInput';
import { ResultDisplay } from './components/ResultDisplay';
import { HistoryPanel } from './components/HistoryPanel';
import { FeedbackDialog } from './components/FeedbackDialog';
import { Dashboard } from './components/Dashboard';
import { AboutPage } from './components/AboutPage';
import { predictFakeNews, PredictionResult } from '../services/api';
import { Shield, Activity, Info, History } from 'lucide-react';

export default function App() {
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [refreshHistory, setRefreshHistory] = useState(0);

  const handleAnalyze = async (text: string, analysisType: 'text' | 'url' | 'file' = 'text') => {
    setIsLoading(true);
    try {
      const prediction = await predictFakeNews(text, analysisType);
      setResult(prediction);
      setRefreshHistory(prev => prev + 1);
    } catch (error) {
      console.error('Analysis failed:', error);
      setResult({
        prediction: 'ERROR',
        confidence: 0,
        explanation: 'Analysis failed. Please try again.',
        features: {}
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">
              Fake News Detection System
            </h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Advanced AI-powered system to detect fake news using machine learning and linguistic analysis
          </p>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="analyze" className="w-full max-w-6xl mx-auto">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="analyze" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Analyze
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <History className="h-4 w-4" />
              History
            </TabsTrigger>
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="about" className="flex items-center gap-2">
              <Info className="h-4 w-4" />
              About
            </TabsTrigger>
          </TabsList>

          <TabsContent value="analyze" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <NewsInput onAnalyze={handleAnalyze} isLoading={isLoading} />
              </div>
              <div>
                <ResultDisplay 
                  result={result} 
                  isLoading={isLoading}
                  onFeedback={() => setShowFeedback(true)}
                />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="history">
            <HistoryPanel refreshTrigger={refreshHistory} />
          </TabsContent>

          <TabsContent value="dashboard">
            <Dashboard refreshTrigger={refreshHistory} />
          </TabsContent>

          <TabsContent value="about">
            <AboutPage />
          </TabsContent>
        </Tabs>

        {/* Feedback Dialog */}
        <FeedbackDialog 
          open={showFeedback}
          onOpenChange={setShowFeedback}
          result={result}
        />

        {/* Toast Notifications */}
        <Toaster />
      </div>
    </div>
  );
}