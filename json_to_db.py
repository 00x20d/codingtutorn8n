import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from typing import Dict, List, Any


class DatabaseLoader:
    def __init__(self, db_params: Dict[str, str]):
        self.conn = psycopg2.connect(**db_params)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cur.close()
        self.conn.close()

    def insert_category(self, category_name: str) -> int:
        """Insert a category and return its ID"""
        self.cur.execute(
            "INSERT INTO categories (category_name) VALUES (%s) ON CONFLICT (category_name) DO UPDATE SET category_name = EXCLUDED.category_name RETURNING category_id",
            (category_name,),
        )
        return self.cur.fetchone()[0]

    def insert_subcategory(self, category_id: int, subcategory_name: str) -> int:
        """Insert a subcategory and return its ID"""
        self.cur.execute(
            """
            INSERT INTO subcategories (category_id, subcategory_name)
            VALUES (%s, %s)
            ON CONFLICT (category_id, subcategory_name) DO UPDATE 
            SET subcategory_name = EXCLUDED.subcategory_name
            RETURNING subcategory_id
            """,
            (category_id, subcategory_name),
        )
        return self.cur.fetchone()[0]

    def insert_topics(self, subcategory_id: int, topics: List[str]):
        """Insert multiple topics for a subcategory"""
        topic_data = [
            (subcategory_id, topic, idx) for idx, topic in enumerate(topics, 1)
        ]
        # Drop the temporary table if it exists
        self.cur.execute("DROP TABLE IF EXISTS temp_topics")
        
        self.cur.execute(
            """
            CREATE TEMP TABLE temp_topics (
                subcategory_id INTEGER,
                topic_name VARCHAR(200),
                topic_order INTEGER
            ) ON COMMIT DROP
            """
        )
        execute_values(
            self.cur,
            "INSERT INTO temp_topics (subcategory_id, topic_name, topic_order) VALUES %s",
            topic_data,
        )
        self.cur.execute(
            """
            INSERT INTO topics (subcategory_id, topic_name, topic_order)
            SELECT subcategory_id, topic_name, topic_order FROM temp_topics
            ON CONFLICT (subcategory_id, topic_name) 
            DO UPDATE SET topic_order = EXCLUDED.topic_order
            """
        )


def load_json_to_db(json_file_path: str, db_params: Dict[str, str]):
    """Main function to load JSON data into the database"""
    # Read JSON file
    with open(json_file_path, "r") as f:
        data = json.load(f)

    # Process frontend data
    frontend_data = data.get("Frontend", {})

    with DatabaseLoader(db_params) as db:
        # Insert main category
        frontend_category_id = db.insert_category("Frontend Development")

        # Process each subcategory and its topics
        for subcategory_name, topics in frontend_data.items():
            subcategory_id = db.insert_subcategory(
                frontend_category_id, subcategory_name
            )
            if topics:  # Only insert if there are topics
                db.insert_topics(subcategory_id, topics)


if __name__ == "__main__":
    # Database connection parameters
    db_params = {
        "dbname": "coding_tutor_demo",
        "user": "danieljurgens",
        "password": "",
        "host": "localhost",
        "port": "5432",
    }

    json_file_path = "frontend.json"

    try:
        load_json_to_db(json_file_path, db_params)
        print("Data successfully loaded into the database!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
