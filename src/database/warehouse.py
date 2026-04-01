"""
Database management for PostgreSQL.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import psycopg2
from psycopg2 import sql


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
            psycopg2.Error: If connection fails
        """
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
