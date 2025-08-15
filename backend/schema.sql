-- backend/schema.sql
CREATE TABLE game_sessions (
    id SERIAL PRIMARY KEY,
    room_type VARCHAR(50),
    prompt TEXT NOT NULL,
    human_response TEXT,
    ai_response TEXT,
    judge_prediction JSONB, -- {human_prob: 0.7, reasoning: "..."}
    actual_labels JSONB,    -- {human: 0, ai: 1}
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    human_wins INTEGER DEFAULT 0,
    ai_detection_score INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0
);

CREATE TABLE training_batches (
    id SERIAL PRIMARY KEY,
    misclassified_examples JSONB,
    model_version VARCHAR(20),
    training_started_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);