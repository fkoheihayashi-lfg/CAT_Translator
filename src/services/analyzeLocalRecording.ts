import type {
  AnalysisInput,
  AnalysisResult,
  AudioFeatures,
  ClipQuality,
  PrimaryIntent,
} from '../types/analysis';

// --- Feature extraction ---
// Phase 1: durationMs is real. Amplitude/silence are reserved for Phase 2 audio processing.
function extractFeatures(input: AnalysisInput): AudioFeatures {
  return {
    durationMs: input.durationMs,
    averageAmplitude: null,
    peakAmplitude: null,
    silenceRatio: null,
  };
}

// --- Scoring ---

type Scores = Record<PrimaryIntent, number>;

function scoreAll(input: AnalysisInput, features: AudioFeatures): [Scores, string[]] {
  const s: Scores = {
    food_like: 0,
    attention_like: 0,
    playful: 0,
    curious: 0,
    unsettled: 0,
    sleepy: 0,
    unknown: 0,
  };
  const reasons: string[] = [];

  const {
    mealContext,
    ownerContext,
    environmentTrigger,
    activityContext,
    locationContext,
    timeBucket,
    clipQuality,
  } = input;
  const { durationMs } = features;

  // food_like
  if (mealContext === 'before_meal_window')    { s.food_like += 3; reasons.push('meal window context'); }
  if (mealContext === 'food_visible')          { s.food_like += 3; reasons.push('food visible'); }
  if (mealContext === 'owner_preparing_food')  { s.food_like += 2; reasons.push('owner preparing food'); }
  if (locationContext === 'kitchen')           { s.food_like += 2; reasons.push('kitchen location'); }
  if (timeBucket === 'morning' || timeBucket === 'evening') s.food_like += 1;
  if (durationMs >= 500 && durationMs <= 2000) s.food_like += 1;

  // attention_like
  if (ownerContext === 'owner_returned_home')  { s.attention_like += 3; reasons.push('owner just returned'); }
  if (ownerContext === 'owner_not_looking')    { s.attention_like += 2; reasons.push('owner not looking'); }
  if (ownerContext === 'owner_near')             s.attention_like += 1;
  if (locationContext === 'door')              { s.attention_like += 2; reasons.push('near door'); }
  if (locationContext === 'sofa')                s.attention_like += 1;
  if (mealContext === 'after_meal_recent')     { s.attention_like += 1; reasons.push('after recent meal'); }

  // playful
  if (activityContext === 'during_play')  { s.playful += 3; reasons.push('during active play'); }
  if (activityContext === 'before_play')  { s.playful += 3; reasons.push('pre-play context'); }
  if (ownerContext === 'owner_interacting') { s.playful += 1; reasons.push('owner interacting'); }
  if (durationMs > 0 && durationMs < 800) { s.playful += 1; reasons.push('short clip duration'); }

  // curious
  if (locationContext === 'window')                 { s.curious += 3; reasons.push('window location'); }
  if (environmentTrigger === 'door_or_barrier_present') { s.curious += 3; reasons.push('door or barrier present'); }
  if (environmentTrigger === 'other')               { s.curious += 1; reasons.push('unusual trigger'); }
  if (durationMs >= 500 && durationMs <= 1500)        s.curious += 1;

  // unsettled
  if (environmentTrigger === 'after_noise')       { s.unsettled += 3; reasons.push('after loud noise'); }
  if (environmentTrigger === 'unfamiliar_person') { s.unsettled += 3; reasons.push('unfamiliar person present'); }
  if (environmentTrigger === 'unfamiliar_animal') { s.unsettled += 3; reasons.push('unfamiliar animal present'); }
  if (ownerContext === 'owner_left_room')          { s.unsettled += 2; reasons.push('owner left room'); }
  if (durationMs > 1500)                            s.unsettled += 1;

  // sleepy
  if (activityContext === 'bedtime_or_just_woke') { s.sleepy += 3; reasons.push('bedtime or wake context'); }
  if (timeBucket === 'late_night')                { s.sleepy += 2; reasons.push('late night time bucket'); }
  if (timeBucket === 'early_morning')               s.sleepy += 1;
  if (locationContext === 'bed')                  { s.sleepy += 2; reasons.push('on the bed'); }
  if (activityContext === 'resting')                s.sleepy += 1;
  if (locationContext === 'sofa' && activityContext === 'resting') s.sleepy += 1;
  if (durationMs > 1000)                            s.sleepy += 1;

  // Slightly soften sleepy when noisy bed-style context overlaps with a recent noise cue.
  // This keeps the read more tentative without forcing a different label.
  if (environmentTrigger === 'after_noise' && clipQuality === 'noisy' && s.sleepy > 0) {
    s.sleepy = Math.max(0, s.sleepy - 2);
  } else if (
    clipQuality === 'noisy'
    && locationContext === 'bed'
    && (activityContext === 'resting' || activityContext === 'bedtime_or_just_woke')
    && s.sleepy > 0
  ) {
    s.sleepy = Math.max(0, s.sleepy - 1);
  }

  // unknown — force or boost when signal is too weak to interpret
  if (clipQuality === 'unusable') {
    s.unknown += 10;
    reasons.push('clip unusable');
  }
  if (durationMs > 0 && durationMs < 300) {
    s.unknown += 3;
    reasons.push('clip too short to read');
  }
  const maxContentScore = Math.max(
    s.food_like, s.attention_like, s.playful, s.curious, s.unsettled, s.sleepy,
  );
  if (clipQuality === 'noisy' && maxContentScore <= 2) {
    s.unknown += 2;
    reasons.push('noisy clip with weak context');
  }

  return [s, reasons];
}

