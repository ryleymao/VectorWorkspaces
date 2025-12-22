from datetime import datetime, timedelta


def calculate_freshness_score(last_updated_at: datetime, freshness_weight: float) -> float:
    if last_updated_at is None:
        return 1.0
    
    days_since_update = (datetime.utcnow() - last_updated_at).days
    freshness_boost = 1.0 + (days_since_update / 365.0) * freshness_weight
    
    return max(0.1, freshness_boost)

