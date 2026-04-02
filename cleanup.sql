-- Cleanup script for PostgreSQL - Run with:
-- psql -h localhost -p 5433 -U postgres -d lightning_db -f cleanup.sql

-- Delete all demo data from tables
DELETE FROM trajectories;
DELETE FROM disruptions;
DELETE FROM flights;
DELETE FROM lightning;

-- Verify deletion
SELECT COUNT(*) as total_lightning FROM lightning;
SELECT COUNT(*) as total_flights FROM flights;
SELECT COUNT(*) as total_disruptions FROM disruptions;
SELECT COUNT(*) as total_trajectories FROM trajectories;

-- Output
SELECT 'Cleanup completed successfully!' as status;
