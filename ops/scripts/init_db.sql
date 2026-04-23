CREATE TABLE IF NOT EXISTS vocalizations (
  recording_id TEXT PRIMARY KEY,
  cat_id TEXT,
  created_at TEXT,
  recording_uri TEXT,
  duration_ms INTEGER,
  clip_quality TEXT,
  time_bucket TEXT,
  meal_context TEXT,
  owner_context TEXT,
  environment_trigger TEXT,
  activity_context TEXT,
  location_context TEXT,
  primary_tendency TEXT,
  secondary_tendency TEXT,
  observed_outcome TEXT,
  labeler_confidence TEXT,
  note TEXT
);
