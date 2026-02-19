"""
Currency utilities for converting fees based on country
"""

# Mapping of countries to their default currencies
COUNTRY_TO_CURRENCY = {
    "Pakistan": "PKR",
    "United States": "USD",
    "United Kingdom": "GBP",
    "Canada": "CAD",
    "Australia": "AUD",
    "Saudi Arabia": "SAR",
    "UAE": "AED",
    "Egypt": "EGP",
    "Malaysia": "MYR",
    "Indonesia": "IDR",
    "Bangladesh": "BDT",
    "India": "INR",
}

# Exchange rates (update daily in production with real API)
EXCHANGE_RATES = {
    "USD": 1.0,
    "PKR": 277.5,  # 1 USD = 277.5 PKR
    "GBP": 0.79,   # 1 USD = 0.79 GBP
    "CAD": 1.36,   # 1 USD = 1.36 CAD
    "AUD": 1.53,   # 1 USD = 1.53 AUD
    "SAR": 3.75,   # 1 USD = 3.75 SAR
    "AED": 3.67,   # 1 USD = 3.67 AED
    "EGP": 49.0,   # 1 USD = 49 EGP
    "MYR": 4.75,   # 1 USD = 4.75 MYR
    "IDR": 16500,  # 1 USD = 16500 IDR
    "BDT": 104,    # 1 USD = 104 BDT
    "INR": 83.0,   # 1 USD = 83 INR
}

# Currency symbols
CURRENCY_SYMBOLS = {
    "USD": "$",
    "PKR": "Rs.",
    "GBP": "£",
    "CAD": "C$",
    "AUD": "A$",
    "SAR": "﷼",
    "AED": "د.إ",
    "EGP": "£",
    "MYR": "RM",
    "IDR": "Rp",
    "BDT": "৳",
    "INR": "₹",
}

def get_currency_for_country(country: str) -> str:
    """
    Get the default currency for a country
    
    Args:
        country: Country name
        
    Returns:
        Currency code (e.g., "USD", "PKR")
    """
    return COUNTRY_TO_CURRENCY.get(country, "USD")

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert amount from one currency to another
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        
    Returns:
        Converted amount
    """
    if from_currency == to_currency:
        return amount
    
    from_rate = EXCHANGE_RATES.get(from_currency, 1.0)
    to_rate = EXCHANGE_RATES.get(to_currency, 1.0)
    
    # Convert to USD first, then to target currency
    amount_in_usd = amount / from_rate
    converted_amount = amount_in_usd * to_rate
    
    return round(converted_amount, 2)

def format_currency(amount: float, currency: str) -> str:
    """
    Format amount with currency symbol
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    return f"{symbol} {amount:,.2f}"

def get_payment_in_user_currency(amount: float, base_currency: str = "USD", 
                                  user_country: str = None, user_currency: str = None) -> dict:
    """
    Get payment amount in user's local currency
    
    Args:
        amount: Base amount
        base_currency: Base currency code (default USD)
        user_country: User's country (to determine currency)
        user_currency: User's explicit currency (takes precedence)
        
    Returns:
        Dictionary with amounts in both currencies
    """
    if user_currency is None and user_country:
        user_currency = get_currency_for_country(user_country)
    elif user_currency is None:
        user_currency = "USD"
    
    converted_amount = convert_currency(amount, base_currency, user_currency)
    
    return {
        "base_amount": amount,
        "base_currency": base_currency,
        "converted_amount": converted_amount,
        "converted_currency": user_currency,
        "formatted_base": format_currency(amount, base_currency),
        "formatted_converted": format_currency(converted_amount, user_currency),
    }
