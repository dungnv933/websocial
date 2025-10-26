"""
Tier calculation utilities for SMM Panel
"""
from typing import Tuple


def calculate_tier(total_spent: float) -> Tuple[int, str, float]:
    """
    Calculate user tier based on total spent amount
    
    Args:
        total_spent: Total amount spent by user
        
    Returns:
        Tuple of (tier_level, tier_name, tier_discount)
    """
    if total_spent < 5000000:  # < 5M VND
        return (1, "Cấp 1", 0.0)
    elif total_spent < 20000000:  # 5M - 20M VND
        return (2, "Cấp 2", 3.0)
    elif total_spent < 50000000:  # 20M - 50M VND
        return (3, "Cấp 3", 5.0)
    else:  # >= 50M VND
        return (4, "VIP", 10.0)


def get_next_tier_info(current_tier: int, total_spent: float) -> dict:
    """
    Get information about next tier
    
    Args:
        current_tier: Current tier level
        total_spent: Total amount spent
        
    Returns:
        Dictionary with next tier information
    """
    tier_thresholds = {
        1: 5000000,   # Cấp 1 -> Cấp 2
        2: 20000000,  # Cấp 2 -> Cấp 3
        3: 50000000,  # Cấp 3 -> VIP
        4: None       # VIP is max tier
    }
    
    next_threshold = tier_thresholds.get(current_tier)
    if next_threshold is None:
        return {"next_tier_spent": None, "is_max_tier": True}
    
    remaining = next_threshold - total_spent
    return {
        "next_tier_spent": max(0, remaining),
        "is_max_tier": False
    }


def calculate_discounted_price(original_price: float, tier_discount: float) -> float:
    """
    Calculate discounted price based on tier
    
    Args:
        original_price: Original price
        tier_discount: Discount percentage
        
    Returns:
        Discounted price
    """
    discount_amount = original_price * (tier_discount / 100)
    return original_price - discount_amount

