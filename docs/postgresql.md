# Postgres user management help

This document contains commands for initializing users and a database for this project.

## 0. Login to postgresql
Run this command in terminal

```bash
sudo su - postgres
```

## 1. Create role
Create an App Read/Write role (Group role)
```sql
CREATE ROLE app_rw_group;
GRANT CONNECT ON DATABASE time_table_db TO app_rw_group;
GRANT USAGE ON SCHEMA public TO app_rw_group;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_rw_group;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_rw_group;
```
## 2. Create a user
Create actual users and assign them to groups(user for the Backend Application)
```sql
CREATE USER app_user WITH PASSWORD 'very_strong_password';
GRANT app_rw_group TO app_user;
```

## 3. Set default privileges (Crucial for future tables)
Ensure new tables created in the future automatically get these permissions
```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_rw_group;
```