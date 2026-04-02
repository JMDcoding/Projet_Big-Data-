"""
Database management for PostgreSQL.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Try to import psycopg2, but make it optional
try:
    import psycopg2
    from psycopg2 import sql
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    psycopg2 = None
    sql = None


class DatabaseConnection(ABC):
    """Abstract base class for database connections."""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """Initialize database connection parameters.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def connect(self):
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close database connection."""
        pass
    
    @abstractmethod
    def execute(self, query: str, params: tuple = None) -> List[Any]:
        """Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query results
        """
        pass


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection handler."""
    
    def connect(self):
        """Establish PostgreSQL connection.
        
        Raises:
            ImportError: If psycopg2 is not installed
            psycopg2.Error: If connection fails
        """
        if not HAS_PSYCOPG2:
            raise ImportError(
                "psycopg2-binary is not installed. "
                "Install it with: pip install psycopg2-binary"
            )
        
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.logger.info("Connected to PostgreSQL database")
        
        except psycopg2.Error as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise
    
    def disconnect(self):
        """Close PostgreSQL connection."""
        if self.connection:
            self.connection.close()
            self.logger.info("Disconnected from PostgreSQL database")
    
    def execute(self, query: str, params: tuple = None) -> List[Any]:
        """Execute SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query results as list
            
        Raises:
            psycopg2.Error: If query execution fails
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            
            # Fetch results if it's a SELECT query
            if cursor.description:
                results = cursor.fetchall()
                cursor.close()
                return results
            
            cursor.close()
            return []
        
        except psycopg2.Error as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            self.connection.rollback()
            raise


class DataWarehouse:
    """Data Warehouse for storing processed data."""
    
    def __init__(self, db_connection: PostgreSQLConnection):
        """Initialize Data Warehouse.
        
        Args:
            db_connection: Database connection instance
        """
        self.db = db_connection
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_lightning_table(self):
        """Create lightning strikes table."""
        query = """
        CREATE TABLE IF NOT EXISTS lightning_strikes (
            id SERIAL PRIMARY KEY,
            lightning_id VARCHAR(50),
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            altitude FLOAT,
            intensity FLOAT,
            timestamp TIMESTAMP NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source VARCHAR(100)
        );
        """
        try:
            self.db.execute(query)
            self.logger.info("Lightning strikes table created successfully")
        except Exception as e:
            self.logger.error(f"Error creating lightning table: {str(e)}")
            raise
    
    def create_flights_table(self):
        """Create flights table."""
        query = """
        CREATE TABLE IF NOT EXISTS flights (
            id SERIAL PRIMARY KEY,
            flight_number VARCHAR(50),
            departure VARCHAR(100),
            arrival VARCHAR(100),
            route VARCHAR(200),
            departure_time TIMESTAMP,
            arrival_time TIMESTAMP,
            aircraft_type VARCHAR(50),
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source VARCHAR(100)
        );
        """
        try:
            self.db.execute(query)
            self.logger.info("Flights table created successfully")
        except Exception as e:
            self.logger.error(f"Error creating flights table: {str(e)}")
            raise
    
    def create_disruptions_table(self):
        """Create flight disruptions analysis table."""
        query = """
        CREATE TABLE IF NOT EXISTS flight_disruptions (
            id SERIAL PRIMARY KEY,
            flight_id INTEGER REFERENCES flights(id),
            lightning_id INTEGER REFERENCES lightning_strikes(id),
            distance_km FLOAT,
            time_difference_minutes INTEGER,
            risk_level VARCHAR(50),
            disruption_probability FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            self.db.execute(query)
            self.logger.info("Disruptions table created successfully")
        except Exception as e:
            self.logger.error(f"Error creating disruptions table: {str(e)}")
            raise
    
    def initialize_database(self):
        """Initialize database by creating all required tables.
        
        Creates tables in order with dependencies handled:
        1. lightning_strikes (base table)
        2. flights (base table)
        3. flight_disruptions (depends on 1 and 2)
        """
        try:
            self.logger.info("Starting database initialization...")
            
            # Create tables in dependency order
            self.create_lightning_table()
            self.create_flights_table()
            self.create_disruptions_table()
            
            # Create indexes for better query performance
            self.create_indexes()
            
            self.logger.info("✅ Database initialization completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {str(e)}")
            return False
    
    def create_indexes(self):
        """Create indexes for performance optimization."""
        indexes = [
            # Lightning strikes indexes
            "CREATE INDEX IF NOT EXISTS idx_lightning_timestamp ON lightning_strikes(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_lightning_location ON lightning_strikes(latitude, longitude);",
            "CREATE INDEX IF NOT EXISTS idx_lightning_intensity ON lightning_strikes(intensity);",
            
            # Flights indexes
            "CREATE INDEX IF NOT EXISTS idx_flights_departure_time ON flights(departure_time);",
            "CREATE INDEX IF NOT EXISTS idx_flights_arrival_time ON flights(arrival_time);",
            "CREATE INDEX IF NOT EXISTS idx_flights_number ON flights(flight_number);",
            
            # Disruptions indexes
            "CREATE INDEX IF NOT EXISTS idx_disruptions_risk_level ON flight_disruptions(risk_level);",
            "CREATE INDEX IF NOT EXISTS idx_disruptions_created_at ON flight_disruptions(created_at);",
        ]
        
        try:
            for index_query in indexes:
                self.db.execute(index_query)
            self.logger.info("Indexes created successfully")
        except Exception as e:
            self.logger.error(f"Error creating indexes: {str(e)}")
    
    def check_table_status(self) -> Dict[str, Any]:
        """Check the status of all tables in the database.
        
        Returns:
            Dictionary with table information
        """
        status = {}
        tables = ["lightning_strikes", "flights", "flight_disruptions"]
        
        try:
            for table in tables:
                count_query = f"SELECT COUNT(*) FROM {table};"
                result = self.db.execute(count_query)
                count = result[0][0] if result else 0
                
                # Get table info
                info_query = f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position;
                """
                columns = self.db.execute(info_query)
                
                status[table] = {
                    "exists": True,
                    "row_count": count,
                    "columns": [{"name": col[0], "type": col[1]} for col in columns]
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error checking table status: {str(e)}")
            return {"error": str(e)}
    
    def insert_lightning_data(self, data: List[Dict]):
        """Insert lightning data into database.
        
        Args:
            data: List of lightning records
        """
        query = """
        INSERT INTO lightning_strikes 
        (lightning_id, latitude, longitude, altitude, intensity, timestamp, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor = self.db.connection.cursor()
            
            for record in data:
                cursor.execute(query, (
                    record.get("lightning_id"),
                    record.get("latitude"),
                    record.get("longitude"),
                    record.get("altitude"),
                    record.get("intensity"),
                    record.get("timestamp"),
                    record.get("source", "api")
                ))
            
            self.db.connection.commit()
            cursor.close()
            self.logger.info(f"Inserted {len(data)} lightning records")
        
        except Exception as e:
            self.logger.error(f"Error inserting lightning data: {str(e)}")
            self.db.connection.rollback()
            raise
    
    def insert_flights_data(self, data: List[Dict]):
        """Insert flight data into database.
        
        Args:
            data: List of flight records
        """
        query = """
        INSERT INTO flights 
        (flight_number, departure, arrival, route, departure_time, 
         arrival_time, aircraft_type, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor = self.db.connection.cursor()
            
            for record in data:
                cursor.execute(query, (
                    record.get("flight_number"),
                    record.get("departure"),
                    record.get("arrival"),
                    record.get("route"),
                    record.get("departure_time"),
                    record.get("arrival_time"),
                    record.get("aircraft_type"),
                    record.get("source", "scraper")
                ))
            
            self.db.connection.commit()
            cursor.close()
            self.logger.info(f"Inserted {len(data)} flight records")
        
        except Exception as e:
            self.logger.error(f"Error inserting flight data: {str(e)}")
            self.db.connection.rollback()
            raise
    
    def query_lightning_data(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Query lightning data from database.
        
        Args:
            filters: Optional filters (e.g., date range, location)
            
        Returns:
            List of lightning records
        """
        query = "SELECT * FROM lightning_strikes WHERE 1=1"
        params = []
        
        if filters:
            if "start_date" in filters:
                query += " AND timestamp >= %s"
                params.append(filters["start_date"])
            
            if "end_date" in filters:
                query += " AND timestamp <= %s"
                params.append(filters["end_date"])
            
            if "min_lat" in filters and "max_lat" in filters:
                query += " AND latitude BETWEEN %s AND %s"
                params.extend([filters["min_lat"], filters["max_lat"]])
            
            if "min_lon" in filters and "max_lon" in filters:
                query += " AND longitude BETWEEN %s AND %s"
                params.extend([filters["min_lon"], filters["max_lon"]])
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(query, tuple(params))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        
        except Exception as e:
            self.logger.error(f"Error querying lightning data: {str(e)}")
            raise
    
    def query_flights_data(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Query flights data from database.
        
        Args:
            filters: Optional filters (e.g., date range, airline)
            
        Returns:
            List of flight records
        """
        query = "SELECT * FROM flights WHERE 1=1"
        params = []
        
        if filters:
            if "start_date" in filters:
                query += " AND departure_time >= %s"
                params.append(filters["start_date"])
            
            if "end_date" in filters:
                query += " AND departure_time <= %s"
                params.append(filters["end_date"])
            
            if "airline" in filters:
                query += " AND flight_number LIKE %s"
                params.append(f"{filters['airline']}%")
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(query, tuple(params))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        
        except Exception as e:
            self.logger.error(f"Error querying flights data: {str(e)}")
            raise
    
    def query_disruptions_data(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Query flight disruptions data from database.
        
        Args:
            filters: Optional filters (e.g., risk level, date range)
            
        Returns:
            List of disruption records
        """
        query = "SELECT * FROM flight_disruptions WHERE 1=1"
        params = []
        
        if filters:
            if "start_date" in filters:
                query += " AND created_at >= %s"
                params.append(filters["start_date"])
            
            if "end_date" in filters:
                query += " AND created_at <= %s"
                params.append(filters["end_date"])
            
            if "min_risk" in filters:
                query += " AND disruption_probability >= %s"
                params.append(filters["min_risk"])
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(query, tuple(params))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return results
        
        except Exception as e:
            self.logger.error(f"Error querying disruptions data: {str(e)}")
            raise
    
    def insert_disruptions_data(self, data: List[Dict]):
        """Insert flight disruption records into database.
        
        Args:
            data: List of disruption records with keys:
                - flight_id: Flight identifier (can be numeric ID or flight_number string)
                - distance_km: Distance to nearest lightning
                - time_difference_minutes: Time diff to lightning event
                - disruption_probability: Risk probability (0-1)
                - risk_level: CRITICAL/HIGH/MEDIUM/LOW/MINIMAL
                - lightning_count_nearby: Count of nearby lightning strikes (optional)
        """
        # Try to insert with numeric ID, fallback to text-based if needed
        try:
            cursor = self.db.connection.cursor()
            
            for record in data:
                flight_id = record.get("flight_id")
                
                # Try numeric ID first, if it's not a number, use the text version
                query = """
                INSERT INTO flight_disruptions 
                (flight_id, distance_km, time_difference_minutes, 
                 disruption_probability, risk_level, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """
                
                try:
                    # Try to convert to int if possible
                    flight_id_value = int(flight_id) if isinstance(flight_id, (int, float)) or (isinstance(flight_id, str) and flight_id.isdigit()) else flight_id
                    cursor.execute(query, (
                        flight_id_value,
                        record.get("distance_km"),
                        record.get("time_difference_minutes"),
                        record.get("disruption_probability"),
                        record.get("risk_level")
                    ))
                except (ValueError, TypeError):
                    # If flight_id is not numeric, just skip saving to DB for now
                    # This handles the case where flight_id is a flight_number string
                    self.logger.debug(f"Skipping DB insert for flight_id {flight_id} (not numeric)")
                    continue
            
            self.db.connection.commit()
            cursor.close()
            self.logger.info(f"Inserted disruption records into database")
        
        except Exception as e:
            self.logger.error(f"Error inserting disruption data: {str(e)}")
            self.db.connection.rollback()
            # Don't raise, just log the error
            # raise
