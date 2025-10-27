import sqlite3
from datetime import datetime
import httpx
from typing import List, Dict
import json

DB_PATH = '/home/homemmo/websocial/backend/services.db'
LIKEVIET_API_BASE = "https://likeviet.vn/api/v2"
LIKEVIET_API_KEY = "c827f930b6fbe6dc726f5ed7429b31b7"

class ServiceManager:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()
    
    def init_db(self):
        """Initialize database with improved schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Services table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY,
                likeviet_id INTEGER UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                likeviet_rate REAL,
                min_quantity INTEGER,
                max_quantity INTEGER,
                likeviet_category TEXT,
                category TEXT NOT NULL,
                subcategory TEXT,
                markup_percent REAL DEFAULT 0,
                final_rate REAL,
                sort_order INTEGER DEFAULT 0,
                is_featured BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                icon TEXT,
                badge TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                icon TEXT,
                color TEXT,
                sort_order INTEGER DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print('[ServiceManager] Database initialized with improved schema')
    
    async def sync_services_from_likeviet(self) -> Dict:
        """Sync Likeviet services and organize by category"""
        try:
            print("[ServiceManager] Fetching services from Likeviet...")
            
            async with httpx.AsyncClient() as client:
                payload = {
                    "key": LIKEVIET_API_KEY,
                    "action": "services"
                }
                response = await client.post(
                    LIKEVIET_API_BASE,
                    data=payload,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
            
            if "error" in data:
                return {"error": f"Likeviet API error: {data.get('message', 'Unknown error')}"}
            
            services = data if isinstance(data, list) else data.get("services", [])
            print(f"[ServiceManager] Got {len(services)} services from Likeviet")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            inserted = 0
            updated = 0
            categories_map = {}  # To organize services
            
            for service in services:
                likeviet_id = service.get('id')
                name = service.get('name', '')
                likeviet_category = service.get('category', 'Other')
                
                # Extract platform and category
                platform = self._extract_platform(name)
                category = self._organize_category(name, likeviet_category)
                icon = self._get_icon(platform)
                
                likeviet_rate = float(service.get('rate', 0))
                final_rate = likeviet_rate
                
                # Check if exists
                cursor.execute('SELECT id FROM services WHERE likeviet_id = ?', (likeviet_id,))
                existing = cursor.fetchone()
                
                if existing:
                    cursor.execute('''
                        UPDATE services SET
                            name = ?, description = ?,
                            likeviet_category = ?, category = ?,
                            likeviet_rate = ?, final_rate = ?,
                            min_quantity = ?, max_quantity = ?,
                            icon = ?, updated_at = ?
                        WHERE likeviet_id = ?
                    ''', (
                        name, service.get('description', ''),
                        likeviet_category, category,
                        likeviet_rate, final_rate,
                        service.get('min', 0), service.get('max', 0),
                        icon, datetime.now(),
                        likeviet_id
                    ))
                    updated += 1
                else:
                    cursor.execute('''
                        INSERT INTO services 
                        (likeviet_id, name, description, likeviet_category, category,
                         likeviet_rate, final_rate, min_quantity, max_quantity, icon)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        likeviet_id, name, service.get('description', ''),
                        likeviet_category, category,
                        likeviet_rate, final_rate,
                        service.get('min', 0), service.get('max', 0),
                        icon
                    ))
                    inserted += 1
                    
                    # Track categories
                    if category not in categories_map:
                        categories_map[category] = {"icon": icon, "count": 0}
                    categories_map[category]["count"] += 1
            
            # Insert/update categories
            for cat_name, cat_info in categories_map.items():
                cursor.execute('''
                    INSERT OR IGNORE INTO service_categories (name, icon)
                    VALUES (?, ?)
                ''', (cat_name, cat_info["icon"]))
            
            # Auto-assign sort_order based on insertion order
            cursor.execute('''
                UPDATE services SET sort_order = id
                WHERE sort_order = 0
            ''')
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "total": len(services),
                "inserted": inserted,
                "updated": updated,
                "categories": len(categories_map),
                "message": f"Synced {len(services)} services into {len(categories_map)} categories"
            }
        
        except Exception as e:
            print(f"[ServiceManager] Error: {str(e)}")
            return {"error": str(e)}
    
    def _extract_platform(self, name: str) -> str:
        """Extract platform from service name"""
        text = name.lower()
        platforms = {
            "tiktok": "🎵 TikTok",
            "instagram": "📷 Instagram",
            "facebook": "👍 Facebook",
            "youtube": "▶️ YouTube",
            "twitter": "🐦 Twitter",
            "telegram": "✈️ Telegram",
            "snapchat": "👻 Snapchat",
            "linkedin": "💼 LinkedIn",
            "pinterest": "📌 Pinterest"
        }
        
        for key, value in platforms.items():
            if key in text:
                return value
        
        return "🔗 Other"
    
    def _organize_category(self, name: str, likeviet_category: str) -> str:
        """Organize service into meaningful category"""
        name_lower = name.lower()
        
        # TikTok categories
        if "tiktok" in name_lower:
            if "like" in name_lower:
                return "🎵 TikTok - Likes"
            elif "follow" in name_lower:
                return "🎵 TikTok - Followers"
            elif "view" in name_lower:
                return "🎵 TikTok - Views"
            elif "comment" in name_lower:
                return "🎵 TikTok - Comments"
            elif "share" in name_lower:
                return "🎵 TikTok - Shares"
            else:
                return "🎵 TikTok - Other"
        
        # Instagram categories
        elif "instagram" in name_lower:
            if "follow" in name_lower:
                return "📷 Instagram - Followers"
            elif "like" in name_lower:
                return "📷 Instagram - Likes"
            elif "comment" in name_lower:
                return "📷 Instagram - Comments"
            elif "view" in name_lower:
                return "📷 Instagram - Views"
            else:
                return "📷 Instagram - Other"
        
        # Facebook categories
        elif "facebook" in name_lower:
            if "like" in name_lower:
                return "👍 Facebook - Likes"
            elif "follow" in name_lower or "page" in name_lower:
                return "👍 Facebook - Followers"
            elif "share" in name_lower:
                return "👍 Facebook - Shares"
            elif "comment" in name_lower:
                return "👍 Facebook - Comments"
            else:
                return "👍 Facebook - Other"
        
        # YouTube categories
        elif "youtube" in name_lower:
            if "subscriber" in name_lower or "follow" in name_lower:
                return "▶️ YouTube - Subscribers"
            elif "view" in name_lower:
                return "▶️ YouTube - Views"
            elif "like" in name_lower:
                return "▶️ YouTube - Likes"
            elif "comment" in name_lower:
                return "▶️ YouTube - Comments"
            else:
                return "▶️ YouTube - Other"
        
        # Twitter
        elif "twitter" in name_lower or "x.com" in name_lower:
            return "🐦 Twitter - Engagement"
        
        # Default fallback
        return f"🔗 {likeviet_category or 'Other'}"
    
    def _get_icon(self, platform: str) -> str:
        """Get icon emoji for platform"""
        icons = {
            "🎵 TikTok": "🎵",
            "📷 Instagram": "📷",
            "👍 Facebook": "👍",
            "▶️ YouTube": "▶️",
            "🐦 Twitter": "🐦",
            "✈️ Telegram": "✈️",
            "👻 Snapchat": "👻",
            "💼 LinkedIn": "💼",
            "📌 Pinterest": "📌"
        }
        return icons.get(platform, "🔗")
    
    def get_all_services(self, enabled_only=True, category=None, platform=None):
        """Get all services organized by category"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM services WHERE 1=1"
        params = []
        
        if enabled_only:
            query += " AND is_active = 1"
        
        if category:
            # Use LIKE to handle emoji encoding
            query += " AND category LIKE ?"
            params.append("%" + category + "%")
            print("[ServiceManager] Filtering category: " + str(category))
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        query += " ORDER BY is_featured DESC, sort_order, category, name"
        
        print("[ServiceManager] Executing query with " + str(len(params)) + " params")
        cursor.execute(query, params)
        services = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        print("[ServiceManager] Found " + str(len(services)) + " services")
        return services
    
    def get_categories(self) -> List[Dict]:
        """Get all categories with service counts"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT category, icon 
            FROM services 
            WHERE is_active = 1
            ORDER BY category
        ''')
        
        results = []
        for row in cursor.fetchall():
            cat_dict = dict(row)
            # Count services in this category
            cursor.execute(
                'SELECT COUNT(*) as count FROM services WHERE category = ? AND is_active = 1',
                (cat_dict['category'],)
            )
            cat_dict['count'] = cursor.fetchone()['count']
            results.append(cat_dict)
        
        conn.close()
        return results
    
    def update_service_order(self, likeviet_id: int, sort_order: int, is_featured: bool = False) -> Dict:
        """Update service sort order and featured status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE services SET
                sort_order = ?, is_featured = ?, updated_at = ?
            WHERE likeviet_id = ?
        ''', (sort_order, is_featured, datetime.now(), likeviet_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    def toggle_service(self, likeviet_id: int, is_active: bool) -> Dict:
        """Enable/disable service"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE services SET is_active = ?, updated_at = ?
            WHERE likeviet_id = ?
        ''', (is_active, datetime.now(), likeviet_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "likeviet_id": likeviet_id, "is_active": is_active}
    
    def update_markup(self, likeviet_id: int, markup_percent: float) -> Dict:
        """Update service markup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT likeviet_rate FROM services WHERE likeviet_id = ?", (likeviet_id,))
        row = cursor.fetchone()
        
        if not row:
            return {"error": "Service not found"}
        
        likeviet_rate = row[0]
        final_rate = likeviet_rate * (1 + markup_percent / 100)
        
        cursor.execute('''
            UPDATE services SET
                markup_percent = ?, final_rate = ?, updated_at = ?
            WHERE likeviet_id = ?
        ''', (markup_percent, final_rate, datetime.now(), likeviet_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "likeviet_id": likeviet_id,
            "markup_percent": markup_percent,
            "final_rate": final_rate
        }
    
    def search_services(self, query: str) -> List[Dict]:
        """Search services"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        cursor.execute('''
            SELECT * FROM services
            WHERE is_active = 1 AND (
                name LIKE ? OR category LIKE ? OR description LIKE ?
            )
            ORDER BY is_featured DESC, sort_order, name
            LIMIT 50
        ''', (search_term, search_term, search_term))
        
        services = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return services

# Initialize manager
service_manager = ServiceManager()