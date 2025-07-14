import json
import requests
import hashlib
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from locations.models import SubCounty, County
from core.models import PopularPlace
from core.services.address_service import AddressService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load popular places data from external APIs (Google Places, Foursquare, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api',
            type=str,
            choices=['google_places', 'foursquare', 'overpass', 'all'],
            default='google_places',
            help='API source to use'
        )
        parser.add_argument(
            '--city',
            type=str,
            default='nairobi',
            help='City to load places for'
        )
        parser.add_argument(
            '--radius',
            type=int,
            default=50000,
            help='Search radius in meters'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=200,
            help='Maximum number of places to load per type'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing places instead of skipping them'
        )

    def handle(self, *args, **options):
        api = options['api']
        city = options['city']
        radius = options['radius']
        limit = options['limit']
        update_existing = options['update_existing']
        
        self.stdout.write(
            self.style.SUCCESS(f'Loading popular places for {city} from {api}...')
        )
        
        try:
            if api == 'google_places':
                self.load_from_google_places(city, radius, limit, update_existing)
            elif api == 'foursquare':
                self.load_from_foursquare(city, radius, limit, update_existing)
            elif api == 'overpass':
                self.load_from_overpass(city, radius, limit, update_existing)
            elif api == 'all':
                self.load_from_google_places(city, radius, limit, update_existing)
                self.load_from_foursquare(city, radius, limit, update_existing)
                self.load_from_overpass(city, radius, limit, update_existing)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading places: {str(e)}')
            )
            logger.error(f'Error loading popular places: {str(e)}')

    def load_from_google_places(self, city, radius, limit, update_existing):
        """Load places from Google Places API"""
        
        # Check if Google Maps API key is available
        if not hasattr(settings, 'GOOGLE_MAPS_API_KEY') or not settings.GOOGLE_MAPS_API_KEY:
            self.stdout.write(
                self.style.WARNING('Google Maps API key not configured. Skipping Google Places.')
            )
            return
        
        # Get city center coordinates
        city_coords = self.get_city_coordinates(city)
        if not city_coords:
            self.stdout.write(
                self.style.ERROR(f'Could not get coordinates for {city}')
            )
            return
        
        # Place types to search for
        place_types = [
            ('shopping_mall', 'shopping'),
            ('restaurant', 'restaurant'),
            ('lodging', 'hotel'),
            ('tourist_attraction', 'attraction'),
            ('park', 'park'),
            ('hospital', 'hospital'),
            ('school', 'education'),
            ('university', 'education'),
            ('airport', 'transport'),
            ('bus_station', 'transport'),
            ('train_station', 'transport'),
            ('government', 'government'),
            ('church', 'religious'),
            ('mosque', 'religious'),
        ]
        
        api_key = settings.GOOGLE_MAPS_API_KEY
        places_created = 0
        places_updated = 0
        
        for google_type, our_type in place_types:
            self.stdout.write(f'  Searching for {google_type} places...')
            
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
            params = {
                'location': f"{city_coords['lat']},{city_coords['lng']}",
                'radius': radius,
                'type': google_type,
                'key': api_key
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data.get('status') != 'OK':
                    self.stdout.write(
                        self.style.WARNING(f'    Google Places API error: {data.get("status")}')
                    )
                    continue
                
                places = data.get('results', [])[:limit]
                
                for place in places:
                    try:
                        created, updated = self.save_google_place(place, our_type, update_existing)
                        if created:
                            places_created += 1
                        elif updated:
                            places_updated += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'    Error saving place {place.get("name", "Unknown")}: {str(e)}')
                        )
                        continue
                
                self.stdout.write(f'    Found {len(places)} {google_type} places')
                
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'    Request failed for {google_type}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Google Places: Created {places_created}, Updated {places_updated} places'
            )
        )

    def save_google_place(self, place_data, place_type, update_existing):
        """Save a place from Google Places API to database"""
        
        name = place_data.get('name', '').strip()
        if not name:
            return False, False
        
        # Get place coordinates
        location = place_data.get('geometry', {}).get('location', {})
        lat = location.get('lat')
        lng = location.get('lng')
        
        # Find best matching sub-county using reverse geocoding
        sub_county = self.find_subcounty_for_coordinates(lat, lng)
        if not sub_county:
            return False, False
        
        # Check if place already exists
        existing_place = PopularPlace.objects.filter(
            place_name__iexact=name,
            sub_county=sub_county
        ).first()
        
        if existing_place:
            if update_existing:
                # Update existing place
                existing_place.place_type = place_type
                existing_place.latitude = lat
                existing_place.longitude = lng
                existing_place.popularity_score = place_data.get('rating', 0) * 20  # Convert 0-5 to 0-100
                existing_place.is_verified = True
                existing_place.save()
                return False, True
            else:
                return False, False
        
        # Create new place
        PopularPlace.objects.create(
            place_name=name,
            place_type=place_type,
            sub_county=sub_county,
            latitude=lat,
            longitude=lng,
            popularity_score=place_data.get('rating', 0) * 20,  # Convert 0-5 to 0-100
            is_verified=True
        )
        
        return True, False

    def load_from_foursquare(self, city, radius, limit, update_existing):
        """Load places from Foursquare API"""
        
        # Check if Foursquare API key is available
        if not hasattr(settings, 'FOURSQUARE_API_KEY') or not settings.FOURSQUARE_API_KEY:
            self.stdout.write(
                self.style.WARNING('Foursquare API key not configured. Skipping Foursquare.')
            )
            return
        
        # Implementation would go here
        self.stdout.write('Foursquare integration not yet implemented')

    def load_from_overpass(self, city, radius, limit, update_existing):
        """Load places from OpenStreetMap Overpass API (free)"""
        
        # Get city center coordinates
        city_coords = self.get_city_coordinates(city)
        if not city_coords:
            self.stdout.write(
                self.style.ERROR(f'Could not get coordinates for {city}')
            )
            return
        
        # Overpass API queries for different place types
        queries = [
            {
                'query': f'[out:json][timeout:25];(node["amenity"="mall"](around:{radius},{city_coords["lat"]},{city_coords["lng"]}););out;',
                'type': 'shopping'
            },
            {
                'query': f'[out:json][timeout:25];(node["amenity"="restaurant"](around:{radius},{city_coords["lat"]},{city_coords["lng"]}););out;',
                'type': 'restaurant'
            },
            {
                'query': f'[out:json][timeout:25];(node["tourism"="hotel"](around:{radius},{city_coords["lat"]},{city_coords["lng"]}););out;',
                'type': 'hotel'
            },
            {
                'query': f'[out:json][timeout:25];(node["amenity"="hospital"](around:{radius},{city_coords["lat"]},{city_coords["lng"]}););out;',
                'type': 'hospital'
            },
            {
                'query': f'[out:json][timeout:25];(node["amenity"="university"](around:{radius},{city_coords["lat"]},{city_coords["lng"]}););out;',
                'type': 'education'
            },
        ]
        
        places_created = 0
        places_updated = 0
        
        for query_data in queries:
            self.stdout.write(f'  Searching OSM for {query_data["type"]} places...')
            
            try:
                response = requests.post(
                    'https://overpass-api.de/api/interpreter',
                    data=query_data['query'],
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                places = data.get('elements', [])[:limit]
                
                for place in places:
                    try:
                        created, updated = self.save_osm_place(place, query_data['type'], update_existing)
                        if created:
                            places_created += 1
                        elif updated:
                            places_updated += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'    Error saving OSM place: {str(e)}')
                        )
                        continue
                
                self.stdout.write(f'    Found {len(places)} {query_data["type"]} places')
                
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'    OSM request failed for {query_data["type"]}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'OpenStreetMap: Created {places_created}, Updated {places_updated} places'
            )
        )

    def save_osm_place(self, place_data, place_type, update_existing):
        """Save a place from OpenStreetMap to database"""
        
        tags = place_data.get('tags', {})
        name = tags.get('name', '').strip()
        
        if not name:
            return False, False
        
        # Get coordinates
        lat = place_data.get('lat')
        lng = place_data.get('lon')
        
        if not lat or not lng:
            return False, False
        
        # Find best matching sub-county
        sub_county = self.find_subcounty_for_coordinates(lat, lng)
        if not sub_county:
            return False, False
        
        # Check if place already exists
        existing_place = PopularPlace.objects.filter(
            place_name__iexact=name,
            sub_county=sub_county
        ).first()
        
        if existing_place:
            if update_existing:
                existing_place.place_type = place_type
                existing_place.latitude = lat
                existing_place.longitude = lng
                existing_place.is_verified = True
                existing_place.save()
                return False, True
            else:
                return False, False
        
        # Create new place
        PopularPlace.objects.create(
            place_name=name,
            place_type=place_type,
            sub_county=sub_county,
            latitude=lat,
            longitude=lng,
            popularity_score=50,  # Default score for OSM places
            is_verified=True
        )
        
        return True, False

    def get_city_coordinates(self, city):
        """Get coordinates for a city"""
        
        # City coordinates (can be expanded)
        city_coords = {
            'nairobi': {'lat': -1.2920659, 'lng': 36.8219462},
            'mombasa': {'lat': -4.0434771, 'lng': 39.6682065},
            'kisumu': {'lat': -0.1021554, 'lng': 34.7617135},
            'nakuru': {'lat': -0.3030988, 'lng': 36.0800217},
            'eldoret': {'lat': 0.5143, 'lng': 35.2697},
        }
        
        coords = city_coords.get(city.lower())
        if coords:
            return coords
        
        # Try geocoding the city name
        try:
            address_service = AddressService()
            if address_service.gmaps:
                geocode_result = address_service.gmaps.geocode(f"{city}, Kenya")
                if geocode_result:
                    location = geocode_result[0]['geometry']['location']
                    return {'lat': location['lat'], 'lng': location['lng']}
        except Exception as e:
            logger.warning(f"Failed to geocode city {city}: {str(e)}")
        
        return None

    def find_subcounty_for_coordinates(self, lat, lng):
        """Find the best matching sub-county for given coordinates"""
        
        if not lat or not lng:
            return None
        
        try:
            # Try reverse geocoding to get administrative area
            address_service = AddressService()
            if address_service.gmaps:
                reverse_result = address_service.gmaps.reverse_geocode((lat, lng))
                
                if reverse_result:
                    components = reverse_result[0].get('address_components', [])
                    
                    # Look for administrative areas
                    for component in components:
                        types = component.get('types', [])
                        name = component.get('long_name', '')
                        
                        # Try to match with sub-county
                        if 'administrative_area_level_2' in types or 'sublocality' in types:
                            subcounty = SubCounty.objects.filter(
                                sub_county_name__icontains=name
                            ).first()
                            if subcounty:
                                return subcounty
                        
                        # Try to match with county
                        if 'administrative_area_level_1' in types:
                            county = County.objects.filter(
                                county_name__icontains=name
                            ).first()
                            if county:
                                # Return the first sub-county of this county
                                return county.sub_counties.first()
        
        except Exception as e:
            logger.warning(f"Failed reverse geocoding for {lat}, {lng}: {str(e)}")
        
        # Fallback: find nearest sub-county (simplified approach)
        # In production, you might want to use PostGIS for spatial queries
        try:
            # For now, just return a sub-county from Nairobi as fallback
            return SubCounty.objects.filter(
                county__county_name__icontains='Nairobi'
            ).first()
        except Exception:
            return None 