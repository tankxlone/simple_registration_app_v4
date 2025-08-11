-- Initialize PostgreSQL database for Feedback App
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist
-- Note: PostgreSQL container creates the database automatically based on POSTGRES_DB env var

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE feedback_app TO postgres;

-- Set timezone
SET timezone = 'UTC';

-- Create a custom function for timestamp (if needed)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
