# E-commerce Web Scraper

A comprehensive web scraping solution for major Indian e-commerce platforms using Scrapy. This project scrapes product data from Amazon, Flipkart, BigBasket, and DMart to provide insights into pricing, availability, and product information.

## Features

- **Multi-platform Support**: Scrape data from Amazon, Flipkart, BigBasket, and DMart
- **Comprehensive Data Extraction**: Product names, prices, ratings, reviews, categories, and more
- **Data Export**: Multiple formats including JSON and CSV
- **Data Analysis**: Built-in analysis tools with visualizations
- **Configurable Scraping**: Customize search queries, categories, and page limits
- **Rate Limiting**: Built-in delays and user agent rotation to avoid blocking
- **Error Handling**: Robust error handling and logging

## Supported Platforms

| Platform | URL | Status |
|----------|-----|--------|
| Amazon India | amazon.in | ✅ Supported |
| Flipkart | flipkart.com | ✅ Supported |
| BigBasket | bigbasket.com | ✅ Supported |
| DMart | dmart.in | ✅ Supported |

## Installation

### Prerequisites

- Python 3.13+
- uv (Python package manager)

### Setup

1. **Clone the repository and navigate to the crawler directory:**
   ```bash
   cd crawler
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate  # On Linux/Mac
   # or
   .venv\Scripts\activate     # On Windows
   ```

## Project Structure

```
crawler/
├── ecommerce_scraper/
│   ├── __init__.py
│   ├── items.py              # Data models
│   ├── middlewares.py        # Request/response processing
│   ├── pipelines.py          # Data processing and export
│   ├── settings.py           # Scrapy configuration
│   └── spiders/              # Spider implementations
│       ├── __init__.py
│       ├── amazon_spider.py
│       ├── flipkart_spider.py
│       ├── bigbasket_spider.py
│       └── dmart_spider.py
├── data/                     # Scraped data output
├── charts/                   # Generated visualizations
├── logs/                     # Log files
├── run_spiders.py            # Main execution script
├── data_analyzer.py          # Data analysis tools
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Usage

### Basic Usage

1. **List available spiders:**
   ```bash
   python run_spiders.py --list
   ```

2. **Run a specific spider:**
   ```bash
   # Scrape Amazon for laptops
   python run_spiders.py --spider amazon --search "laptop" --max-pages 3
   
   # Scrape Flipkart electronics category
   python run_spiders.py --spider flipkart --category "electronics" --max-pages 5
   ```

3. **Run all spiders:**
   ```bash
   python run_spiders.py --all --search "smartphone" --max-pages 2
   ```

### Advanced Usage

1. **Custom search queries:**
   ```bash
   python run_spiders.py --spider amazon --search "gaming laptop" --max-pages 5
   ```

2. **Category-based scraping:**
   ```bash
   python run_spiders.py --spider bigbasket --category "fruits-vegetables" --max-pages 3
   ```

3. **Control page limits:**
   ```bash
   python run_spiders.py --all --max-pages 10
   ```

### Data Analysis

After scraping, analyze the collected data:

```bash
# Analyze latest data with visualizations
python data_analyzer.py

# Analyze specific CSV file
python data_analyzer.py --csv "products_20241201_143022.csv"

# Custom output directory for charts
python data_analyzer.py --output-dir "my_charts"

# Export analysis summary
python data_analyzer.py --export "my_analysis.txt"
```

## Configuration

### Scrapy Settings

Key configuration options in `ecommerce_scraper/settings.py`:

- **Download Delay**: `DOWNLOAD_DELAY = 2` (2 seconds between requests)
- **Concurrent Requests**: `CONCURRENT_REQUESTS_PER_DOMAIN = 8`
- **User Agents**: Rotating user agents to avoid detection
- **Retry Settings**: Automatic retry for failed requests
- **Caching**: HTTP caching enabled for better performance

### Customizing Spiders

Each spider supports these parameters:

- `search_query`: Search term for products
- `category`: Product category to scrape
- `max_pages`: Maximum number of pages to scrape

## Data Output

### JSON Format
```json
{
  "product_id": "B08N5WRWNW",
  "product_name": "Echo Dot (4th Gen)",
  "current_price": "3999",
  "original_price": "4999",
  "discount_percentage": "20%",
  "currency": "INR",
  "platform": "Amazon",
  "category": "Electronics",
  "product_rating": 4.5,
  "product_reviews_count": "12500",
  "scraped_at": "2024-12-01T14:30:22"
}
```

### CSV Format
Data is also exported to CSV format with all fields as columns.

## Data Analysis Features

The built-in analyzer provides:

- **Basic Statistics**: Platform distribution, price ranges, ratings
- **Price Analysis**: Price comparisons across platforms and categories
- **Platform Comparison**: Detailed comparison of data quality and coverage
- **Visualizations**: Charts and graphs for better insights
- **Export Options**: Summary reports in text format

## Ethical Considerations

- **Rate Limiting**: Built-in delays to avoid overwhelming servers
- **Robots.txt**: Respects website crawling policies
- **User Agent Rotation**: Uses realistic browser user agents
- **Error Handling**: Graceful handling of blocked requests

## Troubleshooting

### Common Issues

1. **Spider not found:**
   ```bash
   python run_spiders.py --check amazon
   ```

2. **Permission errors:**
   - Ensure you have write permissions in the crawler directory
   - Check if antivirus software is blocking the scripts

3. **Data not being saved:**
   - Verify the `data/` directory exists
   - Check file permissions

4. **Spider blocked:**
   - Increase `DOWNLOAD_DELAY` in settings
   - Add more user agents to the rotation
   - Use proxy rotation (configure in middlewares)

### Debug Mode

Run spiders with increased logging:

```bash
scrapy crawl amazon -L DEBUG
```

## Performance Optimization

- **Concurrent Requests**: Adjust based on target website capacity
- **Download Delays**: Balance between speed and politeness
- **Caching**: HTTP caching reduces redundant requests
- **Pipeline Optimization**: Efficient data processing and storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect the terms of service of the websites you scrape.

## Disclaimer

- This tool is for educational purposes only
- Respect website terms of service and robots.txt
- Use responsibly and ethically
- The authors are not responsible for misuse of this tool

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review Scrapy documentation
3. Check existing GitHub issues
4. Create a new issue with detailed information

## Changelog

### v0.1.0
- Initial release
- Support for Amazon, Flipkart, BigBasket, and DMart
- Basic data extraction and export
- Data analysis tools
- Multi-format output (JSON/CSV)
