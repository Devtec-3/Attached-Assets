import { useState, useEffect } from 'react';
import { ArrowLeft, CheckCircle, AlertTriangle, FlaskConical, Bug, Sprout, Shield, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { type DiagnosedResponse, type UncertainResponse } from '@/lib/api';

interface ResultsViewProps {
  result: DiagnosedResponse | UncertainResponse;
  imagePreview: string;
  onBack: () => void;
}

const CATEGORY_CONFIG: Record<
  string,
  { label: string; icon: React.ElementType; color: string; bg: string; border: string }
> = {
  Chemical: {
    label: 'Chemical',
    icon: FlaskConical,
    color: 'hsl(195 40% 30%)',
    bg: 'hsl(195 40% 95%)',
    border: 'hsl(195 40% 80%)',
  },
  Biological: {
    label: 'Biological',
    icon: Bug,
    color: 'hsl(145 42% 28%)',
    bg: 'hsl(145 42% 95%)',
    border: 'hsl(145 42% 78%)',
  },
  Cultural: {
    label: 'Cultural',
    icon: Sprout,
    color: 'hsl(32 68% 38%)',
    bg: 'hsl(32 68% 95%)',
    border: 'hsl(32 68% 78%)',
  },
  Preventive: {
    label: 'Preventive',
    icon: Shield,
    color: 'hsl(260 35% 40%)',
    bg: 'hsl(260 35% 95%)',
    border: 'hsl(260 35% 78%)',
  },
};

function ConfidenceBar({ confidence }: { confidence: number }) {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setWidth(confidence), 200);
    return () => clearTimeout(timer);
  }, [confidence]);

  const getColor = (c: number) => {
    if (c >= 80) return 'hsl(145 42% 32%)';
    if (c >= 65) return 'hsl(32 68% 48%)';
    return 'hsl(4 72% 46%)';
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'hsl(30 12% 44%)' }}>
          Model Confidence
        </span>
        <span
          className="font-mono-app text-lg font-bold"
          style={{ color: getColor(confidence) }}
          data-testid="text-confidence"
        >
          {confidence.toFixed(1)}%
        </span>
      </div>
      <div
        className="h-3 rounded-full overflow-hidden"
        style={{ backgroundColor: 'hsl(38 20% 88%)' }}
      >
        <div
          className="h-full rounded-full transition-all duration-1000 ease-out"
          style={{
            width: `${width}%`,
            backgroundColor: getColor(confidence),
          }}
        />
      </div>
      <div className="flex justify-between mt-1">
        <span className="text-xs" style={{ color: 'hsl(30 12% 56%)' }}>0%</span>
        <span className="text-xs" style={{ color: 'hsl(30 12% 56%)' }}>100%</span>
      </div>
    </div>
  );
}

function RecommendationCard({
  category,
  text,
  index,
}: {
  category: string;
  text: string;
  index: number;
}) {
  const config = CATEGORY_CONFIG[category] ?? {
    label: category,
    icon: Shield,
    color: 'hsl(30 20% 30%)',
    bg: 'hsl(38 20% 94%)',
    border: 'hsl(38 20% 80%)',
  };

  const Icon = config.icon;
  const staggerClass = ['stagger-1', 'stagger-2', 'stagger-3', 'stagger-4'][index] ?? '';

  return (
    <div
      className={`rounded-xl p-4 border opacity-0 animate-fade-in-up ${staggerClass}`}
      style={{
        backgroundColor: config.bg,
        borderColor: config.border,
      }}
      data-testid={`card-recommendation-${index}`}
    >
      <div className="flex items-center gap-2 mb-2">
        <div
          className="w-7 h-7 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: config.color + '22' }}
        >
          <Icon className="w-3.5 h-3.5" style={{ color: config.color }} />
        </div>
        <span
          className="text-xs font-bold uppercase tracking-wider"
          style={{ color: config.color }}
        >
          {config.label}
        </span>
      </div>
      <p className="text-sm leading-relaxed" style={{ color: 'hsl(30 20% 18%)' }}>
        {text}
      </p>
    </div>
  );
}

