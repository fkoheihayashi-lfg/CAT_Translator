import { analyzeLocalRecording } from '../analyzeLocalRecording';
import type { AnalysisInput } from '../../types/analysis';

// Shared base — override per test
const base: AnalysisInput = {
  recordingUri: 'local://recordings/test.m4a',
  durationMs: 1200,
  timeBucket: 'morning',
  mealContext: 'no_food_context',
  ownerContext: 'owner_near',
  environmentTrigger: 'quiet',
  activityContext: 'resting',
  locationContext: 'sofa',
  clipQuality: 'clean',
};

// --- Happy path ---

test('strong meal context → food_like, high confidence', () => {
  const result = analyzeLocalRecording({
    ...base,
    mealContext: 'before_meal_window',
    locationContext: 'kitchen',
    timeBucket: 'morning',
    durationMs: 1700,
  });
  expect(result.primaryIntent).toBe('food_like');
  expect(result.confidenceBand).toBe('high');
  expect(result.analysisMode).toBe('local_heuristic');
  expect(result.scoreBreakdown.food_like).toBeGreaterThanOrEqual(6);
  expect(result.reasons).toContain('meal window context');
  expect(result.reasons).toContain('kitchen location');
});

test('owner returned home at door → attention_like', () => {
  const result = analyzeLocalRecording({
    ...base,
    ownerContext: 'owner_returned_home',
    locationContext: 'door',
    mealContext: 'no_food_context',
    durationMs: 980,
  });
  expect(result.primaryIntent).toBe('attention_like');
  expect(result.scoreBreakdown.attention_like).toBeGreaterThanOrEqual(5);
  expect(result.reasons).toContain('owner just returned');
  expect(result.reasons).toContain('near door');
});

test('during active play → playful', () => {
  const result = analyzeLocalRecording({
    ...base,
    activityContext: 'during_play',
    ownerContext: 'owner_interacting',
    durationMs: 540,
  });
  expect(result.primaryIntent).toBe('playful');
  expect(result.scoreBreakdown.playful).toBeGreaterThanOrEqual(4);
  expect(result.reasons).toContain('during active play');
});

test('window + door barrier → curious', () => {
  const result = analyzeLocalRecording({
    ...base,
    locationContext: 'window',
    environmentTrigger: 'door_or_barrier_present',
    durationMs: 1100,
  });
  expect(result.primaryIntent).toBe('curious');
  expect(result.scoreBreakdown.curious).toBeGreaterThanOrEqual(6);
  expect(result.reasons).toContain('window location');
  expect(result.reasons).toContain('door or barrier present');
});

test('late night bed + bedtime context → sleepy, high confidence', () => {
  const result = analyzeLocalRecording({
    ...base,
    timeBucket: 'late_night',
    activityContext: 'bedtime_or_just_woke',
    locationContext: 'bed',
    durationMs: 1450,
  });
  expect(result.primaryIntent).toBe('sleepy');
  expect(result.confidenceBand).toBe('high');
  expect(result.scoreBreakdown.sleepy).toBeGreaterThanOrEqual(7);
  expect(result.reasons).toContain('late night time bucket');
  expect(result.reasons).toContain('bedtime or wake context');
  expect(result.reasons).toContain('on the bed');
});

// --- Edge cases ---

test('edge: unusable clip → unknown, low confidence', () => {
  const result = analyzeLocalRecording({
    ...base,
    clipQuality: 'unusable',
    durationMs: 3100,
  });
  expect(result.primaryIntent).toBe('unknown');
  expect(result.confidenceBand).toBe('low');
  expect(result.reasons).toContain('clip unusable');
});

test('edge: very short clip (< 300ms) → unknown', () => {
  const result = analyzeLocalRecording({
    ...base,
    durationMs: 240,
    clipQuality: 'noisy',
    mealContext: 'no_food_context',
    ownerContext: 'owner_left_room',
    environmentTrigger: 'other',
  });
  expect(result.primaryIntent).toBe('unknown');
  expect(result.reasons).toContain('clip too short to read');
});

test('edge: noisy clip with weak context → unknown, low confidence', () => {
  const result = analyzeLocalRecording({
    ...base,
    clipQuality: 'noisy',
    mealContext: 'no_food_context',
    ownerContext: 'owner_left_room',
    environmentTrigger: 'quiet',
    activityContext: 'resting',
    locationContext: 'unknown',
    durationMs: 900,
  });
  expect(result.primaryIntent).toBe('unknown');
  expect(result.confidenceBand).toBe('low');
  expect(result.reasons).toContain('noisy clip with weak context');
});

test('clean context with moderate evidence stays medium, not high', () => {
  const result = analyzeLocalRecording({
    ...base,
    ownerContext: 'owner_returned_home',
    locationContext: 'door',
    mealContext: 'no_food_context',
    durationMs: 980,
  });
  expect(result.primaryIntent).toBe('attention_like');
  expect(result.confidenceBand).toBe('medium');
});

test('edge: after loud noise + owner left room → unsettled', () => {
  const result = analyzeLocalRecording({
    ...base,
    environmentTrigger: 'after_noise',
    ownerContext: 'owner_left_room',
    locationContext: 'bed',
    durationMs: 2100,
  });
  expect(result.primaryIntent).toBe('unsettled');
  expect(result.scoreBreakdown.unsettled).toBeGreaterThanOrEqual(5);
  expect(result.reasons).toContain('after loud noise');
  expect(result.reasons).toContain('owner left room');
});

test('noisy after-noise bed context leans less strongly toward sleepy', () => {
  const result = analyzeLocalRecording({
    ...base,
    clipQuality: 'noisy',
    environmentTrigger: 'after_noise',
    activityContext: 'bedtime_or_just_woke',
    locationContext: 'bed',
    timeBucket: 'late_night',
    durationMs: 1400,
  });
  expect(result.primaryIntent).toBe('sleepy');
  expect(result.confidenceBand).toBe('medium');
  expect(result.scoreBreakdown.sleepy).toBeLessThan(8);
  expect(result.reasons).toContain('after loud noise');
  expect(result.reasons).toContain('on the bed');
});

// --- Shape checks ---

test('result always has required fields with correct analysisMode', () => {
  const result = analyzeLocalRecording(base);
  expect(result.analysisMode).toBe('local_heuristic');
  expect(result.features.averageAmplitude).toBeNull();
  expect(result.features.peakAmplitude).toBeNull();
  expect(result.features.silenceRatio).toBeNull();
  expect(typeof result.summaryText).toBe('string');
  expect(typeof result.catSubtitle).toBe('string');
  expect(Array.isArray(result.secondaryIntents)).toBe(true);
  expect(Array.isArray(result.reasons)).toBe(true);
});
