-- Create tables for SMS Hub application

-- Users table
CREATE TABLE IF NOT EXISTS public.users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    credits FLOAT DEFAULT 0.0,
    is_admin BOOLEAN DEFAULT FALSE,
    sms_rate FLOAT DEFAULT 0.05,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create initial admin user with password hash for 'admin123'
INSERT INTO public.users (username, email, password, credits, is_admin, role)
VALUES 
('admin', 'admin@example.com', 'pbkdf2:sha256:260000$g7YuWo7jgWXRb3mK$6b2cab0cb2a484c5ec3ddab302fb8ba74cf391cc1bd6e94268abe9f7c3dd56f9', 1000.0, TRUE, 'admin')
ON CONFLICT (username) DO NOTHING;

-- Messages table for SMS tracking
CREATE TABLE IF NOT EXISTS public.messages (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE,
    numbers VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    message_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cost FLOAT DEFAULT 0.0
);

-- System settings table
CREATE TABLE IF NOT EXISTS public.system_settings (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial system balance
INSERT INTO public.system_settings (key, value)
VALUES ('system_balance', '1000.0')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Create indexes for better performance with high volume
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON public.messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_status ON public.messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON public.messages(created_at);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_settings ENABLE ROW LEVEL SECURITY;

-- Create policies for users table
CREATE POLICY users_select_policy ON public.users 
    FOR SELECT USING (auth.uid() = id OR 
                     EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND is_admin = true));

CREATE POLICY users_insert_policy ON public.users 
    FOR INSERT WITH CHECK (auth.uid() IN (SELECT id FROM public.users WHERE is_admin = true));

CREATE POLICY users_update_policy ON public.users 
    FOR UPDATE USING (auth.uid() = id OR 
                     EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND is_admin = true));

-- Create policies for messages table
CREATE POLICY messages_select_policy ON public.messages 
    FOR SELECT USING (auth.uid() = user_id OR 
                     EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND is_admin = true));

CREATE POLICY messages_insert_policy ON public.messages 
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policies for system settings
CREATE POLICY system_settings_select_policy ON public.system_settings 
    FOR SELECT USING (EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid()));

CREATE POLICY system_settings_update_policy ON public.system_settings 
    FOR UPDATE USING (EXISTS (SELECT 1 FROM public.users WHERE id = auth.uid() AND is_admin = true)); 