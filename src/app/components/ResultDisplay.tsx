import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { Alert, AlertDescription } from './ui/alert';
import { 
  CircleCheck, 
  CircleX, 
  TriangleAlert, 
  ExternalLink, 
  TrendingUp, 
  TrendingDown,
  Minus
} from 'lucide-react';
import { PredictionResult } from '../../services/api';

interface ResultDisplayProps {
  result: PredictionResult;
  onFeedback: () => void;
}

export function ResultDisplay({ result, onFeedback }: ResultDisplayProps) {
  const getStatusColor = () => {
    switch (result.prediction) {
      case 'real':
        return 'text-green-600 dark:text-green-400';
      case 'fake':
        return 'text-red-600 dark:text-red-400';
      default:
        return 'text-yellow-600 dark:text-yellow-400';
    }
  };

  const getStatusIcon = () => {
    switch (result.prediction) {
      case 'real':
        return <CircleCheck className="size-12" />;
      case 'fake':
        return <CircleX className="size-12" />;
      default:
        return <TriangleAlert className="size-12" />;
    }
  };

  const getStatusText = () => {
    switch (result.prediction) {
      case 'real':
        return 'Likely Credible';
      case 'fake':
        return 'Likely Misinformation';
      default:
        return 'Inconclusive';
    }
  };

  const getConfidenceColor = () => {
    const confidencePercent = result.confidence * 100;
    if (confidencePercent >= 80) return 'bg-green-500';
    if (confidencePercent >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getFactorIcon = (impact: string) => {
    switch (impact) {
      case 'positive':
        return <TrendingUp className="size-4 text-green-600 dark:text-green-400" />;
      case 'negative':
        return <TrendingDown className="size-4 text-red-600 dark:text-red-400" />;
      default:
        return <Minus className="size-4 text-gray-600 dark:text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Main Result Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Analysis Result</CardTitle>
            <Badge variant={result.prediction === 'real' ? 'default' : result.prediction === 'fake' ? 'destructive' : 'secondary'}>
              {result.prediction.toUpperCase()}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Status Icon and Text */}
          <div className="flex flex-col items-center text-center space-y-4">
            <div className={getStatusColor()}>
              {getStatusIcon()}
            </div>
            <div>
              <h3 className="text-2xl">{getStatusText()}</h3>
              <p className="text-muted-foreground mt-1">
                Confidence: {Math.round(result.confidence * 100)}%
              </p>
            </div>
          </div>

          {/* Confidence Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Confidence Level</span>
              <span>{Math.round(result.confidence * 100)}%</span>
            </div>
            <Progress value={result.confidence * 100} className={getConfidenceColor()} />
          </div>

          <Separator />

          {/* Explanation */}
          <div>
            <h4 className="mb-2">Analysis Explanation</h4>
            <Alert>
              <AlertDescription>
                {result.explanation}
              </AlertDescription>
            </Alert>
          </div>

          {/* Key Factors */}
          <div>
            <h4 className="mb-3">Key Factors Analyzed</h4>
            <div className="space-y-3">
              {result.factors.map((factor, index) => (
                <div key={index} className="flex items-start justify-between p-3 bg-muted rounded-lg">
                  <div className="flex items-start gap-2">
                    {getFactorIcon(factor.impact)}
                    <div>
                      <p className="text-sm">{factor.name}</p>
                      <p className="text-xs text-muted-foreground">
                        Impact: {factor.impact}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline">{Math.round(factor.score)}</Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Fact-Checking Sources */}
          {result.sources && result.sources.length > 0 && (
            <>
              <Separator />
              <div>
                <h4 className="mb-3">Recommended Fact-Checking Sources</h4>
                <div className="space-y-2">
                  {result.sources.map((source, index) => (
                    <a
                      key={index}
                      href={source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-2 hover:bg-muted rounded-lg transition-colors"
                    >
                      <span className="text-sm">{source}</span>
                      <ExternalLink className="size-4 text-muted-foreground" />
                    </a>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Feedback Button */}
          <Button
            variant="outline"
            className="w-full"
            onClick={onFeedback}
          >
            Provide Feedback on This Analysis
          </Button>
        </CardContent>
      </Card>

      {/* Additional Info Card */}
      <Card>
        <CardHeader>
          <CardTitle>Important Disclaimer</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            This AI-powered analysis is provided for informational purposes only and should not be considered definitive proof of authenticity or misinformation.
          </p>
          <p>
            Always verify important information through multiple credible sources and use critical thinking when evaluating news content.
          </p>
          <p>
            The model analyzes linguistic patterns, writing style, and content structure but cannot verify factual claims without access to external databases.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}