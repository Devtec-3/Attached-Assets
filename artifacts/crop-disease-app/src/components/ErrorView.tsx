import { Terminal, RefreshCw, AlertOctagon } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorViewProps {
  error: string;
  message: string;
  onBack: () => void;
}

export default function ErrorView({ error, message, onBack }: ErrorViewProps) {
  const isModelNotTrained = error === 'model_not_trained';

  return (
    <div className="animate-fade-in-up w-full max-w-xl mx-auto">
      {/* Error header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: 'hsl(4 72% 46% / 0.12)' }}
          >
            <AlertOctagon className="w-4 h-4" style={{ color: 'hsl(4 72% 46%)' }} />
          </div>
          <span
            className="text-xs font-semibold tracking-widest uppercase"
            style={{ color: 'hsl(4 72% 46%)' }}
          >
            System Error
          </span>
        </div>
        <h1
          className="font-display text-3xl font-bold leading-tight"
          style={{ color: 'hsl(30 20% 14%)' }}
        >
          {isModelNotTrained ? 'Model Not Trained' : 'Diagnosis Failed'}
        </h1>
      </div>

      {/* Error card */}
      <div
        className="rounded-xl border mb-4 overflow-hidden"
        style={{
          borderColor: 'hsl(4 72% 46% / 0.3)',
          backgroundColor: 'hsl(4 72% 46% / 0.05)',
        }}
        data-testid="status-error-view"
      >
        <div
          className="px-5 py-3 border-b"
          style={{
            borderColor: 'hsl(4 72% 46% / 0.2)',
            backgroundColor: 'hsl(4 72% 46% / 0.08)',
          }}
        >
          <p
            className="text-xs font-mono font-bold uppercase tracking-widest"
            style={{ color: 'hsl(4 72% 38%)' }}
          >
            {error}
          </p>
        </div>
        <div className="px-5 py-4">
          <p className="text-sm leading-relaxed" style={{ color: 'hsl(30 20% 22%)' }}>
            {message}
          </p>
        </div>
      </div>

      {/* Developer instructions for model_not_trained */}
      {isModelNotTrained && (
        <div
          className="rounded-xl border overflow-hidden mb-6"
          style={{
            borderColor: 'hsl(30 20% 78%)',
            backgroundColor: 'hsl(30 16% 13%)',
          }}
          data-testid="section-dev-instructions"
        >
          <div
            className="flex items-center gap-2 px-4 py-2.5 border-b"
            style={{ borderColor: 'hsl(30 12% 22%)' }}
          >
            <Terminal className="w-3.5 h-3.5" style={{ color: 'hsl(38 20% 60%)' }} />
            <span className="text-xs font-bold" style={{ color: 'hsl(38 20% 60%)' }}>
              Developer — Resolution Steps
            </span>
          </div>
          <div className="p-4 space-y-2">
            <p className="text-xs mb-3" style={{ color: 'hsl(38 20% 56%)' }}>
              The AI model has not been trained yet. Run the following commands to train it and restart the server:
            </p>
            {[
              'python backend/train_model.py',
              '# Then restart the server',
            ].map((cmd, i) => (
              <div
                key={i}
                className="px-3 py-2 rounded-lg text-xs font-mono leading-relaxed"
                style={{
                  backgroundColor: 'hsl(30 16% 9%)',
                  color: cmd.startsWith('#') ? 'hsl(145 42% 52%)' : 'hsl(60 40% 80%)',
                }}
                data-testid={`text-cmd-${i}`}
              >
                {cmd}
              </div>
            ))}
            <div
              className="mt-4 pt-4 border-t"
              style={{ borderColor: 'hsl(30 12% 22%)' }}
            >
              <p className="text-xs" style={{ color: 'hsl(38 20% 46%)' }}>
                After training completes and the server restarts, return here and try your analysis again.
              </p>
            </div>
          </div>
        </div>
      )}

      <Button
        variant="outline"
        className="w-full h-11 text-sm font-semibold flex items-center gap-2"
        onClick={onBack}
        data-testid="button-try-again"
      >
        <RefreshCw className="w-4 h-4" />
        Try Again
      </Button>
    </div>
  );
}
