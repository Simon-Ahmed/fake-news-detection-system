import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from './ui/dialog';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { submitFeedback } from '../../services/api';
import { toast } from 'sonner';
import { Loader } from 'lucide-react';

interface FeedbackDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  predictionId: string;
  currentPrediction: 'real' | 'fake' | 'inconclusive';
}

export function FeedbackDialog({ 
  open, 
  onOpenChange, 
  predictionId,
  currentPrediction 
}: FeedbackDialogProps) {
  const [correction, setCorrection] = useState<'real' | 'fake'>(
    currentPrediction === 'fake' ? 'real' : 'fake'
  );
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await submitFeedback({
        predictionId,
        userCorrection: correction,
        comment: comment.trim() || undefined
      });
      toast.success('Thank you for your feedback! This helps improve our model.');
      onOpenChange(false);
      setComment('');
    } catch (error) {
      toast.error('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Provide Feedback</DialogTitle>
          <DialogDescription>
            Help us improve our fake news detection model by providing your feedback on this prediction.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="space-y-3">
            <Label>What do you think the correct classification should be?</Label>
            <RadioGroup value={correction} onValueChange={(value) => setCorrection(value as 'real' | 'fake')}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="real" id="real" />
                <Label htmlFor="real" className="cursor-pointer">
                  This content is real/credible
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="fake" id="fake" />
                <Label htmlFor="fake" className="cursor-pointer">
                  This content is fake/misinformation
                </Label>
              </div>
            </RadioGroup>
          </div>

          <div className="space-y-2">
            <Label htmlFor="comment">Additional Comments (Optional)</Label>
            <Textarea
              id="comment"
              placeholder="Please share why you believe this classification is incorrect, or provide any additional context..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="min-h-[100px]"
            />
          </div>

          <div className="bg-muted p-3 rounded-lg text-sm">
            <p className="text-muted-foreground">
              Your feedback is anonymous and will be used solely to improve the accuracy of our detection model. 
              We may review flagged predictions to better understand edge cases and improve our algorithms.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader className="mr-2 size-4 animate-spin" />
                Submitting...
              </>
            ) : (
              'Submit Feedback'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}