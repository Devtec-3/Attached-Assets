import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import UploadView from '@/components/UploadView';
import ResultsView from '@/components/ResultsView';
import ErrorView from '@/components/ErrorView';
import { type PredictResponse, type DiagnosedResponse, type UncertainResponse, type ErrorResponse } from '@/lib/api';

const queryClient = new QueryClient();

type AppView = 'upload' | 'results' | 'error';

function AppShell() {
  const [view, setView] = useState<AppView>('upload');
  const [result, setResult] = useState<DiagnosedResponse | UncertainResponse | null>(null);
  const [apiError, setApiError] = useState<ErrorResponse | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');

  const handleResult = (res: PredictResponse, imgPreview: string) => {
    setImagePreview(imgPreview);

    // Check for error response
    if ('error' in res) {
      setApiError(res as ErrorResponse);
      setResult(null);
      setView('error');
      return;
    }

    setResult(res as DiagnosedResponse | UncertainResponse);
    setApiError(null);
    setView('results');
  };

  const handleBack = () => {
    setView('upload');
    setResult(null);
    setApiError(null);
    setImagePreview('');
  };

  return (
    <div
      className="min-h-[100dvh] w-full relative"
      style={{ backgroundColor: 'hsl(42 28% 94%)' }}
    >
      {/* Subtle grain texture overlay */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'repeat',
          backgroundSize: '256px 256px',
          opacity: 0.4,
          zIndex: 0,
        }}
      />

      {/* Decorative top stripe */}
      <div
        className="fixed top-0 left-0 right-0 h-1 z-10"
        style={{ backgroundColor: 'hsl(145 42% 28%)' }}
      />

      {/* Header */}
      <header
        className="fixed top-1 left-0 right-0 z-10 border-b"
        style={{
          backgroundColor: 'hsl(42 28% 94% / 0.95)',
          borderColor: 'hsl(38 20% 82%)',
          backdropFilter: 'blur(8px)',
        }}
        data-testid="app-header"
      >
        <div className="max-w-xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'hsl(145 42% 28%)' }}
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                className="w-4 h-4"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 2a10 10 0 0 1 10 10c0 2.5-.9 4.8-2.4 6.6L12 22l-7.6-3.4A10 10 0 0 1 12 2z" />
                <path d="M12 6v6l4 2" />
              </svg>
            </div>
            <div>
              <p className="text-xs font-bold leading-none" style={{ color: 'hsl(30 20% 14%)' }}>
                CropDx
              </p>
              <p className="text-[10px] leading-none mt-0.5" style={{ color: 'hsl(30 12% 52%)' }}>
                AI Field Diagnostics
              </p>
            </div>
          </div>

          {/* Status indicator */}
          <div
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
            style={{
              backgroundColor: 'hsl(145 42% 28% / 0.10)',
              color: 'hsl(145 42% 24%)',
            }}
            data-testid="status-model"
          >
            <div
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: 'hsl(145 42% 38%)' }}
            />
            Model Active
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-0 pt-24 pb-12 px-4" data-testid="main-content">
        {view === 'upload' && (
          <UploadView onResult={handleResult} />
        )}
        {view === 'results' && result && (
          <ResultsView
            result={result}
            imagePreview={imagePreview}
            onBack={handleBack}
          />
        )}
        {view === 'error' && apiError && (
          <ErrorView
            error={apiError.error}
            message={apiError.message}
            onBack={handleBack}
          />
        )}
      </main>

      {/* Footer */}
      <footer
        className="fixed bottom-0 left-0 right-0 border-t py-2 px-4 z-10"
        style={{
          backgroundColor: 'hsl(42 28% 94% / 0.95)',
          borderColor: 'hsl(38 20% 82%)',
          backdropFilter: 'blur(8px)',
        }}
      >
        <p
          className="text-center text-[10px]"
          style={{ color: 'hsl(30 12% 56%)' }}
        >
          For field reference only. Always confirm with a certified agronomist for treatment decisions.
        </p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AppShell />
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
