import { analyzeLocalRecording } from './analyzeLocalRecording';
import type {
  AnalysisInput,
  AnalysisResult,
  ConfidenceBand,
  PrimaryIntent,
} from '../types/analysis';

export interface CatHumanResultCardData {
  summaryText: string;
  primaryIntent: PrimaryIntent;
  confidenceBand: ConfidenceBand;
  analysis: AnalysisResult;
}

// Small app-facing boundary for "recording finished -> show cat-to-human result".
// The UI can render the minimal card fields directly while keeping the full analysis available.
export function analyzeRecordingForCatHuman(input: AnalysisInput): CatHumanResultCardData {
  const analysis = analyzeLocalRecording(input);

  return {
    summaryText: analysis.summaryText,
    primaryIntent: analysis.primaryIntent,
    confidenceBand: analysis.confidenceBand,
    analysis,
  };
}
