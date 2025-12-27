import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { getModelStats, checkHealth, ModelStats, HealthStatus } from '../../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Activity, TrendingUp, FileCheck, CircleAlert, Server, Database, Cpu } from 'lucide-react';
import { Skeleton } from './ui/skeleton';
import { Badge } from './ui/badge';

export function Dashboard() {
  const [stats, setStats] = useState<ModelStats | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [statsData, healthData] = await Promise.all([
        getModelStats().catch(err => {
          console.warn('Stats API failed:', err);
          return null;
        }),
        checkHealth().catch(err => {
          console.warn('Health API failed:', err);
          return null;
        })
      ]);
      
      setStats(statsData);
      setHealth(healthData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setError('Failed to connect to the backend API. Please ensure the server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Dashboard Unavailable</CardTitle>
          <CardDescription>Unable to connect to the backend API</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Server className="size-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-2">{error}</p>
            <p className="text-sm text-muted-foreground">
              Make sure the backend server is running on http://localhost:8000
            </p>
            <button 
              onClick={loadDashboardData}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Retry Connection
            </button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats || stats.totalPredictions === 0) {
    return (
      <div className="space-y-6">
        {/* System Health */}
        {health && (
          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>Backend API health check</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <Badge variant={health.status === 'healthy' ? 'default' : 'destructive'}>
                  {health.status.toUpperCase()}
                </Badge>
                <div className="flex items-center gap-2 text-sm">
                  <Cpu className="size-4" />
                  ML Model: {health.mlModelLoaded ? '✅' : '❌'}
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Database className="size-4" />
                  Database: {health.databaseConnected ? '✅' : '❌'}
                </div>
                <div className="text-sm text-muted-foreground">
                  Version: {health.modelVersion}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Model Performance Dashboard</CardTitle>
            <CardDescription>Statistics will appear after you analyze some content</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Activity className="size-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No data available yet</p>
              <p className="text-sm text-muted-foreground mt-1">
                Start analyzing news content to see performance metrics
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const predictionData = [
    { name: 'Real', value: stats.realPredictions, color: '#10b981' },
    { name: 'Fake', value: stats.fakePredictions, color: '#ef4444' },
    { name: 'Inconclusive', value: stats.inconclusivePredictions, color: '#f59e0b' }
  ].filter(item => item.value > 0);

  const analysisTypeData = [
    { name: 'Text', value: stats.textPredictions, color: '#8b5cf6' },
    { name: 'URL', value: stats.urlPredictions, color: '#06b6d4' },
    { name: 'File', value: stats.filePredictions, color: '#84cc16' }
  ].filter(item => item.value > 0);

  const barData = [
    { name: 'Real', count: stats.realPredictions },
    { name: 'Fake', count: stats.fakePredictions },
    { name: 'Inconclusive', count: stats.inconclusivePredictions }
  ];

  const typeBarData = [
    { name: 'Text', count: stats.textPredictions },
    { name: 'URL', count: stats.urlPredictions },
    { name: 'File', count: stats.filePredictions }
  ];

  return (
    <div className="space-y-6">
      {/* System Health */}
      {health && (
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Backend API health and performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div className="flex items-center gap-2">
                <Badge variant={health.status === 'healthy' ? 'default' : 'destructive'}>
                  {health.status.toUpperCase()}
                </Badge>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Cpu className="size-4" />
                ML Model: {health.mlModelLoaded ? '✅ Ready' : '❌ Not Ready'}
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Database className="size-4" />
                Database: {health.databaseConnected ? '✅ Connected' : '❌ Disconnected'}
              </div>
              <div className="text-sm text-muted-foreground">
                Uptime: {stats.uptimeHours.toFixed(1)}h
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Total Predictions</CardTitle>
            <Activity className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.totalPredictions}</div>
            <p className="text-xs text-muted-foreground mt-1">
              All-time analyses
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Model Accuracy</CardTitle>
            <TrendingUp className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">
              {stats.accuracy ? `${stats.accuracy}%` : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats.accuracy ? 'Based on user feedback' : 'Insufficient feedback data'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Avg Confidence</CardTitle>
            <FileCheck className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.avgConfidence}%</div>
            <p className="text-xs text-muted-foreground mt-1">
              Prediction certainty
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Fake Detected</CardTitle>
            <CircleAlert className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.fakePredictions}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {stats.totalPredictions > 0 
                ? `${Math.round((stats.fakePredictions / stats.totalPredictions) * 100)}% of total`
                : '0% of total'
              }
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Text Analysis</CardTitle>
            <FileCheck className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.textPredictions}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Direct text input
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">URL Analysis</CardTitle>
            <TrendingUp className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.urlPredictions}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Website content
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">File Analysis</CardTitle>
            <Activity className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.filePredictions}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Uploaded files
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Prediction Distribution</CardTitle>
            <CardDescription>Breakdown of all predictions</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={predictionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {predictionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Analysis Types</CardTitle>
            <CardDescription>Input method breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analysisTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {analysisTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Analysis Methods</CardTitle>
            <CardDescription>Count by input type</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={typeBarData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#06b6d4" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Model Information */}
      <Card>
        <CardHeader>
          <CardTitle>Model Information</CardTitle>
          <CardDescription>Technical details about the detection system</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="mb-2 text-sm font-medium">Current Model</h4>
              <p className="text-sm text-muted-foreground">
                {stats.modelVersion} - BERT-based transformer model fine-tuned for fake news detection
              </p>
            </div>
            <div>
              <h4 className="mb-2 text-sm font-medium">Analysis Features</h4>
              <p className="text-sm text-muted-foreground">
                25+ linguistic features including clickbait detection, emotional language analysis, bias indicators, and source citations
              </p>
            </div>
            <div>
              <h4 className="mb-2 text-sm font-medium">Performance</h4>
              <p className="text-sm text-muted-foreground">
                Real-time inference with &lt;2s response time, CPU-optimized for scalability
              </p>
            </div>
            <div>
              <h4 className="mb-2 text-sm font-medium">Continuous Learning</h4>
              <p className="text-sm text-muted-foreground">
                Model improves through user feedback and periodic retraining with new data
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}