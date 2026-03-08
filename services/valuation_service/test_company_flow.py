# test_company_flow.py - Test the complete flow
import asyncio
from app.db.session import SessionLocal
from app.clients.cse_client import CSEClient
from app.services.cse_service import CSEService
from app.core.config import get_settings

async def test_company_flow():
    settings = get_settings()
    db = SessionLocal()
    
    try:
        client = CSEClient(
            base_url=settings.cse_base_url,
            api_key=settings.cse_api_key,
            timeout=settings.http_timeout_seconds,
        )
        
        service = CSEService(session=db, client=client)
        
        # Step 1: Get available companies (without storing)
        print("=" * 60)
        print("STEP 1: Fetching available companies from CSE...")
        print("=" * 60)
        companies = await service.fetch_available_companies()
        print(f"\nFound {len(companies)} companies. Here are first 10:\n")
        for i, company in enumerate(companies[:10], 1):
            print(f"{i}. {company['symbol']:20} - {company['name']}")
        
        if not companies:
            print("No companies found!")
            return
            
        # Step 2: Choose a company (let's pick the first one for demo)
        chosen = companies[0]
        print(f"\n{'=' * 60}")
        print(f"STEP 2: Chosen company: {chosen['symbol']} - {chosen['name']}")
        print("=" * 60)
        
        # Step 3: Fetch and sync full details
        print(f"\nFetching full details for {chosen['symbol']}...")
        details = await service.sync_details_for_symbol(chosen['symbol'])
        
        if not details:
            print(f"Failed to fetch details for {chosen['symbol']}")
            return
        
        # Step 4: Display all the data
        print(f"\n{'=' * 60}")
        print("STEP 3: Full Company Details")
        print("=" * 60)
        print(f"\n📋 Basic Information:")
        print(f"   Symbol: {details.symbol}")
        print(f"   Name: {details.name}")
        print(f"   Sector: {details.sector or 'N/A'}")
        print(f"   Board Type: {details.board_type or 'N/A'}")
        print(f"   Established Year: {details.established_year or 'N/A'}")
        
        print(f"\n💼 Trading Information:")
        print(f"   Issue Date: {details.issue_date or 'N/A'}")
        print(f"   Quantity Issued: {details.quantity_issued:,}" if details.quantity_issued else "   Quantity Issued: N/A")
        print(f"   Market Cap: LKR {details.market_cap:,.2f}" if details.market_cap else "   Market Cap: N/A")
        print(f"   Market Cap %: {details.market_cap_percentage:.4f}%" if details.market_cap_percentage else "   Market Cap %: N/A")
        print(f"   Previous Close: LKR {details.previous_close}" if details.previous_close else "   Previous Close: N/A")
        print(f"   Closing Price: LKR {details.closing_price}" if details.closing_price else "   Closing Price: N/A")
        
        if details.logo_url:
            print(f"\n🖼️  Logo URL: {details.logo_url}")
        
        if details.business_summary:
            summary = details.business_summary[:200] + "..." if len(details.business_summary) > 200 else details.business_summary
            print(f"\n📝 Business Summary:")
            print(f"   {summary}")
        
        print(f"\n📊 Annual Reports ({len(details.annual_reports)}):")
        for i, report in enumerate(details.annual_reports[:3], 1):
            print(f"   {i}. {report.file_text or 'Unnamed Report'}")
            print(f"      URL: {report.url}")
            if report.manual_date:
                print(f"      Date: {report.manual_date.strftime('%Y-%m-%d')}")
        if len(details.annual_reports) > 3:
            print(f"   ... and {len(details.annual_reports) - 3} more")
        
        print(f"\n📊 Quarterly Reports ({len(details.quarterly_reports)}):")
        for i, report in enumerate(details.quarterly_reports[:3], 1):
            print(f"   {i}. {report.file_text or 'Unnamed Report'}")
            print(f"      URL: {report.url}")
            if report.manual_date:
                print(f"      Date: {report.manual_date.strftime('%Y-%m-%d')}")
        if len(details.quarterly_reports) > 3:
            print(f"   ... and {len(details.quarterly_reports) - 3} more")
        
        print(f"\n⏱️  Database Timestamps:")
        print(f"   Created: {details.created_at}")
        print(f"   Updated: {details.updated_at}")
        
        print("\n" + "=" * 60)
        print("✅ Complete! Data is now stored in the database.")
        print("=" * 60)
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_company_flow())
