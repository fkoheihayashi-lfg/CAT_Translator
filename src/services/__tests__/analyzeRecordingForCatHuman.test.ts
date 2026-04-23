import { analyzeRecordingForCatHuman } from '../analyzeRecordingForCatHuman';
import type { AnalysisInput } from '../../types/analysis';

const base: AnalysisInput = {
  recordingUri: 'local://recordings/test.m4a',
  durationMs: 1500,
  timeBucket: 'morning',
  mealContext: 'before_meal_window',
  ownerContext: 'owner_near',
  environmentTrigger: 'quiet',
  activityContext: 'resting',
  locationContext: 'kitchen',
  clipQuality: 'clean',
};

test('cat-human wrapper exposes minimum result-card fields from local analysis', () => {
  const result = analyzeRecordingForCatHuman(base);

  expect(result.primaryIntent).toBe('food_like');
  expect(result.confidenceBand).toBe('high');
  expect(typeof result.summaryText).toBe('string');
  expect(result.analysis.primaryIntent).toBe(result.primaryIntent);
  expect(result.analysis.confidenceBand).toBe(result.confidenceBand);
  expect(result.analysis.summaryText).toBe(result.summaryText);
});
