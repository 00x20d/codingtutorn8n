CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT NOT NULL UNIQUE,  -- Changed to BIGINT
    username TEXT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_user_id ON users(user_id);

CREATE TABLE learning_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id SERIAL NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,  -- Changed to BIGINT
    topic_id INTEGER NOT NULL,
    session_type TEXT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    topic_name VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_learning_sessions_user ON learning_sessions(user_id);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id INTEGER NOT NULL,
    session_id SERIAL NOT NULL UNIQUE,
    telegram_user_id BIGINT NOT NULL,  -- Changed to BIGINT
    telegram_chat_id BIGINT NOT NULL,
    is_bot BOOLEAN NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_telegram ON conversations(telegram_chat_id, telegram_user_id);
