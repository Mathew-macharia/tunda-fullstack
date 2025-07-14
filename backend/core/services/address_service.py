from django.conf import settings
from django.core.cache import cache, caches
from decimal import Decimal
import hashlib
import logging
import time
from typing import Optional, Tuple, Dict, Any
import re

# Try to import googlemaps, but handle gracefully if not available
try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    googlemaps = None

logger = logging.getLogger(__name__)

class AddressService:
    """Production-ready service for handling address resolution and distance calculations"""
    
    # Rate limiting settings
    MAX_REQUESTS_PER_MINUTE = 50
    MAX_REQUESTS_PER_HOUR = 1000
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.gmaps = None
        try:
            self.geocoding_cache = caches['geocoding']
        except:
            self.geocoding_cache = cache
        
        try:
            self.distance_cache = caches['distance']  
        except:
            self.distance_cache = cache
            
        self._request_timestamps = []
        
        if GOOGLEMAPS_AVAILABLE and hasattr(settings, 'GOOGLE_MAPS_API_KEY') and settings.GOOGLE_MAPS_API_KEY:
            try:
                self.gmaps = googlemaps.Client(
                    key=settings.GOOGLE_MAPS_API_KEY,
                    timeout=10,  # 10 second timeout
                    retry_timeout=60  # Retry for up to 60 seconds
                    # Note: requests_per_second is handled by our custom rate limiting
                )
                self.logger.info("Google Maps client initialized successfully")
                self._test_api_connectivity()
            except Exception as e:
                self.logger.error(f"Failed to initialize Google Maps client: {str(e)}")
                self.gmaps = None
        else:
            if not GOOGLEMAPS_AVAILABLE:
                self.logger.warning("Google Maps package not available")
            else:
                self.logger.warning("Google Maps API key not configured")
    
    def _test_api_connectivity(self):
        """Test API connectivity on initialization"""
        try:
            # Simple geocoding test
            test_result = self.gmaps.geocode("Nairobi, Kenya")
            if test_result:
                self.logger.info("Google Maps API connectivity test successful")
            else:
                self.logger.warning("Google Maps API test returned no results")
        except Exception as e:
            self.logger.error(f"Google Maps API connectivity test failed: {str(e)}")
            self.gmaps = None
    
    def _check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        
        # Clean old timestamps (older than 1 hour)
        self._request_timestamps = [
            ts for ts in self._request_timestamps 
            if current_time - ts < 3600
        ]
        
        # Check hourly limit
        if len(self._request_timestamps) >= self.MAX_REQUESTS_PER_HOUR:
            self.logger.warning("Hourly rate limit reached for Google Maps API")
            return False
        
        # Check per-minute limit
        recent_requests = [
            ts for ts in self._request_timestamps 
            if current_time - ts < 60
        ]
        
        if len(recent_requests) >= self.MAX_REQUESTS_PER_MINUTE:
            self.logger.warning("Per-minute rate limit reached for Google Maps API")
            return False
        
        return True
    
    def _record_api_request(self):
        """Record an API request for rate limiting"""
        self._request_timestamps.append(time.time())
    
    def get_farm_coordinates(self, farm) -> Tuple[float, float]:
        """Get farm coordinates using existing sub-county data"""
        # Build address from existing farm data
        address = f"{farm.sub_county.sub_county_name}, {farm.sub_county.county.county_name}, Kenya"
        return self._geocode_address_string(address)
    
    def get_customer_coordinates(self, delivery_address) -> Tuple[float, float]:
        """Get customer coordinates from delivery address dictionary or object"""
        
        # Handle dictionary input (from API requests)
        if isinstance(delivery_address, dict):
            # Check if we have direct coordinates
            if 'latitude' in delivery_address and 'longitude' in delivery_address:
                if delivery_address['latitude'] and delivery_address['longitude']:
                    return (float(delivery_address['latitude']), float(delivery_address['longitude']))
            
            # Build address from dictionary components
            address_parts = []
            if delivery_address.get('detailed_address'):
                address_parts.append(delivery_address['detailed_address'])
            
            # Handle sub_county - could be ID or name
            sub_county = delivery_address.get('sub_county')
            if sub_county:
                # If it's a number, it's likely an ID, so we need to get the name
                try:
                    if isinstance(sub_county, (int, str)) and str(sub_county).isdigit():
                        from locations.models import SubCounty
                        subcounty_obj = SubCounty.objects.get(sub_county_id=int(sub_county))
                        address_parts.append(subcounty_obj.sub_county_name)
                        address_parts.append(subcounty_obj.county.county_name)
                    else:
                        # It's already a name
                        address_parts.append(sub_county)
                        if delivery_address.get('county'):
                            address_parts.append(delivery_address['county'])
                except:
                    # Fallback to using the value as-is
                    address_parts.append(str(sub_county))
                    if delivery_address.get('county'):
                        address_parts.append(delivery_address['county'])
            
            address_parts.append("Kenya")
            
            full_address = ", ".join(filter(None, address_parts))
            return self._geocode_address_string(full_address)
        
        # Handle UserAddress or Location objects
        if hasattr(delivery_address, 'latitude') and hasattr(delivery_address, 'longitude'):
            # UserAddress object
            if delivery_address.latitude and delivery_address.longitude:
                return (float(delivery_address.latitude), float(delivery_address.longitude))
            
            # Build full address for geocoding
            address_parts = []
            if hasattr(delivery_address, 'detailed_address') and delivery_address.detailed_address:
                address_parts.append(delivery_address.detailed_address)
            if hasattr(delivery_address, 'location_name') and delivery_address.location_name:
                address_parts.append(delivery_address.location_name)
            if hasattr(delivery_address, 'sub_county'):
                address_parts.append(f"{delivery_address.sub_county.sub_county_name}, {delivery_address.sub_county.county.county_name}")
            address_parts.append("Kenya")
            
        else:
            # Legacy Location object
            if hasattr(delivery_address, 'latitude') and hasattr(delivery_address, 'longitude'):
                if delivery_address.latitude and delivery_address.longitude:
                    return (float(delivery_address.latitude), float(delivery_address.longitude))
            
            # Build address from location data
            address_parts = []
            if hasattr(delivery_address, 'location_name') and delivery_address.location_name:
                address_parts.append(delivery_address.location_name)
            if hasattr(delivery_address, 'sub_location') and delivery_address.sub_location:
                address_parts.append(delivery_address.sub_location)
            if hasattr(delivery_address, 'landmark') and delivery_address.landmark:
                address_parts.append(delivery_address.landmark)
            address_parts.append("Kenya")
        
        full_address = ", ".join(filter(None, address_parts))
        return self._geocode_address_string(full_address)
    
    def get_customer_coordinates_with_details(self, delivery_address):
        """
        Get customer coordinates with detailed information about which address was used
        """
        # Handle dictionary input (from API requests)
        if isinstance(delivery_address, dict):
            # Check if we have direct coordinates
            if 'latitude' in delivery_address and 'longitude' in delivery_address:
                if delivery_address['latitude'] and delivery_address['longitude']:
                    return {
                        'coordinates': (float(delivery_address['latitude']), float(delivery_address['longitude'])),
                        'address_used': 'Direct coordinates provided',
                        'confidence': 1.0,
                        'method': 'direct_coordinates'
                    }
            
            # Use the enhanced geocoding with detailed results
            address_components = {
                'detailed_address': delivery_address.get('detailed_address', ''),
                'sub_county': delivery_address.get('sub_county', ''),
                'county': delivery_address.get('county', '')
            }
            
            geocoding_result = self.geocode_address(address_components)
            
            if isinstance(geocoding_result, dict) and 'coordinates' in geocoding_result:
                return {
                    'coordinates': geocoding_result['coordinates'],
                    'address_used': geocoding_result.get('address_used', 'Unknown'),
                    'confidence': geocoding_result.get('confidence', 0.0),
                    'method': 'geocoding',
                    'strategy_used': geocoding_result.get('strategy_used', 'Unknown')
                }
            else:
                # Fallback coordinates
                return {
                    'coordinates': geocoding_result,
                    'address_used': f"Fallback coordinates for {address_components.get('county', 'Kenya')}",
                    'confidence': 0.3,
                    'method': 'fallback'
                }
        
        # For non-dictionary objects, fall back to regular method
        return {
            'coordinates': self.get_customer_coordinates(delivery_address),
            'address_used': 'Object-based address',
            'confidence': 0.5,
            'method': 'object_based'
        }
    
    def geocode_address(self, address_components):
        """
        Enhanced geocoding with smart address prioritization
        
        Priority Order:
        1. Detailed address (if provided and meaningful)
        2. Sub-county + County combination
        3. County only (fallback)
        """
        detailed_address = address_components.get('detailed_address', '').strip()
        sub_county = address_components.get('sub_county', '').strip()
        county = address_components.get('county', '').strip()
        
        # Smart prioritization logic
        geocoding_strategies = self._build_geocoding_strategies(
            detailed_address, sub_county, county
        )
        
        for strategy in geocoding_strategies:
            try:
                self.logger.info(f"Trying geocoding strategy: {strategy['description']}")
                coordinates = self._attempt_geocoding(strategy['address'])
                
                if coordinates and self._validate_coordinates_in_kenya(coordinates):
                    self.logger.info(f"✅ Successful geocoding with strategy: {strategy['description']}")
                    return {
                        'coordinates': coordinates,
                        'strategy_used': strategy['description'],
                        'address_used': strategy['address'],
                        'confidence': strategy['confidence']
                    }
                    
            except Exception as e:
                self.logger.warning(f"Strategy '{strategy['description']}' failed: {str(e)}")
                continue
        
        # Final fallback to Kenya city coordinates
        return self._get_kenya_fallback_coordinates(county, sub_county)
    
    def _geocode_address_string(self, address_string):
        """
        Geocode a simple address string and return coordinates
        """
        try:
            coordinates = self._attempt_geocoding(address_string)
            if coordinates and self._validate_coordinates_in_kenya(coordinates):
                return coordinates
        except Exception as e:
            self.logger.warning(f"Failed to geocode address string '{address_string}': {str(e)}")
        
        # Return default Nairobi coordinates as fallback
        return (-1.2920659, 36.8219462)
    
    def _get_kenya_fallback_coordinates(self, county, sub_county):
        """
        Get fallback coordinates for Kenya locations
        """
        # Kenya city coordinates fallback
        kenya_fallback_coords = {
            'nairobi': (-1.2920659, 36.8219462),
            'mombasa': (-4.0434771, 39.6682065),
            'kisumu': (-0.1021554, 34.7617135),
            'nakuru': (-0.3030988, 36.0800217),
            'eldoret': (0.5143, 35.2697),
            'thika': (-1.0332, 37.0694),
            'malindi': (-3.2175, 40.1169),
            'kitale': (1.0177, 35.0062),
            'garissa': (-0.4569, 39.6582),
            'kakamega': (0.2827, 34.7519),
        }
        
        # Try to match county name to known coordinates
        if county:
            county_lower = county.lower()
            for city, coords in kenya_fallback_coords.items():
                if city in county_lower or county_lower in city:
                    self.logger.info(f"Using fallback coordinates for {county}: {coords}")
                    return coords
        
        # Default to Nairobi
        self.logger.info("Using default Nairobi coordinates as final fallback")
        return kenya_fallback_coords['nairobi']

    def _build_geocoding_strategies(self, detailed_address, sub_county, county):
        """
        Build prioritized list of geocoding strategies based on address quality
        """
        strategies = []
        
        # Strategy 1: Detailed address is meaningful and specific
        if self._is_meaningful_address(detailed_address):
            # Try detailed address with county context
            strategies.append({
                'address': f"{detailed_address}, {county}, Kenya",
                'description': f"Detailed address with county context",
                'confidence': 0.9
            })
            
            # Try detailed address with sub-county context
            if sub_county:
                strategies.append({
                    'address': f"{detailed_address}, {sub_county}, {county}, Kenya",
                    'description': f"Detailed address with sub-county context",
                    'confidence': 0.85
                })
            
            # Try detailed address alone
            strategies.append({
                'address': f"{detailed_address}, Kenya",
                'description': f"Detailed address only",
                'confidence': 0.8
            })
        
        # Strategy 2: Sub-county + County combination
        if sub_county and county:
            strategies.append({
                'address': f"{sub_county}, {county}, Kenya",
                'description': f"Sub-county with county",
                'confidence': 0.7
            })
        
        # Strategy 3: County center as fallback
        if county:
            strategies.append({
                'address': f"{county}, Kenya",
                'description': f"County center",
                'confidence': 0.6
            })
        
        return strategies

    def _is_meaningful_address(self, address):
        """
        Determine if a detailed address is meaningful enough to prioritize
        """
        if not address or len(address.strip()) < 3:
            return False
        
        # Check for meaningful address indicators
        meaningful_indicators = [
            'road', 'street', 'avenue', 'drive', 'lane', 'close', 'crescent',
            'mall', 'shopping', 'center', 'centre', 'building', 'tower',
            'hotel', 'hospital', 'school', 'university', 'church', 'mosque',
            'market', 'stage', 'junction', 'roundabout', 'estate', 'plaza',
            'gardens', 'park', 'stadium', 'airport', 'station'
        ]
        
        address_lower = address.lower()
        
        # Check for meaningful keywords
        has_meaningful_words = any(indicator in address_lower for indicator in meaningful_indicators)
        
        # Check for specific patterns (numbers + words typically indicate addresses)
        has_address_pattern = bool(re.search(r'\d+.*[a-zA-Z]|[a-zA-Z].*\d+', address))
        
        # Avoid generic terms that aren't helpful
        generic_terms = ['town', 'city', 'area', 'location', 'place']
        is_too_generic = any(term in address_lower and len(address.split()) <= 2 for term in generic_terms)
        
        return (has_meaningful_words or has_address_pattern) and not is_too_generic

    def _validate_coordinates_in_kenya(self, coordinates):
        """
        Validate that coordinates are within Kenya's boundaries
        """
        lat, lng = coordinates
        
        # Kenya's approximate boundaries
        # Latitude: -4.7 to 5.5
        # Longitude: 33.9 to 42.0
        return (
            -4.7 <= lat <= 5.5 and
            33.9 <= lng <= 42.0
        )

    def _attempt_geocoding(self, address):
        """
        Attempt to geocode a specific address string
        """
        try:
            # Check cache first
            cache_key = f"geocode:{hashlib.md5(address.encode()).hexdigest()}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                self.logger.info(f"Cache hit for address: {address[:50]}...")
                return cached_result
            
            # Rate limiting
            if not self._check_rate_limits():
                raise Exception("Rate limit exceeded")
            
            # Make API call
            geocode_result = self.gmaps.geocode(address)
            
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                coordinates = (location['lat'], location['lng'])
                
                # Cache the result
                cache.set(cache_key, coordinates, timeout=86400)  # 24 hours
                
                return coordinates
                
        except Exception as e:
            self.logger.error(f"Geocoding failed for '{address}': {str(e)}")
            raise

        return None

    def calculate_distance(self, origin_coords: Tuple[float, float], destination_coords: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates with production-ready error handling"""
        
        # Create cache key for distance calculation
        cache_key = f"distance_{hashlib.md5(f'{origin_coords}_{destination_coords}'.encode()).hexdigest()}"
        
        # Check cache first
        cached_result = self.distance_cache.get(cache_key)
        if cached_result:
            self.logger.debug(f"Using cached distance: {cached_result} km")
            return cached_result
        
        # If no Google Maps API or rate limited, use straight-line distance
        if not self.gmaps or not self._check_rate_limits():
            self.logger.warning("Using straight-line distance calculation")
            distance = self.calculate_straight_line_distance(origin_coords, destination_coords)
            self.distance_cache.set(cache_key, distance, 3600)  # Cache for 1 hour
            return distance
        
        try:
            self.logger.info(f"Calculating distance from {origin_coords} to {destination_coords}")
            self._record_api_request()
            
            # Use Google Distance Matrix API
            distance_result = self.gmaps.distance_matrix(
                origins=[origin_coords],
                destinations=[destination_coords],
                mode="driving",
                units="metric",
                avoid="tolls"  # Avoid tolls for cost-effective routing
            )
            
            if distance_result['status'] == 'OK':
                element = distance_result['rows'][0]['elements'][0]
                if element['status'] == 'OK':
                    # Return distance in kilometers
                    distance_meters = element['distance']['value']
                    distance_km = distance_meters / 1000.0
                    
                    self.logger.info(f"Calculated driving distance: {distance_km} km")
                    
                    # Cache for 1 hour
                    self.distance_cache.set(cache_key, distance_km, 3600)
                    return distance_km
                else:
                    self.logger.warning(f"Distance calculation failed: {element['status']}")
            else:
                self.logger.warning(f"Distance Matrix API failed: {distance_result['status']}")
                
        except googlemaps.exceptions.ApiError as e:
            self.logger.error(f"Google Maps API error during distance calculation: {e}")
        except googlemaps.exceptions.Timeout as e:
            self.logger.error(f"Google Maps API timeout during distance calculation: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected distance calculation error: {e}")
        
        # Fallback to straight-line distance
        self.logger.info("Using straight-line distance as fallback")
        distance = self.calculate_straight_line_distance(origin_coords, destination_coords)
        self.distance_cache.set(cache_key, distance, 3600)
        return distance
    
    def calculate_straight_line_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate straight-line distance as fallback using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        distance_km = c * r
        
        self.logger.info(f"Calculated straight-line distance: {distance_km:.2f} km")
        return distance_km
    
    def get_api_usage_stats(self) -> Dict[str, Any]:
        """Get current API usage statistics for monitoring"""
        current_time = time.time()
        
        # Clean old timestamps
        self._request_timestamps = [
            ts for ts in self._request_timestamps 
            if current_time - ts < 3600
        ]
        
        recent_requests = [
            ts for ts in self._request_timestamps 
            if current_time - ts < 60
        ]
        
        return {
            'api_available': self.gmaps is not None,
            'requests_last_hour': len(self._request_timestamps),
            'requests_last_minute': len(recent_requests),
            'hourly_limit': self.MAX_REQUESTS_PER_HOUR,
            'minute_limit': self.MAX_REQUESTS_PER_MINUTE,
            'within_limits': len(self._request_timestamps) < self.MAX_REQUESTS_PER_HOUR and len(recent_requests) < self.MAX_REQUESTS_PER_MINUTE
        } 