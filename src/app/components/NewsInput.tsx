import { useState } from 'react';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { FileText, Link, Upload, Loader } from 'lucide-react';
import { toast } from 'sonner';

interface NewsInputProps {
  onAnalyze: (text: string, url?: string, isFileUpload?: boolean) => void;
  isLoading: boolean;
}

export function NewsInput({ onAnalyze, isLoading }: NewsInputProps) {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [activeTab, setActiveTab] = useState('text');

  const handleTextAnalyze = () => {
    if (!text.trim()) {
      toast.error('Please enter some text to analyze');
      return;
    }
    onAnalyze(text);
  };

  const handleUrlAnalyze = () => {
    if (!url.trim()) {
      toast.error('Please enter a URL');
      return;
    }
    if (!isValidUrl(url)) {
      toast.error('Please enter a valid URL');
      return;
    }
    // Simulate fetching content from URL
    const mockContent = `Article from ${url}: This is simulated content extracted from the provided URL. The actual implementation would scrape the webpage content for analysis.`;
    onAnalyze(mockContent, url);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'text/plain') {
      toast.error('Please upload a .txt file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setText(content);
      // DON'T switch to text tab - stay in file tab
      // setActiveTab('text'); // REMOVED THIS LINE
      toast.success('File loaded successfully');
    };
    reader.readAsText(file);
  };

  const isValidUrl = (urlString: string) => {
    try {
      new URL(urlString);
      return true;
    } catch {
      return false;
    }
  };

  const loadSampleText = () => {
    const samples = [
      "Scientists have discovered a revolutionary new treatment that cures all diseases overnight! Doctors are shocked by this one simple trick that pharmaceutical companies don't want you to know about. Share this before it gets taken down!",
      "According to a peer-reviewed study published in Nature Medicine on March 15, 2024, researchers at Stanford University found that regular exercise combined with a Mediterranean diet can reduce the risk of cardiovascular disease by up to 30% over a 10-year period. The study included 15,000 participants across multiple countries.",
      "BREAKING NEWS: Celebrity reveals shocking secrets about the government! You won't believe what happens next! This will change everything you thought you knew! Share immediately before they delete this!",
      "The Federal Reserve announced today that interest rates will remain unchanged at 5.25-5.50% following their two-day policy meeting. Fed Chair Jerome Powell stated that the central bank is closely monitoring inflation data while maintaining a cautious approach to monetary policy."
    ];
    
    const randomSample = samples[Math.floor(Math.random() * samples.length)];
    setText(randomSample);
    setActiveTab('text');
    toast.success('Sample text loaded');
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Analyze News Content</CardTitle>
        <CardDescription>
          Enter text, paste a URL, or upload a file to check for misinformation
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="text">
              <FileText className="mr-2 size-4" />
              Text Input
            </TabsTrigger>
            <TabsTrigger value="url">
              <Link className="mr-2 size-4" />
              URL
            </TabsTrigger>
            <TabsTrigger value="file">
              <Upload className="mr-2 size-4" />
              File Upload
            </TabsTrigger>
          </TabsList>

          <TabsContent value="text" className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <Label htmlFor="news-text">News Article Text</Label>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={loadSampleText}
                  type="button"
                >
                  Load Sample
                </Button>
              </div>
              <Textarea
                id="news-text"
                placeholder="Paste the news article or text you want to verify here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="min-h-[200px]"
              />
              <p className="text-sm text-muted-foreground mt-2">
                {text.length} characters
              </p>
            </div>
            <Button
              onClick={handleTextAnalyze}
              disabled={isLoading || !text.trim()}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader className="mr-2 size-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Analyze Text'
              )}
            </Button>
          </TabsContent>

          <TabsContent value="url" className="space-y-4">
            <div>
              <Label htmlFor="news-url">Article URL</Label>
              <Input
                id="news-url"
                type="url"
                placeholder="https://example.com/article"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="mt-2"
              />
              <p className="text-sm text-muted-foreground mt-2">
                We'll extract and analyze the article content from the provided URL
              </p>
            </div>
            <Button
              onClick={handleUrlAnalyze}
              disabled={isLoading || !url.trim()}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader className="mr-2 size-4 animate-spin" />
                  Fetching & Analyzing...
                </>
              ) : (
                'Analyze URL'
              )}
            </Button>
          </TabsContent>

          <TabsContent value="file" className="space-y-4">
            <div>
              <Label htmlFor="news-file">Upload Text File</Label>
              <Input
                id="news-file"
                type="file"
                accept=".txt"
                onChange={handleFileUpload}
                className="mt-2"
                disabled={isLoading}
              />
              <p className="text-sm text-muted-foreground mt-2">
                Supported format: .txt (plain text)
              </p>
            </div>
            {text && (
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Upload className="size-4 text-green-600" />
                  <span className="text-sm font-medium text-green-600">File loaded successfully!</span>
                </div>
                <div className="mb-3">
                  <Label className="text-sm font-medium">File Content Preview:</Label>
                  <div className="mt-1 p-3 bg-background border rounded text-sm max-h-32 overflow-y-auto">
                    {text.substring(0, 300)}{text.length > 300 ? '...' : ''}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {text.length} characters loaded
                  </p>
                </div>
                <Button
                  onClick={() => onAnalyze(text, undefined, true)}
                  disabled={isLoading}
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <Loader className="mr-2 size-4 animate-spin" />
                      Analyzing File...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 size-4" />
                      Analyze Uploaded File
                    </>
                  )}
                </Button>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}