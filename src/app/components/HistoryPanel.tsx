import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { Clock, Trash2, Eye, RefreshCw, Server } from 'lucide-react';
import { PredictionResult, getPredictionHistory } from '../../services/api';

interface HistoryPanelProps {
  onViewResult: (result: PredictionResult) => void;
}

export function HistoryPanel({ onViewResult }: HistoryPanelProps) {
  const [history, setHistory] = useState<PredictionResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [filterType, setFilterType] = useState<'all' | 'text' | 'url' | 'file'>('all');

  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      return date.toLocaleString();
    } catch (error) {
      return 'Invalid date';
    }
  };

  const getAnalysisType = (item: PredictionResult): 'text' | 'url' | 'file' => {
    if (item.analysis_type) return item.analysis_type as 'text' | 'url' | 'file';
    if (item.inputUrl || item.input_url) return 'url';
    return 'text';
  };

  const filteredHistory = history.filter(item => {
    if (filterType === 'all') return true;
    return getAnalysisType(item) === filterType;
  });

  const getTypeStats = () => {
    const textCount = history.filter(item => getAnalysisType(item) === 'text').length;
    const urlCount = history.filter(item => getAnalysisType(item) === 'url').length;
    const fileCount = history.filter(item => getAnalysisType(item) === 'file').length;
    return { textCount, urlCount, fileCount };
  };

  useEffect(() => {
    const initializeHistory = async () => {
      try {
        // Load from localStorage immediately for fast display
        const stored = localStorage.getItem('predictionHistory');
        if (stored) {
          const localHistory = JSON.parse(stored);
          setHistory(localHistory.slice(0, 20)); // Show first 20 immediately
          setTotal(localHistory.length);
        }
        
        // Then try to load from backend
        await loadHistory();
      } catch (error) {
        console.error('Error in HistoryPanel useEffect:', error);
        setError('Failed to load history');
        setIsLoading(false);
      }
    };

    initializeHistory();
  }, []);

  const loadHistory = async (pageNum = 1, append = false) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Try backend first with shorter timeout
      const limit = 20;
      const offset = (pageNum - 1) * limit;
      
      const response = await getPredictionHistory(limit, offset);
      
      if (append) {
        setHistory(prev => [...prev, ...response.predictions]);
      } else {
        setHistory(response.predictions);
      }
      
      setTotal(response.total);
      setPage(pageNum);
      setHasMore(response.predictions.length === limit && (offset + limit) < response.total);
      
      // Clear error if successful
      setError(null);
      
    } catch (error) {
      console.warn('Backend history failed, using localStorage:', error);
      
      // Quick fallback to localStorage
      const stored = localStorage.getItem('predictionHistory');
      if (stored) {
        try {
          const localHistory = JSON.parse(stored);
          const startIndex = (pageNum - 1) * 20;
          const endIndex = startIndex + 20;
          const pageData = localHistory.slice(startIndex, endIndex);
          
          if (append) {
            setHistory(prev => [...prev, ...pageData]);
          } else {
            setHistory(pageData);
          }
          setTotal(localHistory.length);
          setHasMore(endIndex < localHistory.length);
          
          // Only show offline mode if we have local data
          if (localHistory.length > 0) {
            setError('Using local data - backend unavailable');
          }
        } catch (parseError) {
          console.error('Failed to parse localStorage:', parseError);
          setHistory([]);
          setTotal(0);
          setHasMore(false);
        }
      } else {
        setHistory([]);
        setTotal(0);
        setHasMore(false);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadMore = () => {
    loadHistory(page + 1, true);
  };

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      // Clear local storage
      localStorage.removeItem('predictionHistory');
      setHistory([]);
      setTotal(0);
      
      // Note: In a real implementation, you might want to call an API to clear server history
      // For now, we just clear the local display
    }
  };

  const deleteItem = (item: PredictionResult, index: number) => {
    // Remove from local display
    const newHistory = history.filter((_, i) => i !== index);
    setHistory(newHistory);
    setTotal(prev => prev - 1);
    
    // Also remove from localStorage if it exists there
    const stored = localStorage.getItem('predictionHistory');
    if (stored) {
      const localHistory = JSON.parse(stored);
      const updatedLocal = localHistory.filter((h: PredictionResult) => h.id !== item.id);
      localStorage.setItem('predictionHistory', JSON.stringify(updatedLocal));
    }
    
    // Note: In a real implementation, you might want to call an API to delete from server
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const getPredictionBadge = (prediction: string) => {
    switch (prediction) {
      case 'real':
        return <Badge variant="default" className="bg-green-600">Real</Badge>;
      case 'fake':
        return <Badge variant="destructive">Fake</Badge>;
      default:
        return <Badge variant="secondary">Inconclusive</Badge>;
    }
  };

  const renderHistoryItem = (item: PredictionResult, index: number) => {
    try {
      const analysisType = getAnalysisType(item);
      const typeIcon = analysisType === 'url' ? '🔗' : analysisType === 'file' ? '📄' : '📝';
      
      return (
        <div key={item.id || index}>
          <div className="space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{typeIcon}</span>
                  {getPredictionBadge(item.prediction)}
                  <span className="text-sm text-muted-foreground">
                    {item.confidence || 0}% confidence
                  </span>
                  {item.processingTime && (
                    <span className="text-xs text-muted-foreground">
                      ({item.processingTime}s)
                    </span>
                  )}
                </div>
                <p className="text-sm">
                  {truncateText(item.inputText || item.input_text || 'No text available')}
                </p>
                {(item.inputUrl || item.input_url) && (
                  <p className="text-xs text-muted-foreground">
                    URL: {item.inputUrl || item.input_url}
                  </p>
                )}
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{formatDate(item.timestamp)}</span>
                  <span>• {analysisType.toUpperCase()}</span>
                  {item.modelVersion && (
                    <span>• Model: {item.modelVersion}</span>
                  )}
                </div>
              </div>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onViewResult(item)}
                >
                  <Eye className="size-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => deleteItem(item, index)}
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>
            </div>
          </div>
          {index < filteredHistory.length - 1 && <Separator className="mt-4" />}
        </div>
      );
    } catch (error) {
      console.error('Error rendering history item:', error);
      return (
        <div key={index} className="p-4 border border-red-200 rounded">
          <p className="text-red-500">Error displaying this item</p>
        </div>
      );
    }
  };

  if (error && history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Analysis History</CardTitle>
          <CardDescription>Unable to load history from server</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Server className="size-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-2">{error}</p>
            <Button onClick={() => loadHistory()} variant="outline">
              <RefreshCw className="mr-2 size-4" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading && history.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Analysis History</CardTitle>
          <CardDescription>Loading your prediction history...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <RefreshCw className="size-12 text-muted-foreground mb-4 animate-spin" />
            <p className="text-muted-foreground">Loading history...</p>
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
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Analysis History</CardTitle>
            <CardDescription>
              {total > 0 ? `${total} total predictions` : `${history.length} predictions`}
              {error && <span className="text-blue-600 ml-2">(Offline mode)</span>}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadHistory()}
              disabled={isLoading}
            >
              <RefreshCw className={`mr-2 size-4 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={clearHistory}
            >
              <Trash2 className="mr-2 size-4" />
              Clear All
            </Button>
          </div>
        </div>
        
        {/* Filter Buttons */}
        <div className="flex gap-2 mt-4">
          <Button
            variant={filterType === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('all')}
          >
            All ({history.length})
          </Button>
          <Button
            variant={filterType === 'text' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('text')}
          >
            📝 Text ({getTypeStats().textCount})
          </Button>
          <Button
            variant={filterType === 'url' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('url')}
          >
            🔗 URL ({getTypeStats().urlCount})
          </Button>
          <Button
            variant={filterType === 'file' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterType('file')}
          >
            📄 File ({getTypeStats().fileCount})
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px] pr-4">
          <div className="space-y-4">
            {filteredHistory.map((item, index) => renderHistoryItem(item, index))}
            
            {hasMore && (
              <div className="flex justify-center pt-4">
                <Button
                  variant="outline"
                  onClick={loadMore}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <RefreshCw className="mr-2 size-4 animate-spin" />
                  ) : null}
                  Load More
                </Button>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
