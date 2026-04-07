from api.endpoints.match import match
from api.endpoints.offers import scan_and_save_offers
from api.endpoints.generate_cv import auto_generate_cv
from api.endpoints.supabase import (
    supabase_delete,
    supabase_insert,
    supabase_select,
    supabase_update,
)

__all__ = [
    'match',
    'supabase_select',
    'supabase_insert',
    'supabase_update',
    'supabase_delete',
    'scan_and_save_offers',
    'auto_generate_cv',
]
