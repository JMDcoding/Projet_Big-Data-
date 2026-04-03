-- Create flight_disruptions table
-- Créer la table flight_disruptions

CREATE TABLE IF NOT EXISTS flight_disruptions (
    id SERIAL PRIMARY KEY,
    flight_id VARCHAR(255),
    lightning_id VARCHAR(255),
    distance_km FLOAT,
    time_difference_minutes INTEGER,
    risk_level VARCHAR(50),
    disruption_probability FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_disruptions_flight_id ON flight_disruptions(flight_id);
CREATE INDEX IF NOT EXISTS idx_disruptions_lightning_id ON flight_disruptions(lightning_id);
CREATE INDEX IF NOT EXISTS idx_disruptions_risk_level ON flight_disruptions(risk_level);
CREATE INDEX IF NOT EXISTS idx_disruptions_probability ON flight_disruptions(disruption_probability);

-- Verify table structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'flight_disruptions' 
ORDER BY ordinal_position;
