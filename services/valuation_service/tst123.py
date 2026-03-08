# test_sync_basic.py (create in valuation-engine/)
import asyncio
from app.db.session import SessionLocal
from app.clients.cse_client import CSEClient
from app.services.cse_service import CSEService
from app.core.config import get_settings

async def test_sync_basic():
    settings = get_settings()
    db = SessionLocal()
    
    try:
        client = CSEClient(
            base_url=settings.cse_base_url,
            api_key=settings.cse_api_key,
            timeout=settings.http_timeout_seconds,
        )
        
        service = CSEService(session=db, client=client)
        
        print("Calling sync_basic_list()...")
        results = await service.sync_basic_list()
        
        print(f"\nSynced {len(results)} securities:")
        for sec in results[:5]:  # Show first 5
            print(f"  {sec.symbol}: {sec.name}")
        
        if len(results) > 5:
            print(f"  ... and {len(results) - 5} more")
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_sync_basic())