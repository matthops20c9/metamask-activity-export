from decimal import Decimal
from datetime import datetime

def hex_to_int(val):
    if not val:
        return 0
    if isinstance(val, int):
        return val
    
    val_str = str(val).strip()
    
    # Handle negative hex values which show up in some dev networks
    is_negative = False
    if val_str.startswith('-'):
        is_negative = True
        val_str = val_str[1:]
        
    if val_str.startswith('0x'):
        try:
            num = int(val_str[2:], 16)
            return -num if is_negative else num
        except ValueError:
            return 0
            
    try:
        num = int(val_str)
        return -num if is_negative else num
    except ValueError:
        return 0

def wei_to_ether(wei_val, decimals=18):
    # This is a bit of a misnomer since it supports any decimal power (e.g. 8 for WBTC),
    # but we're keeping the name from the early version to avoid breaking parser.py.
    if wei_val is None:
        return Decimal('0')
    
    val_int = hex_to_int(wei_val)
    # print(f"DEBUG utils: {wei_val} -> {val_int}")
    return Decimal(val_int) / Decimal(10 ** decimals)

def format_ts(ts):
    if not ts:
        return ''
    try:
        val = int(ts)
        # MetaMask sometimes switches between seconds and milliseconds depending on 
        # whether it's standard tx or an incoming tx from helper APIs.
        if val < 9999999999:
            val *= 1000
        dt = datetime.fromtimestamp(val / 1000.0)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return ''
