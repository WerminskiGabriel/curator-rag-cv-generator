import os
import json
import psycopg2

# Domyślne ustawienia bazy danych (do zmiany w zależności od ustawień kontenera)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Tworzenie odpowiedniej tabeli, jeśli uzywasz np bazy ofert pracy.
    cur.execute('''
        CREATE TABLE IF NOT EXISTS job_offers (
            slug VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255),
            body TEXT,
            required_skills JSONB
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def save_offer_to_db(offer_data):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        insert_query = '''
            INSERT INTO job_offers (slug, title, body, required_skills)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE
            SET title = EXCLUDED.title,
                body = EXCLUDED.body,
                required_skills = EXCLUDED.required_skills;
        '''

        cur.execute(insert_query, (
            offer_data.get('slug'),
            offer_data.get('title'),
            offer_data.get('body'),
            json.dumps(offer_data.get('required_skills', []))
        ))

        conn.commit()
        cur.close()
        conn.close()
        print(f"Zapisano ofertę: {offer_data.get('slug')}")
    except Exception as e:
        print(f"Błąd przy zapisywaniu do bazy: {e}")

if __name__ == "__main__":
    init_db()