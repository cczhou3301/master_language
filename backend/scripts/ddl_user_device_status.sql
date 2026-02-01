-- Add status to user_device: 'active' | 'logged_out'. On logout we set status='logged_out' instead of deleting.
-- Run: mysql -u ... -p ... < scripts/ddl_user_device_status.sql
ALTER TABLE user_device
  ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'active' AFTER last_active_at;
