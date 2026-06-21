/**
 * App component — main layout with semantic landmarks.
 *
 * Sets document.documentElement.lang on mount for screen readers.
 */

import React, { useEffect } from 'react';
import { SkipLink } from './components/shared/SkipLink';
import { ErrorBoundary } from './components/shared/ErrorBoundary';
import { CarbonForm } from './components/Calculator/CarbonForm';
import { ResultsDisplay } from './components/Calculator/ResultsDisplay';
import { CategoryChart } from './components/Calculator/CategoryChart';
import { InsightsList } from './components/Insights/InsightsList';
import { HistoryChart } from './components/History/HistoryChart';
import { HistoryTable } from './components/History/HistoryTable';
import { useCarbonStore } from './store/carbonStore';
import { useHistory } from './hooks/useHistory';

const App: React.FC = () => {
  const result = useCarbonStore((state) => state.result);
  const { history } = useHistory();

  // Set lang attribute for screen readers — wired for future i18n expansion
  useEffect(() => {
    document.documentElement.lang = 'en';
  }, []);

  return (
    <>
      <SkipLink />

      <div className="min-h-screen bg-hero-pattern font-sans text-white">
        {/* Header */}
        <header className="border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-lg">
          <nav
            className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4"
            aria-label="Main navigation"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl" aria-hidden="true">
                🌍
              </span>
              <h1 className="text-xl font-bold tracking-tight">
                <span className="bg-gradient-to-r from-carbon-400 to-emerald-300 bg-clip-text text-transparent">
                  Carbon
                </span>{' '}
                Platform
              </h1>
            </div>
            <div className="flex items-center gap-2">
              <span className="rounded-full bg-carbon-500/20 px-3 py-1 text-xs font-medium text-carbon-300">
                v1.0
              </span>
            </div>
          </nav>
        </header>

        {/* Main content */}
        <main
          id="main-content"
          className="mx-auto max-w-6xl px-6 py-12"
          role="main"
        >
          {/* Hero section */}
          <section className="mb-12 text-center" aria-label="Introduction">
            <h2 className="mb-4 text-4xl font-extrabold tracking-tight sm:text-5xl">
              <span className="bg-gradient-to-r from-carbon-400 via-emerald-300 to-teal-400 bg-clip-text text-transparent">
                Understand
              </span>{' '}
              →{' '}
              <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                Track
              </span>{' '}
              →{' '}
              <span className="bg-gradient-to-r from-amber-400 to-orange-300 bg-clip-text text-transparent">
                Reduce
              </span>
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-slate-300">
              Calculate your annual carbon footprint, get AI-powered reduction
              insights, and track your progress toward a sustainable future.
            </p>
          </section>

          {/* Two-column layout */}
          <div className="grid gap-12 lg:grid-cols-2">
            {/* Left column — form */}
            <section aria-label="Calculator form">
              <div className="rounded-3xl border border-slate-700/50 bg-slate-800/30 p-8 shadow-2xl backdrop-blur-sm">
                <h2 className="mb-6 text-2xl font-bold text-white">
                  📊 Calculate Your Footprint
                </h2>
                <ErrorBoundary>
                  <CarbonForm />
                </ErrorBoundary>
              </div>
            </section>

            {/* Right column — results */}
            <section aria-label="Results">
              {result ? (
                <ErrorBoundary>
                  <div className="space-y-6">
                    <ResultsDisplay result={result} />
                    <CategoryChart breakdown={result.breakdown} />
                  </div>
                </ErrorBoundary>
              ) : (
                <div className="flex h-full items-center justify-center rounded-3xl border border-dashed border-slate-700/50 bg-slate-800/10 p-12">
                  <div className="text-center">
                    <div className="mb-4 text-6xl" aria-hidden="true">
                      🌱
                    </div>
                    <p className="text-lg font-medium text-slate-300">
                      Fill in the form to see your results
                    </p>
                    <p className="mt-2 text-sm text-slate-400">
                      Your carbon footprint will appear here
                    </p>
                  </div>
                </div>
              )}
            </section>
          </div>

          {/* Insights (full width) */}
          {result && result.insights.length > 0 && (
            <div className="mt-12">
              <ErrorBoundary>
                <InsightsList
                  insights={result.insights}
                  source={result.source}
                />
              </ErrorBoundary>
            </div>
          )}

          {/* History section */}
          {history.length > 0 && (
            <section className="mt-16 space-y-6" aria-label="Calculation history">
              <h2 className="text-2xl font-bold text-white">📋 History</h2>
              <ErrorBoundary>
                <HistoryChart entries={history} />
                <HistoryTable entries={history} />
              </ErrorBoundary>
            </section>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-700/50 bg-slate-900/80 py-8 backdrop-blur-lg">
          <div className="mx-auto max-w-6xl px-6 text-center">
            <p className="text-sm text-slate-300">
              Carbon Footprint Awareness Platform — Built with 💚 for a
              sustainable future
            </p>
            <p className="mt-1 text-xs text-slate-400">
              Emission factors sourced from DEFRA 2023, US EPA, ICAO, Our World
              in Data, and IPCC AR6
            </p>
          </div>
        </footer>
      </div>
    </>
  );
};

export default App;
