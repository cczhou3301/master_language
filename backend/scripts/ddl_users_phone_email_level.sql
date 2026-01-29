-- Migrate users: phone nullable/longer, add email and level (run if tables already exist)
-- mysql -u master_language -p master_language < scripts/ddl_users_phone_email_level.sql

SET NAMES utf8mb4;

-- phone: allow NULL and up to 32 chars; add email (unique), level
ALTER TABLE `users`
  MODIFY COLUMN `phone` VARCHAR(32) NULL,
  ADD COLUMN `email` VARCHAR(255) NULL AFTER `phone`,
  ADD COLUMN `level` INT NOT NULL DEFAULT 0 AFTER `is_active`,
  ADD UNIQUE KEY `idx_email` (`email`);
