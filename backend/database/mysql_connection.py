import mysql.connector


def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",      # <-- Leave blank for now
        )

        print("✅ Connected to MySQL Successfully!")

        return connection

    except Exception as e:
        print("❌ Connection Failed")
        print(e)


if __name__ == "__main__":
    conn = get_connection()

    if conn:
        conn.close()