// --- Intent derivation ---

function topIntent(scores: Scores): PrimaryIntent {
  return (Object.keys(scores) as PrimaryIntent[]).reduce(
    (best, k) => (scores[k] > scores[best] ? k : best),
    'unknown' as PrimaryIntent,
  );
}

function deriveSecondary(primary: PrimaryIntent, scores: Scores): PrimaryIntent[] {
  const topScore = scores[primary];
  const threshold = Math.max(2, topScore * 0.5);
  return (Object.keys(scores) as PrimaryIntent[])
    .filter(k => k !== primary && k !== 'unknown' && scores[k] >= threshold)
    .sort((a, b) => scores[b] - scores[a])
    .slice(0, 2);
}

function deriveConfidence(
  primary: PrimaryIntent,
  scores: Scores,
  clipQuality: ClipQuality,
): 'low' | 'medium' | 'high' {
  if (primary === 'unknown' || clipQuality === 'unusable') return 'low';

  const sorted = Object.values(scores).sort((a, b) => b - a);
  const topScore = sorted[0];
  const gap = topScore - (sorted[1] ?? 0);

  if (clipQuality === 'noisy') return topScore >= 4 && gap >= 2 ? 'medium' : 'low';

  if (topScore >= 6 && gap >= 3) return 'high';
  if (topScore >= 3 && gap >= 2) return 'medium';
  return 'low';
}

// --- Reply generation ---

const SUMMARY_TEXT: Record<PrimaryIntent, string> = {
  food_like:
    'Sounds like food might be on the mind — these kinds of vocalizations often show up around meal time.',
  attention_like:
    'Seems like your cat might be looking for a bit of company right now.',
  playful:
    "Sounds like play mode might be activating — something's caught the hunting instinct.",
  curious:
    'Something nearby seems to have caught some serious attention.',
  unsettled:
    'Sounds like something in the environment might have been a little startling or unexpected.',
  sleepy:
    'Seems like winding down time — this kind of sound often comes just before a long nap.',
  unknown:
    "Hard to say with this one — the signal wasn't strong enough to read clearly.",
};

const CAT_SUBTITLE: Record<PrimaryIntent, string> = {
  food_like:        'Keeping a close eye on the bowl situation',
  attention_like:   "Just checking if you're paying attention",
  playful:          'Ready for something to chase',
  curious:          'Watching something very carefully',
  unsettled:        'Not totally sure about that noise',
  sleepy:           'Almost definitely about to nap',
  unknown:          'Keeping their thoughts private',
};

// --- Main export ---

export function analyzeLocalRecording(input: AnalysisInput): AnalysisResult {
  const features = extractFeatures(input);
  const [scores, rawReasons] = scoreAll(input, features);
  const primary = topIntent(scores);
  const secondary = deriveSecondary(primary, scores);
  const confidence = deriveConfidence(primary, scores, input.clipQuality);

  return {
    primaryIntent: primary,
    secondaryIntents: secondary,
    confidenceBand: confidence,
    summaryText: SUMMARY_TEXT[primary],
    catSubtitle: CAT_SUBTITLE[primary],
    analysisMode: 'local_heuristic',
    features,
    scoreBreakdown: scores,
    reasons: [...new Set(rawReasons)],
  };
}
