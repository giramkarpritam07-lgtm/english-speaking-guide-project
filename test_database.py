#!/usr/bin/env python3
"""
Test script to verify database functionality and view stored user data.
"""

import sqlite3
from database import DatabaseManager
from datetime import datetime

def display_database_info():
    """Display all database tables and their contents."""
    
    db = DatabaseManager()
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("📊 DATABASE INFORMATION")
    print("="*70)
    
    # Get all users
    print("\n👥 REGISTERED USERS:")
    print("-" * 70)
    cursor.execute("SELECT id, username, email, created_at, last_login FROM users")
    users = cursor.fetchall()
    
    if users:
        print(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Created':<20}")
        print("-" * 70)
        for user in users:
            user_id, username, email, created_at, last_login = user
            print(f"{user_id:<5} {username:<15} {email:<25} {created_at:<20}")
    else:
        print("No users registered yet.")
    
    print(f"\nTotal Users: {db.get_all_users_count()}")
    
    # Get learning history
    print("\n" + "="*70)
    print("📚 LEARNING HISTORY:")
    print("-" * 70)
    cursor.execute("""
        SELECT lh.id, u.username, lh.sentence, lh.correction, lh.timestamp 
        FROM learning_history lh
        JOIN users u ON lh.user_id = u.id
        ORDER BY lh.timestamp DESC
        LIMIT 20
    """)
    history = cursor.fetchall()
    
    if history:
        print(f"{'ID':<5} {'User':<15} {'Original':<30} {'Correction':<30} {'Time':<15}")
        print("-" * 70)
        for record in history:
            rec_id, username, sentence, correction, timestamp = record
            sent_short = sentence[:28] + ".." if len(sentence) > 30 else sentence
            corr_short = correction[:28] + ".." if len(correction) > 30 else correction
            print(f"{rec_id:<5} {username:<15} {sent_short:<30} {corr_short:<30} {timestamp:<15}")
    else:
        print("No learning history yet.")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✅ Database is working correctly!")
    print("="*70 + "\n")

def test_registration():
    """Test registration with a new user."""
    
    print("\n" + "="*70)
    print("🧪 TESTING REGISTRATION")
    print("="*70 + "\n")
    
    db = DatabaseManager()
    
    # Test data
    test_username = f"testuser_{datetime.now().strftime('%H%M%S')}"
    test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
    test_password = "TestPassword123"
    
    print(f"📝 Registering test user:")
    print(f"   Username: {test_username}")
    print(f"   Email: {test_email}")
    print(f"   Password: {test_password}")
    
    success, message = db.register_user(test_username, test_email, test_password)
    
    if success:
        print(f"\n✅ {message}")
        
        # Test authentication
        print(f"\n🔐 Testing authentication...")
        auth_success, user_info = db.authenticate_user(test_username, test_password)
        
        if auth_success:
            user_id, username, email = user_info
            print(f"✅ Authentication successful!")
            print(f"   User ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
        else:
            print(f"❌ Authentication failed!")
    else:
        print(f"\n❌ {message}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    print("\n🗄️  DATABASE MANAGEMENT TOOL")
    print("=" * 70)
    
    # Show current database state
    display_database_info()
    
    # Optionally test registration (uncomment to enable)
    # test_registration()
    # display_database_info()
