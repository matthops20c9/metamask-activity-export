import json
from datetime import datetime
from metamask_activity_export.utils import clean_hex, to_decimal_str

def _find_transactions_recursive(node, visited=None):
    """Recursively walk state log tree to find lists under 'transactions' keys."""
    if visited is None:
        visited = set()
        
    node_id = id(node)
    if node_id in visited:
        return None
    visited.add(node_id)
    
    if isinstance(node, dict):
        if "transactions" in node and isinstance(node["transactions"], list):
            txs = node["transactions"]
            if txs and isinstance(txs[0], dict) and ("txParams" in txs[0] or "status" in txs[0]):
                return txs
        
        for k, v in node.items():
            res = _find_transactions_recursive(v, visited)
            if res:
                return res
    elif isinstance(node, list):
        for item in node:
            res = _find_transactions_recursive(item, visited)
            if res:
                return res
    return None

def extract_transactions(state_data):
    """Extract all raw transaction records found in the MetaMask state export."""
    tx_list = None
    
    # Standard fast paths
    if "TransactionController" in state_data and "transactions" in state_data["TransactionController"]:
        tx_list = state_data["TransactionController"]["transactions"]
    elif "metamask" in state_data:
        mm = state_data["metamask"]
        if "TransactionController" in mm and "transactions" in mm["TransactionController"]:
            tx_list = mm["TransactionController"]["transactions"]
        elif "transactions" in mm:
            tx_list = mm["transactions"]
            
    # Deep fallback if paths changed (e.g., inside EngineController or newer state partitions)
    if not tx_list:
        tx_list = _find_transactions_recursive(state_data)
        
    if not tx_list:
        return []
        
    # print(f"Found {len(tx_list)} raw transactions in state export")
    
    normalized = []
    for tx in tx_list:
        try:
            # Some older states had extremely simplified transaction representations
            if "txParams" not in tx and "from" in tx and "to" in tx:
                item = extractLegacyTx(tx)
            else:
                item = normalize_transaction(tx)
            if item:
                normalized.append(item)
        except (ValueError, KeyError, TypeError):
            # Corrupted transaction entry, skip it and carry on
            continue
            
    return normalized

def extractLegacyTx(tx):
    # Leftover mapper for pre-v7 MM states where txParams didn't exist
    # TODO: verify if we still need this for exports from 2018-2019 logs
    tx_id = tx.get("id")
    if not tx_id:
        return None
        
    return {
        "id": str(tx_id),
        "time": "",
        "status": tx.get("status", "unknown"),
        "hash": tx.get("hash", ""),
        "from": tx.get("from", ""),
        "to": tx.get("to", ""),
        "value_wei": tx.get("value", "0"),
        "value_eth": to_decimal_str(tx.get("value", "0")),
        "gas_limit": tx.get("gas", "0"),
        "gas_price_wei": tx.get("gasPrice", "0"),
        "chain_id": int(tx.get("metamaskNetworkId", "1")),
        "data": tx.get("input", "")
    }

def normalize_transaction(tx):
    tx_id = tx.get("id")
    if not tx_id:
        return None
        
    status = tx.get("status", "unknown")
    tx_hash = tx.get("hash", "")
    
    raw_time = tx.get("time")
    if isinstance(raw_time, str):
        try:
            raw_time = int(raw_time)
        except ValueError:
            raw_time = None
    
    if raw_time:
        dt = datetime.utcfromtimestamp(raw_time / 1000.0)
        formatted_time = dt.isoformat() + "Z"
    else:
        formatted_time = ""
        
    tx_params = tx.get("txParams", {})
    if not tx_params:
        # Fallback if the top level has some details but txParams is empty
        if tx.get("to") or tx.get("from"):
            return extractLegacyTx(tx)
        return None
        
    from_addr = tx_params.get("from", "")
    to_addr = tx_params.get("to", "")
    
    chain_id_raw = tx.get("chainId") or tx_params.get("chainId") or tx.get("metamaskNetworkId")
    chain_id = 1
    if chain_id_raw:
        if isinstance(chain_id_raw, str):
            if chain_id_raw.startswith("0x"):
                chain_id = int(chain_id_raw, 16)
            else:
                # Strip any non-digit trailing characters if state is weird
                numeric_part = "".join(c for c in chain_id_raw if c.isdigit())
                chain_id = int(numeric_part) if numeric_part else 1
        else:
            try:
                chain_id = int(chain_id_raw)
            except (ValueError, TypeError):
                chain_id = 1
            
    raw_val = tx_params.get("value", "0x0")
    val_wei = clean_hex(raw_val)
    val_eth = to_decimal_str(val_wei)
    
    gas_limit = clean_hex(tx_params.get("gas", "0x0"))
    gas_price = clean_hex(tx_params.get("gasPrice", "0x0"))
    
    return {
        "id": str(tx_id),
        "time": formatted_time,
        "status": status,
        "hash": tx_hash,
        "from": from_addr,
        "to": to_addr,
        "value_wei": val_wei,
        "value_eth": val_eth,
        "gas_limit": gas_limit,
        "gas_price_wei": gas_price,
        "chain_id": chain_id,
        "data": tx_params.get("data", "")
    }
