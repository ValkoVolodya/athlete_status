-- 
-- depends: 

CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    sport_type TEXT,
    checkin_time TIME,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    weight INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT TRUE
);

INSERT INTO questions (text) VALUES
('✅ Чи добре я відновився після попереднього тренування?'),
('✅ Чи мій ранковий пульс у нормі (±5 уд/хв від звичного)?'),
('✅ Чи я виспався (7–8 годин сну, без нічних пробуджень)?'),
('✅ Чи маю мотивацію тренуватись або хоча б настрій “норм”?'),
('✅ Чи мій апетит нормальний (не надто слабкий і не занадто дикий)?'),
('✅ Чи почуваюся спокійним, без роздратованості?'),
('✅ Чи ноги відчуваються “живими” після короткої розминки?');

CREATE TABLE checkins (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER REFERENCES users(telegram_id) ON DELETE CASCADE,
    total_score INTEGER,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE checkin_answers (
    id SERIAL PRIMARY KEY,
    checkin_id INTEGER REFERENCES checkins(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id),
    answer TEXT NOT NULL,
    score INTEGER NOT NULL
);

CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    min_score INTEGER NOT NULL,
    max_score INTEGER NOT NULL,
    text TEXT NOT NULL
);

INSERT INTO recommendations (min_score, max_score, text) VALUES
(0, 3, 'Краще зроби день відпочинку або легке катання в Z1-Z2 🧘'),
(4, 5, 'Поміркуй над легшим тренуванням або коротким Sweet Spot'),
(6, 7, 'Все ок! Тренуйся на максимум 🚴‍♂️');

