DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS news_article;

CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    personal_email VARCHAR(255) UNIQUE NOT NULL,
    contact_email VARCHAR(255) UNIQUE NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,                       -- Unique identifier for each report
    type VARCHAR(100) NOT NULL,                  -- Type of report (e.g., phishing, scam)
    verdict VARCHAR(100) NOT NULL,               -- Verdict or result of the fraud analysis (e.g., suspicious, safe)
    recommendations TEXT,                        -- Recommendations for the user
    asset_name VARCHAR(255),                        -- unique Associated link or URL (optional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp for when the report was created
);