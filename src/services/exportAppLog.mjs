import { basename } from 'node:path';

const VALID_TENDENCY = new Set([
  'attention_like',
  'food_like',
  'playful',
  'curious',
  'unsettled',
  'sleepy',
  'unknown',
]);

const VALID_QUALITY = new Set(['clean', 'noisy', 'unusable']);
const VALID_CONFIDENCE = new Set(['low', 'medium', 'high']);
const VALID_TIME_BUCKET = new Set(['early_morning', 'morning', 'afternoon', 'evening', 'late_night']);
const VALID_MEAL_CONTEXT = new Set([
  'before_meal_window',
  'after_meal_recent',
  'food_visible',
  'owner_preparing_food',
  'no_food_context',
]);
const VALID_OWNER_CONTEXT = new Set([
  'owner_near',
  'owner_not_looking',
  'owner_interacting',
  'owner_left_room',
  'owner_returned_home',
]);
const VALID_ENVIRONMENT_TRIGGER = new Set([
  'quiet',
  'after_noise',
  'door_or_barrier_present',
  'unfamiliar_person',
  'unfamiliar_animal',
  'other',
]);
const VALID_ACTIVITY_CONTEXT = new Set([
  'resting',
  'before_play',
  'during_play',
  'during_pet_or_brush',
  'bedtime_or_just_woke',
]);
const VALID_LOCATION_CONTEXT = new Set(['kitchen', 'sofa', 'bed', 'window', 'door', 'unknown']);
const VALID_OBSERVED_OUTCOME = new Set(['no_clear_outcome']);

const DEFAULTS = {
  cat_id: 'momo',
  duration_ms: 1000,
  clip_quality: 'noisy',
  time_bucket: 'morning',
  meal_context: 'no_food_context',
  owner_context: 'owner_near',
  environment_trigger: 'quiet',
  activity_context: 'resting',
  location_context: 'unknown',
  primary_tendency: 'unknown',
  secondary_tendency: null,
  observed_outcome: 'no_clear_outcome',
  labeler_confidence: 'low',
};

function pickFirst(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null && value !== '') {
      return value;
    }
  }
  return undefined;
}

function normalizeChoice(value, validValues, fallback) {
  return typeof value === 'string' && validValues.has(value) ? value : fallback;
}

function normalizeDuration(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) && numeric > 0 ? Math.round(numeric) : DEFAULTS.duration_ms;
}

