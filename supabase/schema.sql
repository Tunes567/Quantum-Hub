-- Create tables for SMS Hub application

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    credits FLOAT DEFAULT 0.0,
    is_admin BOOLEAN DEFAULT FALSE,
    sms_rate FLOAT DEFAULT 0.05,
    role TEXT DEFAULT 'user',
    auth_id UUID -- Add this to link to Supabase auth
);

-- Create initial admin user with password hash
INSERT INTO users (username, email, password, credits, is_admin, role)
VALUES 
('admin', 'admin@example.com', 'pbkdf2:sha256:260000$g7YuWo7jgWXRb3mK$6b2cab0cb2a484c5ec3ddab302fb8ba74cf391cc1bd6e94268abe9f7c3dd56f9', 1000.0, TRUE, 'admin')
ON CONFLICT (username) DO NOTHING;

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    numbers TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    message_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cost FLOAT DEFAULT 0.0
);

-- System settings table
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Initialize system balance
INSERT INTO system_settings (key, value)
VALUES ('system_balance', '1000.0')
ON CONFLICT (key) DO NOTHING;

-- Create indexes for better performance with high volume
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Create a function to check if a user is an admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM users 
        WHERE auth_id = auth.uid() AND is_admin = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enable Row Level Security (only if needed for this application)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Create simplified policies that will actually work
-- These allow public access initially since we're handling authentication in our application
CREATE POLICY "Allow full access to all tables" ON users FOR ALL USING (true);
CREATE POLICY "Allow full access to all tables" ON messages FOR ALL USING (true);
CREATE POLICY "Allow full access to all tables" ON system_settings FOR ALL USING (true); 