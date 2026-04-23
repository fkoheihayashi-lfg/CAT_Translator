export type TimeBucket = 'early_morning' | 'morning' | 'afternoon' | 'evening' | 'late_night';

export type MealContext =
  | 'before_meal_window'
  | 'after_meal_recent'
  | 'food_visible'
  | 'owner_preparing_food'
  | 'no_food_context';

export type OwnerContext =
  | 'owner_near'
  | 'owner_not_looking'
  | 'owner_interacting'
  | 'owner_left_room'
  | 'owner_returned_home';

export type EnvironmentTrigger =
  | 'quiet'
  | 'after_noise'
  | 'door_or_barrier_present'
  | 'unfamiliar_person'
  | 'unfamiliar_animal'
  | 'other';

export type ActivityContext =
  | 'resting'
  | 'before_play'
  | 'during_play'
  | 'during_pet_or_brush'
  | 'bedtime_or_just_woke';

export type LocationContext = 'kitchen' | 'sofa' | 'bed' | 'window' | 'door' | 'unknown';

export type ClipQuality = 'clean' | 'noisy' | 'unusable';

export type PrimaryIntent =
  | 'food_like'
  | 'attention_like'
  | 'playful'
  | 'curious'
  | 'unsettled'
  | 'sleepy'
  | 'unknown';

export type ConfidenceBand = 'low' | 'medium' | 'high';

export interface AnalysisInput {
  recordingUri: string;
  durationMs: number;
  timeBucket: TimeBucket;
  mealContext: MealContext;
  ownerContext: OwnerContext;
  environmentTrigger: EnvironmentTrigger;
  activityContext: ActivityContext;
  locationContext: LocationContext;
  clipQuality: ClipQuality;
}

export interface AudioFeatures {
  durationMs: number;
  averageAmplitude: number | null; // reserved for Phase 2 signal processing
  peakAmplitude: number | null;    // reserved for Phase 2 signal processing
  silenceRatio: number | null;     // reserved for Phase 2 signal processing
}

export interface AnalysisResult {
  primaryIntent: PrimaryIntent;
  secondaryIntents: PrimaryIntent[];
  confidenceBand: ConfidenceBand;
  summaryText: string;
  catSubtitle: string;
  analysisMode: 'local_heuristic';
  features: AudioFeatures;
  scoreBreakdown: Record<PrimaryIntent, number>;
  reasons: string[];
}
