import type { ReactNode } from "react";

export interface AssessmentFactor {
  name: string;
  contribution: string;
}

export interface OpportunityAssessmentCardProps {
  title: string;
  sourceLabel: string;
  score: number;
  confidence: number;
  recommendation: "strong" | "review" | "weak";
  factors: AssessmentFactor[];
  warnings?: string[];
  onReview: () => void;
}

const tone: Record<OpportunityAssessmentCardProps["recommendation"], string> = {
  strong: "border-emerald-400/40 bg-emerald-400/10 text-emerald-100",
  review: "border-amber-300/40 bg-amber-300/10 text-amber-100",
  weak: "border-zinc-500/40 bg-zinc-500/10 text-zinc-200",
};

function Stat({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-zinc-500">{label}</dt>
      <dd className="mt-1 font-mono text-lg text-zinc-100">{children}</dd>
    </div>
  );
}

/**
 * Standalone portfolio excerpt. The complete private component also renders source
 * provenance and persisted run links; those private contracts are omitted.
 */
export function OpportunityAssessmentCard({
  title,
  sourceLabel,
  score,
  confidence,
  recommendation,
  factors,
  warnings = [],
  onReview,
}: OpportunityAssessmentCardProps) {
  const boundedScore = Math.max(0, Math.min(100, score));

  return (
    <article className="rounded-xl border border-zinc-800 bg-zinc-950 p-5 text-zinc-100">
      <header className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-zinc-500">{sourceLabel}</p>
          <h2 className="mt-1 text-lg font-semibold">{title}</h2>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-medium ${tone[recommendation]}`}>
          {recommendation}
        </span>
      </header>

      <dl className="mt-5 grid grid-cols-2 gap-4">
        <Stat label="Opportunity score">{boundedScore.toFixed(1)}</Stat>
        <Stat label="Confidence">{Math.max(0, Math.min(100, confidence)).toFixed(1)}%</Stat>
      </dl>

      <div className="mt-4 h-2 overflow-hidden rounded bg-zinc-800" aria-label={`Opportunity score ${boundedScore} out of 100`}>
        <div className="h-full bg-sky-400" style={{ width: `${boundedScore}%` }} />
      </div>

      <ul className="mt-5 space-y-2 text-sm text-zinc-300">
        {factors.map((factor) => (
          <li key={factor.name} className="flex justify-between gap-4">
            <span>{factor.name.replaceAll("_", " ")}</span>
            <span className="font-mono">+{factor.contribution}</span>
          </li>
        ))}
      </ul>

      {warnings.length > 0 && (
        <div className="mt-5 rounded-lg border border-amber-300/30 bg-amber-300/5 p-3">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-amber-200">Review required</h3>
          <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-amber-100/80">
            {warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </div>
      )}

      <button
        type="button"
        onClick={onReview}
        className="mt-5 rounded-lg bg-sky-300 px-4 py-2 text-sm font-semibold text-zinc-950 hover:bg-sky-200 focus:outline-none focus:ring-2 focus:ring-sky-300 focus:ring-offset-2 focus:ring-offset-zinc-950"
      >
        Review evidence
      </button>
    </article>
  );
}
