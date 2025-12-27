import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Clock, RefreshCw } from 'lucide-react';

interface SimpleHistoryPanelProps {
  onViewResult?: (result: any) => void;
}

export function SimpleHistoryPanel({ onViewResult }: SimpleHistoryPanelProps) {
  const [history, setHistory] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Check localStorage first
      const stored = localStorage.getItem('predictionHistory');
      if (stored) {
        const localHistory = JSON.parse(stored);
        setHistory(localHistory);
        console.log('Loaded history from localStorage:', localHistory.length, 'items');
      } else {
        setHistory([]);
        console.log('No history found in localStorage');
      }
    } catch (error) {
      console.error('Error loading history:', error);
      setError('Failed to load history');
      setHistory([]);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Analysis History</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="size-8 animate-spin" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Analysis History</CardTitle>
          <CardDescription>Error loading history</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={loadHistory} variant="outline">
              <RefreshCw className="mr-2 size-4" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Analysis History</CardTitle>
          <CardDescription>Your recent predictions will appear here</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Clock className="size-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No analysis history yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Start analyzing news content to build your history
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Analysis History</CardTitle>
        <CardDescription>{history.length} predictions found</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {history.slice(0, 10).map((item, index) => (
            <div key={item.id || index} className="p-4 border rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">
                    Prediction: {item.prediction || 'Unknown'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Confidence: {item.confidence || 0}%
                  </p>
                  <p className="text-sm mt-2">
                    {item.inputText ? 
                      (item.inputText.length > 100 ? 
                        item.inputText.substring(0, 100) + '...' : 
                        item.inputText
                      ) : 
                      'No text'
                    }
                  </p>
                </div>
                {onViewResult && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => onViewResult(item)}
                  >
                    View
                  </Button>
                )}
              </div>
            </div>
          ))}
          
          {history.length > 10 && (
            <p className="text-center text-sm text-muted-foreground">
              Showing first 10 of {history.length} predictions
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}