export default function ResultsView({ result, imagePreview, onBack }: ResultsViewProps) {
  const isDiagnosed = result.status === 'diagnosed';
  const isUncertain = result.status === 'uncertain';

  const diagnosed = isDiagnosed ? (result as DiagnosedResponse) : null;
  const uncertain = isUncertain ? (result as UncertainResponse) : null;

  return (
    <div className="animate-fade-in w-full max-w-xl mx-auto">
      {/* Back button */}
      <button
        className="flex items-center gap-1.5 text-sm font-medium mb-6 transition-opacity hover:opacity-70"
        style={{ color: 'hsl(145 42% 28%)' }}
        onClick={onBack}
        data-testid="button-back"
      >
        <ArrowLeft className="w-4 h-4" />
        New Analysis
      </button>

      {/* Image strip */}
      <div className="relative rounded-xl overflow-hidden mb-5" style={{ height: '200px' }}>
        <img
          src={imagePreview}
          alt="Analyzed leaf"
          className="w-full h-full object-cover"
          data-testid="img-result-preview"
        />
        <div
          className="absolute inset-0"
          style={{ background: 'linear-gradient(to right, rgba(30,20,10,0.65) 0%, transparent 55%)' }}
        />
        <div className="absolute inset-0 flex flex-col justify-end p-5">
          {isDiagnosed && diagnosed && (
            <>
              <div className="flex items-center gap-2 mb-2">
                {diagnosed.is_healthy ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                )}
                <span className="text-xs font-semibold text-white/80 uppercase tracking-wide">
                  {diagnosed.is_healthy ? 'Healthy Plant' : 'Disease Detected'}
                </span>
              </div>
              <h2
                className="font-display text-2xl font-bold text-white leading-tight"
                data-testid="text-disease-name"
              >
                {diagnosed.disease_name}
              </h2>
              <p className="text-white/70 text-xs mt-1" data-testid="text-crop-type">
                {diagnosed.crop_type}
              </p>
            </>
          )}
          {isUncertain && uncertain && (
            <>
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-semibold text-white/80 uppercase tracking-wide">
                  Low Confidence
                </span>
              </div>
              <h2 className="font-display text-2xl font-bold text-white leading-tight" data-testid="text-disease-name">
                {uncertain.predicted_class}
              </h2>
            </>
          )}
        </div>
      </div>

      {/* Confidence bar */}
      <div
        className="rounded-xl p-5 border mb-4"
        style={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--card-border))' }}
      >
        <ConfidenceBar confidence={result.confidence} />
      </div>

      {/* Uncertain state */}
      {isUncertain && uncertain && (
        <div
          className="rounded-xl p-5 border mb-4 animate-fade-in-up"
          style={{
            backgroundColor: 'hsl(32 68% 52% / 0.08)',
            borderColor: 'hsl(32 68% 52% / 0.3)',
          }}
          data-testid="status-uncertain"
        >
          <div className="flex items-start gap-3">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
              style={{ backgroundColor: 'hsl(32 68% 52% / 0.15)' }}
            >
              <Users className="w-4 h-4" style={{ color: 'hsl(32 68% 38%)' }} />
            </div>
            <div>
              <p className="text-sm font-bold mb-1" style={{ color: 'hsl(30 20% 14%)' }}>
                Consult an Agricultural Expert
              </p>
              <p className="text-sm leading-relaxed" style={{ color: 'hsl(30 12% 44%)' }}>
                {uncertain.message || 'Confidence is below threshold for a reliable diagnosis. Contact your local agricultural extension officer for a hands-on inspection.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Diagnosed: Description + Symptoms */}
      {isDiagnosed && diagnosed && (
        <>
          {/* Healthy message */}
          {diagnosed.is_healthy && (
            <div
              className="rounded-xl p-5 border mb-4 animate-fade-in-up"
              style={{
                backgroundColor: 'hsl(145 42% 28% / 0.07)',
                borderColor: 'hsl(145 42% 28% / 0.25)',
              }}
              data-testid="status-healthy"
            >
              <div className="flex items-start gap-3">
                <div
                  className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                  style={{ backgroundColor: 'hsl(145 42% 28% / 0.15)' }}
                >
                  <CheckCircle className="w-4 h-4" style={{ color: 'hsl(145 42% 28%)' }} />
                </div>
                <div>
                  <p className="text-sm font-bold mb-1" style={{ color: 'hsl(30 20% 14%)' }}>
                    Your crop appears healthy
                  </p>
                  <p className="text-sm leading-relaxed" style={{ color: 'hsl(30 12% 44%)' }}>
                    No signs of disease detected. Continue your current management practices and monitor regularly.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Description */}
          {diagnosed.description && (
            <div
              className="rounded-xl p-5 border mb-4 animate-fade-in-up"
              style={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--card-border))' }}
              data-testid="section-description"
            >
              <h3
                className="text-xs font-bold uppercase tracking-widest mb-3"
                style={{ color: 'hsl(30 12% 44%)' }}
              >
                About This Condition
              </h3>
              <p className="text-sm leading-relaxed" style={{ color: 'hsl(30 20% 18%)' }}>
                {diagnosed.description}
              </p>
            </div>
          )}

          {/* Symptoms */}
          {diagnosed.symptoms && (
            <div
              className="rounded-xl p-5 border mb-4 animate-fade-in-up"
              style={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--card-border))' }}
              data-testid="section-symptoms"
            >
              <div className="flex items-center gap-2 mb-3">
                <Badge
                  variant="outline"
                  className="text-xs font-bold uppercase tracking-wider px-2 py-0.5"
                  style={{ color: 'hsl(4 72% 46%)', borderColor: 'hsl(4 72% 46% / 0.4)', backgroundColor: 'hsl(4 72% 46% / 0.07)' }}
                >
                  Symptoms
                </Badge>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: 'hsl(30 20% 18%)' }}>
                {diagnosed.symptoms}
              </p>
            </div>
          )}

          {/* Recommendations */}
          {!diagnosed.is_healthy && diagnosed.recommendations && diagnosed.recommendations.length > 0 && (
            <div data-testid="section-recommendations">
              <div className="flex items-center gap-3 mb-3">
                <Separator className="flex-1" />
                <span
                  className="text-xs font-bold uppercase tracking-widest whitespace-nowrap"
                  style={{ color: 'hsl(30 12% 44%)' }}
                >
                  Field Recommendations
                </span>
                <Separator className="flex-1" />
              </div>
              <div className="grid grid-cols-1 gap-3">
                {diagnosed.recommendations.map((rec, i) => (
                  <RecommendationCard
                    key={i}
                    category={rec.category}
                    text={rec.recommendation_text}
                    index={i}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Footer CTA */}
      <div className="mt-6">
        <Button
          variant="outline"
          className="w-full h-11 text-sm font-semibold"
          onClick={onBack}
          data-testid="button-analyze-another"
        >
          Analyze Another Sample
        </Button>
      </div>
    </div>
  );
}
