from economynext_scraper_selenium import scrape_economynext_dynamic
from dailyft_scraper_selenium import scrape_dailyft_dynamic
from save_csv_utils import save_to_csv

def run_pipeline():
    print("🚀 Running Selenium Data Pipeline...")

    df1 = scrape_economynext_dynamic(pages=3)
    save_to_csv(df1, "economynext_dynamic.csv")

    df2 = scrape_dailyft_dynamic()
    save_to_csv(df2, "dailyft_dynamic.csv")

    print("🎉 Pipeline Completed Successfully!")

if __name__ == "__main__":
    run_pipeline()
