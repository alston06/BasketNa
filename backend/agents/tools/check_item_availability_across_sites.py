import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


def check_item_availability_across_sites(product_name: str, site: str = "all") -> dict:
    """
    Check current item (stock) availability across sites.
    """
    def check_amazon(product_name):
        try:
            search_url = f"https://www.amazon.in/s?k={quote(product_name)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            link = soup.select_one('a.a-link-normal.s-no-outline')
            href = link.get('href') if link else None
            if not href:
                return "Unknown"
            product_url = "https://www.amazon.in" + str(href)
            prod_resp = requests.get(product_url, headers=headers, timeout=10)
            prod_soup = BeautifulSoup(prod_resp.text, 'html.parser')
            availability_tag = prod_soup.select_one('#availability span')
            if availability_tag:
                text = availability_tag.get_text(strip=True)
                if re.search(r'in stock', text, re.I):
                    return "In stock"
                elif re.search(r'out of stock', text, re.I):
                    return "Out of stock"
                elif re.search(r'pre-order', text, re.I):
                    return "Pre-order"
                elif re.search(r'limited', text, re.I):
                    return "Limited stock"
                else:
                    return text
            return "Unknown"
        except Exception:
            return "Unknown"
    def check_flipkart(product_name):
        try:
            search_url = f"https://www.flipkart.com/search?q={quote(product_name)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            link = soup.select_one('a._1fQZEK') or soup.select_one('a.s1Q9rs')
            href = link.get('href') if link else None
            if not href:
                return "Unknown"
            product_url = "https://www.flipkart.com" + str(href)
            prod_resp = requests.get(product_url, headers=headers, timeout=10)
            prod_soup = BeautifulSoup(prod_resp.text, 'html.parser')
            sold_out = prod_soup.find(string=re.compile(r'sold out|currently unavailable', re.I))
            if sold_out:
                return "Out of stock"
            add_to_cart = prod_soup.select_one('button._2KpZ6l._2U9uOA._3v1-ww')
            if add_to_cart and 'add to cart' in add_to_cart.get_text(strip=True).lower():
                return "In stock"
            return "Unknown"
        except Exception:
            return "Unknown"
    def check_bigbasket(product_name):
        return "Unknown"
    sites = ["amazon", "flipkart", "bigbasket"] if site == "all" else [site]
    availability = {}
    for s in sites:
        if s == "amazon":
            availability[s] = check_amazon(product_name)
        elif s == "flipkart":
            availability[s] = check_flipkart(product_name)
        elif s == "bigbasket":
            availability[s] = check_bigbasket(product_name)
        else:
            availability[s] = "Unknown"
    return availability
