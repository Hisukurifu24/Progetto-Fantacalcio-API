#!/usr/bin/env python3
"""
Test script to validate the Fantasy Football API setup
"""
import sys
import os
import asyncio

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test FastAPI import
        import fastapi
        print("✓ FastAPI imported successfully")
        
        # Test Pydantic import  
        import pydantic
        print("✓ Pydantic imported successfully")
        
        # Test our app modules
        from app.models import Player, MatchRating, PlayerRole
        print("✓ App models imported successfully")
        
        from app.services import DataManager, ScraperService
        print("✓ App services imported successfully")
        
        from app.routes import players, matches, scrapers
        print("✓ App routes imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return False

async def test_data_manager():
    """Test DataManager functionality"""
    print("\nTesting DataManager...")
    
    try:
        from app.services.data_manager import DataManager
        
        dm = DataManager()
        print("✓ DataManager created")
        
        # Test data loading (will work even if files don't exist)
        await dm.initialize()
        print("✓ DataManager initialized")
        
        # Get stats
        stats = dm.get_data_stats()
        print(f"✓ Data stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ DataManager test failed: {e}")
        return False

async def test_models():
    """Test Pydantic models"""
    print("\nTesting Pydantic models...")
    
    try:
        from app.models import Player, MatchRating, PlayerRole, PlayerStatus
        
        # Test Player model
        player = Player(
            nome="Test Player",
            squadra="Test Team", 
            ruolo=PlayerRole.A,
            quotazione_attuale_classico=25.0
        )
        print(f"✓ Player model: {player.nome}")
        
        # Test MatchRating model
        rating = MatchRating(
            nome="Test Player",
            squadra="Test Team",
            ruolo=PlayerRole.A,
            voto=7.5,
            gol=1,
            assist=0
        )
        print(f"✓ MatchRating model: {rating.nome} - {rating.voto}")
        
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def check_external_scripts():
    """Check if external scraper scripts exist"""
    print("\nChecking external scraper scripts...")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    quotazioni_script = os.path.join(base_dir, "Estrai listone", "src", "quotazioni_scraper.py")
    voti_script = os.path.join(base_dir, "Estrai voti", "src", "voti_scraper.py")
    
    if os.path.exists(quotazioni_script):
        print("✓ Quotazioni scraper found")
    else:
        print(f"⚠️  Quotazioni scraper not found at: {quotazioni_script}")
    
    if os.path.exists(voti_script):
        print("✓ Voti scraper found")
    else:
        print(f"⚠️  Voti scraper not found at: {voti_script}")

async def main():
    """Run all tests"""
    print("🧪 Fantasy Football API - Setup Validation")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not await test_imports():
        success = False
    
    # Test models
    if not await test_models():
        success = False
    
    # Test data manager
    if not await test_data_manager():
        success = False
    
    # Check external scripts
    check_external_scripts()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The API is ready to run.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Test the endpoints!")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
