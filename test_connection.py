from database import engine, Base

try:
    # Test connection
    conn = engine.connect()
    print("✅ PostgreSQL connection successful!")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")
    
    conn.close()
    print("🎉 PostgreSQL is ready for your resume scorer!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("💡 Check: 1) Password is correct 2) PostgreSQL service is running")