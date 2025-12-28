// API service for fake news detection backend integration

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface PredictionResult {
  id: string;
  prediction: 'real' | 'fake' | 'inconclusive';
  confidence: number;
  explanation: string;
  factors: {
    name: string;
    score: number;
    impact: 'positive' | 'negative' | 'neutral';
    description: string;
  }[];
  sources: string[];
  timestamp: string;
  inputText: string;
  inputUrl?: string;
  modelVersion: string;
  processingTime?: number;
}

export interface FeedbackData {
  predictionId: string;
  userCorrection: 'real' | 'fake';
  comment?: string;
}

export interface ModelStats {
  totalPredictions: number;
  accuracy?: number;
  fakePredictions: number;
  realPredictions: number;
  inconclusivePredictions: number;
  textPredictions: number;
  urlPredictions: number;
  filePredictions: number;
  avgConfidence: number;
  modelVersion: string;
  uptimeHours: number;
}

export interface HealthStatus {
  status: string;
  mlModelLoaded: boolean;
  databaseConnected: boolean;
  redisConnected: boolean;
  modelVersion: string;
  timestamp: string;
}

// API Error handling
class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  console.log('🔍 Making API request to:', url);
  console.log('🔍 Request options:', options);
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Add timeout to prevent hanging
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
  
  try {
    console.log('📡 Sending request...');
    const response = await fetch(url, { 
      ...defaultOptions, 
      signal: controller.signal 
    });
    clearTimeout(timeoutId);
    
    console.log('📡 Response received:', response.status, response.statusText);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
      console.error('❌ API Error:', errorData);
      throw new APIError(response.status, errorData.message || `HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ API Success:', data);
    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    console.error('🚨 API Request Failed:', error);
    
    if (error instanceof APIError) {
      throw error;
    }
    
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. The backend may be slow to respond.');
    }
    
    // Network or other errors
    console.error('API request failed:', error);
    throw new Error('Failed to connect to the API. Please check if the backend is running.');
  }
}

// Fallback prediction function for when backend is not available
function createFallbackPrediction(text: string): PredictionResult {
  const lowerText = text.toLowerCase();
  
  // Simple rule-based prediction
  let prediction: 'real' | 'fake' | 'inconclusive' = 'inconclusive';
  let confidence = 60;
  
  const fakeIndicators = ['shocking', 'unbelievable', 'you won\'t believe', 'click here', 'amazing', 'secret'];
  const realIndicators = ['according to', 'study', 'research', 'university', 'published'];
  
  const fakeCount = fakeIndicators.filter(word => lowerText.includes(word)).length;
  const realCount = realIndicators.filter(word => lowerText.includes(word)).length;
  
  if (fakeCount > realCount && fakeCount > 0) {
    prediction = 'fake';
    confidence = Math.min(85, 60 + fakeCount * 10);
  } else if (realCount > fakeCount && realCount > 0) {
    prediction = 'real';
    confidence = Math.min(85, 60 + realCount * 10);
  }
  
  return {
    id: 'fallback-' + Date.now(),
    prediction,
    confidence,
    explanation: `This analysis uses a simple fallback system. ${prediction === 'fake' ? 'The text contains language patterns often associated with misinformation.' : prediction === 'real' ? 'The text appears to follow standard journalistic patterns.' : 'The text shows mixed indicators and requires further verification.'}`,
    factors: [
      {
        name: 'Pattern Analysis',
        score: confidence,
        impact: prediction === 'fake' ? 'negative' : 'positive',
        description: `Simple keyword-based analysis (${fakeCount} fake indicators, ${realCount} real indicators)`
      }
    ],
    sources: ['https://www.snopes.com', 'https://www.factcheck.org'],
    timestamp: new Date().toISOString(),
    inputText: text,
    modelVersion: 'fallback-v1.0'
  };
}

// Main prediction function
export const predictFakeNews = async (text: string, url?: string, analysisType?: 'text' | 'url' | 'file'): Promise<PredictionResult> => {
  try {
    if (url) {
      // Use URL prediction endpoint
      const response = await apiRequest<PredictionResult>('/predict', {
        method: 'POST',
        body: JSON.stringify({ url, language: 'en' }),
      });
      
      return {
        ...response,
        timestamp: response.timestamp || new Date().toISOString(),
      };
    } else {
      // Use text prediction endpoint
      const requestBody: any = { text, language: 'en' };
      
      // Add analysis type if specified
      if (analysisType) {
        requestBody.analysis_type = analysisType;
      }
      
      const response = await apiRequest<{
        prediction: string;
        confidence: number;
        explanation: string;
        features: any;
      }>('/predict', {
        method: 'POST',
        body: JSON.stringify(requestBody),
      });
      
      return {
        id: Date.now().toString(),
        prediction: response.prediction.toLowerCase() === 'fake' ? 'fake' : 'real',
        confidence: response.confidence,
        explanation: response.explanation,
        factors: [],
        sources: [],
        timestamp: new Date().toISOString(),
        inputText: text,
        modelVersion: 'lightweight-v1.0',
        analysis_type: analysisType || 'text'
      };
    }
  } catch (error) {
    console.warn('Backend API failed, using fallback prediction:', error);
    
    // If URL analysis fails, we can't provide fallback
    if (url) {
      throw new Error('URL analysis requires backend connection. Please check if the server is running.');
    }
    
    // Use fallback for text analysis
    return createFallbackPrediction(text);
  }
};

// Batch prediction function
export const predictBatchFakeNews = async (texts: string[]): Promise<PredictionResult[]> => {
  const response = await apiRequest<{ predictions: PredictionResult[] }>('/api/batch-predict', {
    method: 'POST',
    body: JSON.stringify({ texts, language: 'en' }),
  });
  
  return response.predictions.map(pred => ({
    ...pred,
    timestamp: pred.timestamp || new Date().toISOString(),
  }));
};

// Submit user feedback
export const submitFeedback = async (feedback: FeedbackData): Promise<void> => {
  await apiRequest('/api/feedback', {
    method: 'POST',
    body: JSON.stringify({
      prediction_id: feedback.predictionId,
      user_correction: feedback.userCorrection,
      comment: feedback.comment,
    }),
  });
};

// Get model statistics
export const getModelStats = async (): Promise<ModelStats> => {
  try {
    const response = await apiRequest<{
      total_predictions: number;
      by_prediction: { [key: string]: number };
      by_analysis_type: { [key: string]: number };
    }>('/stats');
    
    return {
      totalPredictions: response.total_predictions,
      accuracy: undefined,
      fakePredictions: response.by_prediction?.FAKE || 0,
      realPredictions: response.by_prediction?.REAL || 0,
      inconclusivePredictions: response.by_prediction?.inconclusive || 0,
      textPredictions: response.by_analysis_type?.text || 0,
      urlPredictions: response.by_analysis_type?.url || 0,
      filePredictions: response.by_analysis_type?.file || 0,
      avgConfidence: 75, // Default since backend doesn't provide this
      modelVersion: 'lightweight-v1.0',
      uptimeHours: 24,
    };
  } catch (error) {
    console.warn('Stats API failed, using fallback data:', error);
    
    // Fallback to localStorage data
    const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
    
    if (history.length === 0) {
      return {
        totalPredictions: 0,
        accuracy: undefined,
        fakePredictions: 0,
        realPredictions: 0,
        inconclusivePredictions: 0,
        avgConfidence: 0,
        modelVersion: 'fallback-v1.0',
        uptimeHours: 0,
      };
    }

    const fakePredictions = history.filter((h: any) => h.prediction === 'fake').length;
    const realPredictions = history.filter((h: any) => h.prediction === 'real').length;
    const inconclusivePredictions = history.filter((h: any) => h.prediction === 'inconclusive').length;
    const avgConfidence = history.reduce((sum: number, h: any) => sum + (h.confidence || 0), 0) / history.length;

    return {
      totalPredictions: history.length,
      accuracy: undefined,
      fakePredictions,
      realPredictions,
      inconclusivePredictions,
      avgConfidence: Math.round(avgConfidence * 10) / 10,
      modelVersion: 'fallback-v1.0',
      uptimeHours: 1,
    };
  }
};

// Get prediction history
export const getPredictionHistory = async (limit = 50, offset = 0): Promise<{
  predictions: PredictionResult[];
  total: number;
  page: number;
  perPage: number;
}> => {
  try {
    const response = await apiRequest<{
      history: any[];
    }>(`/history`);
    
    return {
      predictions: response.history.map((item: any) => ({
        id: item.id?.toString() || 'unknown',
        prediction: item.prediction?.toLowerCase() === 'fake' ? 'fake' : 'real',
        confidence: item.confidence || 0,
        explanation: item.explanation || 'No explanation available',
        factors: [],
        sources: [],
        timestamp: item.created_at || new Date().toISOString(),
        inputText: item.text || '',
        modelVersion: 'lightweight-v1.0',
        analysis_type: item.analysis_type || 'text'
      })),
      total: response.history.length,
      page: 1,
      perPage: response.history.length,
    };
  } catch (error) {
    console.warn('History API failed, using localStorage fallback:', error);
    
    // Fast fallback to localStorage
    const stored = localStorage.getItem('predictionHistory');
    if (stored) {
      const localHistory = JSON.parse(stored);
      const startIndex = offset;
      const endIndex = startIndex + limit;
      const pageData = localHistory.slice(startIndex, endIndex);
      
      return {
        predictions: pageData,
        total: localHistory.length,
        page: Math.floor(offset / limit) + 1,
        perPage: limit,
      };
    }
    
    return {
      predictions: [],
      total: 0,
      page: 1,
      perPage: limit,
    };
  }
};

// Health check
export const checkHealth = async (): Promise<HealthStatus> => {
  try {
    const response = await apiRequest<{
      status: string;
    }>('/health');
    
    return {
      status: response.status,
      mlModelLoaded: true,
      databaseConnected: true,
      redisConnected: false,
      modelVersion: 'lightweight-v1.0',
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    console.warn('Health API failed, using fallback status:', error);
    
    return {
      status: 'offline',
      mlModelLoaded: false,
      databaseConnected: false,
      redisConnected: false,
      modelVersion: 'fallback-v1.0',
      timestamp: new Date().toISOString(),
    };
  }
};

// Fetch news from URL (this is now handled by the backend)
export const fetchNewsFromUrl = async (url: string): Promise<string> => {
  // This function is now integrated into predictFakeNews when url is provided
  // Keeping for backward compatibility
  const result = await predictFakeNews('', url);
  return result.inputText;
};
