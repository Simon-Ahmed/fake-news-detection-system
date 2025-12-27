import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { 
  Shield, 
  Brain, 
  Target, 
  Users, 
  TriangleAlert,
  CircleCheck,
  Info
} from 'lucide-react';

export function AboutPage() {
  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3 mb-2">
            <Shield className="size-8 text-primary" />
            <CardTitle className="text-3xl">Fake News Detection AI</CardTitle>
          </div>
          <CardDescription className="text-base">
            An advanced machine learning system designed to identify misinformation and help users make informed decisions about the content they consume.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <Info className="size-4" />
            <AlertDescription>
              This tool is designed to assist in identifying potential misinformation, but should not be the sole factor in determining content credibility. Always verify important information through multiple trusted sources.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* How It Works */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="size-5" />
            How It Works
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div>
              <h4 className="mb-2 flex items-center gap-2">
                <span className="flex items-center justify-center size-6 rounded-full bg-primary text-primary-foreground text-sm">1</span>
                Natural Language Processing
              </h4>
              <p className="text-sm text-muted-foreground ml-8">
                Our system uses advanced NLP techniques to analyze the linguistic patterns, writing style, and structure of news content. This includes examining word choice, sentence complexity, and overall coherence.
              </p>
            </div>

            <Separator />

            <div>
              <h4 className="mb-2 flex items-center gap-2">
                <span className="flex items-center justify-center size-6 rounded-full bg-primary text-primary-foreground text-sm">2</span>
                Transformer Models (BERT)
              </h4>
              <p className="text-sm text-muted-foreground ml-8">
                We employ state-of-the-art transformer-based models, specifically fine-tuned BERT (Bidirectional Encoder Representations from Transformers), which has been trained on thousands of verified fake and real news articles.
              </p>
            </div>

            <Separator />

            <div>
              <h4 className="mb-2 flex items-center gap-2">
                <span className="flex items-center justify-center size-6 rounded-full bg-primary text-primary-foreground text-sm">3</span>
                Multi-Factor Analysis
              </h4>
              <p className="text-sm text-muted-foreground ml-8">
                The system evaluates multiple indicators including emotional language, sensationalism, source credibility, citation presence, and logical consistency to provide a comprehensive assessment.
              </p>
            </div>

            <Separator />

            <div>
              <h4 className="mb-2 flex items-center gap-2">
                <span className="flex items-center justify-center size-6 rounded-full bg-primary text-primary-foreground text-sm">4</span>
                Confidence Scoring
              </h4>
              <p className="text-sm text-muted-foreground ml-8">
                Each prediction comes with a confidence score that reflects the model's certainty. Predictions below 60% confidence are marked as inconclusive, encouraging additional verification.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="size-5" />
            Key Features
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex gap-3">
              <CircleCheck className="size-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="mb-1">Real-time Analysis</h4>
                <p className="text-sm text-muted-foreground">
                  Get instant predictions on news articles, social media posts, and other text content
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <CircleCheck className="size-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="mb-1">Detailed Explanations</h4>
                <p className="text-sm text-muted-foreground">
                  Understand why content was flagged with comprehensive breakdowns of key factors
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <CircleCheck className="size-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="mb-1">Multiple Input Methods</h4>
                <p className="text-sm text-muted-foreground">
                  Analyze content via text input, URL scraping, or file upload
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <CircleCheck className="size-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="mb-1">Continuous Learning</h4>
                <p className="text-sm text-muted-foreground">
                  The model improves over time through user feedback and regular updates
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <CircleCheck className="size-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="mb-1">Privacy Focused</h4>
                <p className="text-sm text-muted-foreground">
                  Your analyses are processed securely and feedback is collected anonymously
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <CircleCheck className="size-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="mb-1">Fact-Checking Resources</h4>
                <p className="text-sm text-muted-foreground">
                  Direct links to trusted fact-checking organizations for additional verification
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Training Data */}
      <Card>
        <CardHeader>
          <CardTitle>Training Datasets</CardTitle>
          <CardDescription>Our model is trained on multiple verified datasets</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start justify-between p-3 bg-muted rounded-lg">
              <div>
                <h4>LIAR Dataset</h4>
                <p className="text-sm text-muted-foreground">
                  12,000+ fact-checked statements from PolitiFact
                </p>
              </div>
              <Badge variant="outline">Political</Badge>
            </div>

            <div className="flex items-start justify-between p-3 bg-muted rounded-lg">
              <div>
                <h4>FakeNewsNet</h4>
                <p className="text-sm text-muted-foreground">
                  23,000+ news articles with credibility labels
                </p>
              </div>
              <Badge variant="outline">General News</Badge>
            </div>

            <div className="flex items-start justify-between p-3 bg-muted rounded-lg">
              <div>
                <h4>COVID-19 Fake News Dataset</h4>
                <p className="text-sm text-muted-foreground">
                  10,000+ pandemic-related claims and fact-checks
                </p>
              </div>
              <Badge variant="outline">Health</Badge>
            </div>

            <div className="flex items-start justify-between p-3 bg-muted rounded-lg">
              <div>
                <h4>ISOT Fake News Dataset</h4>
                <p className="text-sm text-muted-foreground">
                  21,000+ authentic and fake news articles
                </p>
              </div>
              <Badge variant="outline">Mixed Topics</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ethical Considerations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="size-5" />
            Ethical Considerations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert>
            <TriangleAlert className="size-4" />
            <AlertDescription>
              This tool is designed to assist, not replace, human judgment in evaluating news content.
            </AlertDescription>
          </Alert>

          <div className="space-y-3 text-sm">
            <div>
              <h4 className="mb-1">Transparency</h4>
              <p className="text-muted-foreground">
                We provide detailed explanations for all predictions, showing which factors influenced the decision and to what degree.
              </p>
            </div>

            <Separator />

            <div>
              <h4 className="mb-1">Bias Mitigation</h4>
              <p className="text-muted-foreground">
                Our training data is carefully balanced across political perspectives, topics, and time periods to minimize algorithmic bias.
              </p>
            </div>

            <Separator />

            <div>
              <h4 className="mb-1">User Feedback</h4>
              <p className="text-muted-foreground">
                Users can report incorrect predictions, helping us identify edge cases and improve the model's accuracy over time.
              </p>
            </div>

            <Separator />

            <div>
              <h4 className="mb-1">Limitations Awareness</h4>
              <p className="text-muted-foreground">
                We clearly communicate the model's limitations and encourage users to verify important information through multiple sources.
              </p>
            </div>

            <Separator />

            <div>
              <h4 className="mb-1">Privacy Protection</h4>
              <p className="text-muted-foreground">
                All feedback is collected anonymously, and we do not store or share personal information about our users.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Technical Stack */}
      <Card>
        <CardHeader>
          <CardTitle>Technology Stack</CardTitle>
          <CardDescription>Built with modern AI and web technologies</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="p-3 bg-muted rounded-lg">
              <h4 className="mb-1">Machine Learning</h4>
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge>BERT</Badge>
                <Badge>Transformers</Badge>
                <Badge>PyTorch</Badge>
                <Badge>Scikit-learn</Badge>
              </div>
            </div>

            <div className="p-3 bg-muted rounded-lg">
              <h4 className="mb-1">Backend</h4>
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge>Python</Badge>
                <Badge>FastAPI</Badge>
                <Badge>REST API</Badge>
              </div>
            </div>

            <div className="p-3 bg-muted rounded-lg">
              <h4 className="mb-1">Frontend</h4>
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge>React</Badge>
                <Badge>TypeScript</Badge>
                <Badge>Tailwind CSS</Badge>
              </div>
            </div>

            <div className="p-3 bg-muted rounded-lg">
              <h4 className="mb-1">Visualization</h4>
              <div className="flex flex-wrap gap-2 mt-2">
                <Badge>Recharts</Badge>
                <Badge>Radix UI</Badge>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}