function normalizeIsoDate(value) {
  if (typeof value !== 'string' || !value.trim()) {
    return '';
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? '' : value.trim();
}

function deriveTimeBucket(rawValue) {
  if (typeof rawValue !== 'string' || !rawValue.trim()) {
    return DEFAULTS.time_bucket;
  }

  const match = rawValue.trim().match(/T(\d{2}):\d{2}/);
  if (!match) {
    return DEFAULTS.time_bucket;
  }

  const hour = Number(match[1]);
  if (!Number.isFinite(hour)) {
    return DEFAULTS.time_bucket;
  }

  if (hour >= 5 && hour < 8) return 'early_morning';
  if (hour >= 8 && hour < 12) return 'morning';
  if (hour >= 12 && hour < 17) return 'afternoon';
  if (hour >= 17 && hour < 22) return 'evening';
  return 'late_night';
}

function deriveRecordingId(entry, createdAt) {
  const directId = pickFirst(entry.recording_id, entry.recordingId, entry.id, entry.logId, entry.entryId);
  if (directId) {
    return String(directId);
  }

  const recordingUri = pickFirst(
    entry.recording_uri,
    entry.recordingUri,
    entry.analysisInput?.recordingUri,
    entry.input?.recordingUri,
  );
  if (typeof recordingUri === 'string' && recordingUri.trim()) {
    const leaf = basename(recordingUri.trim());
    const dot = leaf.lastIndexOf('.');
    return dot > 0 ? leaf.slice(0, dot) : leaf;
  }

  if (createdAt && entry.index !== undefined) {
    return `app_log_${createdAt.replace(/[^0-9]/g, '').slice(0, 14)}_${entry.index}`;
  }

  return '';
}

function buildNote(entry, analysisSummary) {
  const notes = [];
  const rawNote = pickFirst(entry.note, entry.notes, entry.userNote, entry.labelNote);
  if (typeof rawNote === 'string' && rawNote.trim()) {
    notes.push(rawNote.trim());
  }

  if (analysisSummary) {
    notes.push(`app summary: ${analysisSummary}`);
  }

  const sourceId = pickFirst(entry.id, entry.logId, entry.entryId);
  if (sourceId) {
    notes.push(`source_log_id=${sourceId}`);
  }

  notes.push('imported from app log export');
  return notes.join(' | ');
}

export function normalizeAppLogEntry(rawEntry, index = 0) {
  const entry = rawEntry && typeof rawEntry === 'object' ? rawEntry : {};
  const analysisInput = entry.analysisInput ?? entry.input ?? {};
  const analysisResult = entry.analysisResult ?? entry.result ?? {};

  const rawCreatedAt = pickFirst(entry.created_at, entry.createdAt, entry.timestamp, entry.loggedAt);
  const createdAt = normalizeIsoDate(rawCreatedAt);

  const timeBucketValue = pickFirst(entry.time_bucket, entry.timeBucket, analysisInput.timeBucket);
  const timeBucket = normalizeChoice(
    timeBucketValue,
    VALID_TIME_BUCKET,
    deriveTimeBucket(typeof rawCreatedAt === 'string' ? rawCreatedAt : createdAt),
  );

  const summaryText = pickFirst(entry.summaryText, analysisResult.summaryText);
  const catSubtitle = pickFirst(entry.catSubtitle, analysisResult.catSubtitle);
  const analysisMode = pickFirst(entry.analysisMode, analysisResult.analysisMode, 'local_heuristic');

  return {
    source_log_id: pickFirst(entry.id, entry.logId, entry.entryId, '') || '',
    recording_id: deriveRecordingId({ ...entry, index }, createdAt),
    cat_id: String(pickFirst(entry.cat_id, entry.catId, DEFAULTS.cat_id)),
    created_at: createdAt,
    recording_uri: String(
      pickFirst(entry.recording_uri, entry.recordingUri, analysisInput.recordingUri, '') || '',
    ),
    duration_ms: normalizeDuration(
      pickFirst(entry.duration_ms, entry.durationMs, analysisInput.durationMs),
    ),
    clip_quality: normalizeChoice(
      pickFirst(entry.clip_quality, entry.clipQuality, analysisInput.clipQuality),
      VALID_QUALITY,
      DEFAULTS.clip_quality,
    ),
    time_bucket: timeBucket,
    meal_context: normalizeChoice(
      pickFirst(entry.meal_context, entry.mealContext, analysisInput.mealContext),
      VALID_MEAL_CONTEXT,
      DEFAULTS.meal_context,
    ),
    owner_context: normalizeChoice(
      pickFirst(entry.owner_context, entry.ownerContext, analysisInput.ownerContext),
      VALID_OWNER_CONTEXT,
      DEFAULTS.owner_context,
    ),
    environment_trigger: normalizeChoice(
      pickFirst(entry.environment_trigger, entry.environmentTrigger, analysisInput.environmentTrigger),
      VALID_ENVIRONMENT_TRIGGER,
      DEFAULTS.environment_trigger,
    ),
    activity_context: normalizeChoice(
      pickFirst(entry.activity_context, entry.activityContext, analysisInput.activityContext),
      VALID_ACTIVITY_CONTEXT,
      DEFAULTS.activity_context,
    ),
    location_context: normalizeChoice(
      pickFirst(entry.location_context, entry.locationContext, analysisInput.locationContext),
      VALID_LOCATION_CONTEXT,
      DEFAULTS.location_context,
    ),
    primary_tendency: normalizeChoice(
      pickFirst(entry.primary_tendency, entry.primaryTendency, analysisResult.primaryIntent),
      VALID_TENDENCY,
      DEFAULTS.primary_tendency,
    ),
    secondary_tendency: normalizeChoice(
      pickFirst(entry.secondary_tendency, entry.secondaryTendency, analysisResult.secondaryIntents?.[0]),
      VALID_TENDENCY,
      DEFAULTS.secondary_tendency,
    ),
    observed_outcome: normalizeChoice(
      pickFirst(entry.observed_outcome, entry.observedOutcome),
      VALID_OBSERVED_OUTCOME,
      DEFAULTS.observed_outcome,
    ),
    labeler_confidence: normalizeChoice(
      pickFirst(entry.labeler_confidence, entry.labelerConfidence, analysisResult.confidenceBand),
      VALID_CONFIDENCE,
      DEFAULTS.labeler_confidence,
    ),
    note: buildNote(entry, typeof summaryText === 'string' ? summaryText.trim() : ''),
    app_summary_text: typeof summaryText === 'string' ? summaryText.trim() : '',
    app_cat_subtitle: typeof catSubtitle === 'string' ? catSubtitle.trim() : '',
    app_analysis_mode: typeof analysisMode === 'string' ? analysisMode : 'local_heuristic',
  };
}

export function buildAppLogExportPayload(rawEntries, options = {}) {
  const entries = Array.isArray(rawEntries) ? rawEntries : [];
  const exportedAt = normalizeIsoDate(options.exportedAt) || new Date().toISOString();

  return {
    export_version: 1,
    exported_at: exportedAt,
    source: 'cat_translator_app_log',
    entry_count: entries.length,
    entries: entries.map((entry, index) => normalizeAppLogEntry(entry, index)),
  };
}

export function stringifyAppLogExport(rawEntries, options = {}) {
  return JSON.stringify(buildAppLogExportPayload(rawEntries, options), null, 2);
}
