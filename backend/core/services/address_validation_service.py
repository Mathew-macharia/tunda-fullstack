import re
import logging
from typing import Dict, List, Optional, Tuple
from django.core.cache import cache
from django.conf import settings
from locations.models import County, SubCounty
from .address_service import AddressService

logger = logging.getLogger(__name__)

class AddressValidationService:
    """
    Service for validating addresses and detecting mismatches between
    detailed addresses and selected administrative boundaries
    """
    
    def __init__(self):
        self.address_service = AddressService()
        self.load_popular_places()
    
    def load_popular_places(self):
        """Load popular places and landmarks for validation from database"""
        # Load from database instead of hardcoding
        self.popular_places = {}
        self._load_from_database()
        
        # Load additional places from cache or external APIs
        self._load_external_places()
    
    def _load_from_database(self):
        """Load popular places from database"""
        try:
            from core.models import PopularPlace
            
            # Get all popular places from database
            places = PopularPlace.objects.select_related('sub_county').filter(
                is_verified=True
            ).order_by('-popularity_score')
            
            for place in places:
                # Add main name
                place_name = place.place_name.lower()
                subcounty_name = place.sub_county.sub_county_name.lower()
                
                self.popular_places[place_name] = subcounty_name
                
                # Add alternative names
                for alt_name in place.alternative_names:
                    if alt_name and alt_name.strip():
                        self.popular_places[alt_name.lower().strip()] = subcounty_name
            
            logger.info(f"Loaded {len(self.popular_places)} popular places from database")
            
        except Exception as e:
            logger.warning(f"Failed to load places from database: {str(e)}")
            # Fallback to minimal hardcoded data for critical places
            self._load_fallback_places()
    
    def _load_fallback_places(self):
        """Load minimal fallback places if database is empty"""
        self.popular_places = {
            # Only the most critical places as fallback
            'westgate': 'westlands',
            'sarit centre': 'westlands',
            'village market': 'westlands',
            'jkia': 'embakasi south',
            'wilson airport': 'langata',
            'nairobi national park': 'langata',
            'uhuru park': 'starehe',
            'kenyatta national hospital': 'starehe',
        }
    
    def _load_external_places(self):
        """Load additional popular places from external sources"""
        try:
            # Try to load from cache first
            cached_places = cache.get('popular_places_kenya')
            if cached_places:
                self.popular_places.update(cached_places)
                return
            
            # In production, this could trigger background tasks to:
            # - Update places from Google Places API
            # - Sync with OpenStreetMap data
            # - Load from Kenya tourism board data
            
        except Exception as e:
            logger.warning(f"Failed to load external places: {str(e)}")
    
    def validate_address(self, address_data: Dict) -> Dict:
        """
        Validate address and detect potential mismatches
        
        Args:
            address_data: Dictionary containing:
                - detailed_address: User-entered address
                - sub_county: Selected sub-county ID or name
                - county: Selected county ID or name
        
        Returns:
            Dictionary with validation results and warnings
        """
        detailed_address = address_data.get('detailed_address', '').strip()
        sub_county = address_data.get('sub_county', '')
        county = address_data.get('county', '')
        
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'suggestions': [],
            'confidence': 1.0,
            'detected_location': None,
            'mismatch_detected': False
        }
        
        if not detailed_address:
            return validation_result
        
        # Step 1: Detect location from detailed address
        detected_location = self._detect_location_from_address(detailed_address)
        
        if detected_location:
            validation_result['detected_location'] = detected_location
            
            # Step 2: Compare with selected sub-county
            mismatch_info = self._check_for_mismatch(
                detected_location, sub_county, county
            )
            
            if mismatch_info['has_mismatch']:
                validation_result['mismatch_detected'] = True
                validation_result['warnings'].append(mismatch_info['warning'])
                validation_result['suggestions'].extend(mismatch_info['suggestions'])
                validation_result['confidence'] = 0.6  # Lower confidence due to mismatch
        
        # Step 3: Additional validations
        self._add_additional_validations(detailed_address, validation_result)
        
        return validation_result
    
    def _detect_location_from_address(self, address: str) -> Optional[Dict]:
        """
        Detect likely location/sub-county from address text
        """
        address_lower = address.lower()
        
        # Check against popular places
        for place, expected_subcounty in self.popular_places.items():
            if place in address_lower:
                return {
                    'detected_place': place,
                    'expected_subcounty': expected_subcounty,
                    'confidence': 0.8,
                    'method': 'popular_places'
                }
        
        # Check for direct sub-county mentions
        subcounty_matches = self._find_subcounty_mentions(address_lower)
        if subcounty_matches:
            return {
                'detected_place': subcounty_matches[0]['name'],
                'expected_subcounty': subcounty_matches[0]['name'],
                'confidence': 0.9,
                'method': 'direct_mention'
            }
        
        # Use reverse geocoding if available
        reverse_geocoded = self._reverse_geocode_address(address)
        if reverse_geocoded:
            return reverse_geocoded
        
        return None
    
    def _find_subcounty_mentions(self, address: str) -> List[Dict]:
        """Find direct mentions of sub-counties in the address"""
        matches = []
        
        try:
            # Get all sub-counties from database
            subcounties = SubCounty.objects.select_related('county').all()
            
            for subcounty in subcounties:
                subcounty_name = subcounty.sub_county_name.lower()
                
                # Check for exact match
                if subcounty_name in address:
                    matches.append({
                        'name': subcounty.sub_county_name,
                        'county': subcounty.county.county_name,
                        'confidence': 0.9
                    })
                
                # Check for partial match (for compound names)
                words = subcounty_name.split()
                if len(words) > 1:
                    for word in words:
                        if len(word) > 3 and word in address:
                            matches.append({
                                'name': subcounty.sub_county_name,
                                'county': subcounty.county.county_name,
                                'confidence': 0.7
                            })
        
        except Exception as e:
            logger.warning(f"Error finding subcounty mentions: {str(e)}")
        
        # Sort by confidence and remove duplicates
        unique_matches = {}
        for match in matches:
            name = match['name']
            if name not in unique_matches or match['confidence'] > unique_matches[name]['confidence']:
                unique_matches[name] = match
        
        return sorted(unique_matches.values(), key=lambda x: x['confidence'], reverse=True)
    
    def _reverse_geocode_address(self, address: str) -> Optional[Dict]:
        """Use reverse geocoding to detect location"""
        try:
            # First geocode to get coordinates
            coordinates = self.address_service._geocode_address_string(address)
            
            if coordinates and self.address_service.gmaps:
                # Then reverse geocode to get administrative components
                reverse_result = self.address_service.gmaps.reverse_geocode(coordinates)
                
                if reverse_result:
                    # Extract administrative components
                    components = reverse_result[0].get('address_components', [])
                    
                    for component in components:
                        types = component.get('types', [])
                        if 'administrative_area_level_2' in types:
                            # This is typically the sub-county level
                            return {
                                'detected_place': address,
                                'expected_subcounty': component['long_name'],
                                'confidence': 0.7,
                                'method': 'reverse_geocoding'
                            }
        
        except Exception as e:
            logger.warning(f"Reverse geocoding failed: {str(e)}")
        
        return None
    
    def _check_for_mismatch(self, detected_location: Dict, selected_subcounty, selected_county) -> Dict:
        """Check if detected location matches selected sub-county"""
        
        expected_subcounty = detected_location.get('expected_subcounty', '').lower()
        detected_place = detected_location.get('detected_place', '')
        
        # Get selected sub-county name
        selected_subcounty_name = self._get_subcounty_name(selected_subcounty)
        
        if not selected_subcounty_name:
            return {'has_mismatch': False}
        
        selected_subcounty_lower = selected_subcounty_name.lower()
        
        # Check for mismatch
        if expected_subcounty and expected_subcounty != selected_subcounty_lower:
            # Check if they're similar (to avoid false positives)
            similarity = self._calculate_similarity(expected_subcounty, selected_subcounty_lower)
            
            if similarity < 0.7:  # Significant difference
                return {
                    'has_mismatch': True,
                    'warning': f"⚠️ Address mismatch detected: '{detected_place}' is typically located in {expected_subcounty.title()}, but you selected {selected_subcounty_name}.",
                    'suggestions': [
                        f"Consider selecting '{expected_subcounty.title()}' instead",
                        "Double-check your address details",
                        "Verify the sub-county selection"
                    ]
                }
        
        return {'has_mismatch': False}
    
    def _get_subcounty_name(self, subcounty_identifier) -> Optional[str]:
        """Get sub-county name from ID or name"""
        if not subcounty_identifier:
            return None
        
        try:
            # If it's a number, treat as ID
            if isinstance(subcounty_identifier, (int, str)) and str(subcounty_identifier).isdigit():
                subcounty = SubCounty.objects.get(sub_county_id=int(subcounty_identifier))
                return subcounty.sub_county_name
            else:
                # Assume it's already a name
                return str(subcounty_identifier)
        
        except SubCounty.DoesNotExist:
            return None
        except Exception as e:
            logger.warning(f"Error getting subcounty name: {str(e)}")
            return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple similarity calculation based on common characters
        if not str1 or not str2:
            return 0.0
        
        # Normalize strings
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        if str1 == str2:
            return 1.0
        
        # Calculate Jaccard similarity on words
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _add_additional_validations(self, address: str, validation_result: Dict):
        """Add additional validation checks"""
        
        # Check for common address patterns
        if re.search(r'\b\d+\s*(st|nd|rd|th)\s+floor\b', address.lower()):
            validation_result['suggestions'].append(
                "💡 Tip: Include building name for more accurate delivery"
            )
        
        # Check for missing postal code
        if not re.search(r'\b\d{5}\b', address):
            validation_result['suggestions'].append(
                "💡 Consider adding a postal code for better accuracy"
            )
        
        # Check for very short addresses
        if len(address.strip()) < 10:
            validation_result['warnings'].append(
                "⚠️ Address seems very short - consider adding more details"
            )
            validation_result['confidence'] *= 0.8
    
    def get_autocomplete_suggestions(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Get autocomplete suggestions for addresses
        """
        suggestions = []
        query_lower = query.lower()
        
        # Search popular places
        for place, subcounty in self.popular_places.items():
            if query_lower in place or place.startswith(query_lower):
                suggestions.append({
                    'text': place.title(),
                    'description': f"{place.title()}, {subcounty.title()}",
                    'subcounty': subcounty,
                    'type': 'popular_place'
                })
        
        # Search sub-counties
        try:
            subcounties = SubCounty.objects.filter(
                sub_county_name__icontains=query
            ).select_related('county')[:limit]
            
            for subcounty in subcounties:
                suggestions.append({
                    'text': subcounty.sub_county_name,
                    'description': f"{subcounty.sub_county_name}, {subcounty.county.county_name}",
                    'subcounty': subcounty.sub_county_name,
                    'county': subcounty.county.county_name,
                    'type': 'subcounty'
                })
        
        except Exception as e:
            logger.warning(f"Error getting subcounty suggestions: {str(e)}")
        
        # Remove duplicates and limit results
        unique_suggestions = []
        seen_texts = set()
        
        for suggestion in suggestions:
            if suggestion['text'] not in seen_texts:
                unique_suggestions.append(suggestion)
                seen_texts.add(suggestion['text'])
            
            if len(unique_suggestions) >= limit:
                break
        
        return unique_suggestions 