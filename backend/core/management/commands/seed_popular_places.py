from django.core.management.base import BaseCommand
from django.db import transaction
from locations.models import SubCounty
from core.models import PopularPlace
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seed initial popular places data for address validation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing popular places before seeding'
        )

    def handle(self, *args, **options):
        clear_existing = options['clear']
        
        if clear_existing:
            self.stdout.write('Clearing existing popular places...')
            PopularPlace.objects.all().delete()
        
        self.stdout.write('Seeding popular places...')
        
        # Curated list of important places in Kenya
        # This is a starter set - production would load from external APIs
        places_data = [
            # Nairobi - Shopping Centers
            {'name': 'Westgate Shopping Mall', 'type': 'shopping', 'subcounty': 'Westlands Sub County', 'alternatives': ['Westgate Mall', 'Westgate'], 'score': 95},
            {'name': 'Sarit Centre', 'type': 'shopping', 'subcounty': 'Westlands Sub County', 'alternatives': ['Sarit Center'], 'score': 90},
            {'name': 'Village Market', 'type': 'shopping', 'subcounty': 'Westlands Sub County', 'alternatives': [], 'score': 85},
            {'name': 'Two Rivers Mall', 'type': 'shopping', 'subcounty': 'Westlands Sub County', 'alternatives': [], 'score': 80},
            {'name': 'Garden City Mall', 'type': 'shopping', 'subcounty': 'Kasarani Sub County', 'alternatives': ['Garden City'], 'score': 75},
            {'name': 'Thika Road Mall', 'type': 'shopping', 'subcounty': 'Kasarani Sub County', 'alternatives': ['TRM'], 'score': 70},
            {'name': 'Junction Mall', 'type': 'shopping', 'subcounty': 'Dagoretti North Sub County', 'alternatives': ['The Junction'], 'score': 65},
            {'name': 'Yaya Centre', 'type': 'shopping', 'subcounty': 'Dagoretti North Sub County', 'alternatives': ['Yaya Center'], 'score': 60},
            {'name': 'Galleria Mall', 'type': 'shopping', 'subcounty': 'Langata Sub County', 'alternatives': ['Galleria'], 'score': 55},
            {'name': 'The Hub Karen', 'type': 'shopping', 'subcounty': 'Langata Sub County', 'alternatives': ['Hub Karen'], 'score': 50},
            
            # Nairobi - Restaurants & Hotels
            {'name': 'Carnivore Restaurant', 'type': 'restaurant', 'subcounty': 'Langata Sub County', 'alternatives': ['Carnivore'], 'score': 85},
            {'name': 'Java House', 'type': 'restaurant', 'subcounty': 'Westlands Sub County', 'alternatives': [], 'score': 70},
            {'name': 'Artcaffe', 'type': 'restaurant', 'subcounty': 'Westlands Sub County', 'alternatives': ['Art Caffe'], 'score': 65},
            {'name': 'Sankara Nairobi', 'type': 'hotel', 'subcounty': 'Westlands Sub County', 'alternatives': ['Sankara Hotel'], 'score': 80},
            {'name': 'Villa Rosa Kempinski', 'type': 'hotel', 'subcounty': 'Westlands Sub County', 'alternatives': ['Kempinski'], 'score': 85},
            {'name': 'Serena Hotel', 'type': 'hotel', 'subcounty': 'Starehe Sub County', 'alternatives': ['Nairobi Serena'], 'score': 80},
            {'name': 'Hilton Nairobi', 'type': 'hotel', 'subcounty': 'Starehe Sub County', 'alternatives': ['Hilton'], 'score': 75},
            
            # Nairobi - Attractions
            {'name': 'Nairobi National Park', 'type': 'attraction', 'subcounty': 'Langata Sub County', 'alternatives': ['National Park'], 'score': 95},
            {'name': 'Giraffe Centre', 'type': 'attraction', 'subcounty': 'Langata Sub County', 'alternatives': ['Giraffe Center'], 'score': 90},
            {'name': 'David Sheldrick Elephant Orphanage', 'type': 'attraction', 'subcounty': 'Langata Sub County', 'alternatives': ['Elephant Orphanage', 'David Sheldrick'], 'score': 85},
            {'name': 'Karen Blixen Museum', 'type': 'attraction', 'subcounty': 'Langata Sub County', 'alternatives': ['Karen Blixen'], 'score': 70},
            {'name': 'Nairobi National Museum', 'type': 'attraction', 'subcounty': 'Starehe Sub County', 'alternatives': ['National Museum'], 'score': 65},
            {'name': 'Uhuru Park', 'type': 'park', 'subcounty': 'Starehe Sub County', 'alternatives': [], 'score': 60},
            {'name': 'Central Park', 'type': 'park', 'subcounty': 'Starehe Sub County', 'alternatives': [], 'score': 55},
            {'name': 'Karura Forest', 'type': 'park', 'subcounty': 'Westlands Sub County', 'alternatives': [], 'score': 70},
            
            # Nairobi - Areas
            {'name': 'Westlands', 'type': 'area', 'subcounty': 'Westlands Sub County', 'alternatives': [], 'score': 90},
            {'name': 'Kilimani', 'type': 'area', 'subcounty': 'Dagoretti North Sub County', 'alternatives': [], 'score': 85},
            {'name': 'Karen', 'type': 'area', 'subcounty': 'Langata Sub County', 'alternatives': [], 'score': 80},
            {'name': 'Runda', 'type': 'area', 'subcounty': 'Westlands Sub County', 'alternatives': [], 'score': 75},
            {'name': 'Lavington', 'type': 'area', 'subcounty': 'Dagoretti North Sub County', 'alternatives': [], 'score': 70},
            {'name': 'Kileleshwa', 'type': 'area', 'subcounty': 'Dagoretti North Sub County', 'alternatives': [], 'score': 65},
            {'name': 'Parklands', 'type': 'area', 'subcounty': 'Westlands Sub County', 'alternatives': [], 'score': 60},
            {'name': 'Eastleigh', 'type': 'area', 'subcounty': 'Kamukunji Sub County', 'alternatives': [], 'score': 70},
            {'name': 'South C', 'type': 'area', 'subcounty': 'Langata Sub County', 'alternatives': [], 'score': 65},
            {'name': 'South B', 'type': 'area', 'subcounty': 'Langata Sub County', 'alternatives': [], 'score': 60},
            {'name': 'Kibera', 'type': 'area', 'subcounty': 'Kibra Sub County', 'alternatives': [], 'score': 55},
            {'name': 'Kasarani', 'type': 'area', 'subcounty': 'Kasarani Sub County', 'alternatives': [], 'score': 50},
            {'name': 'Roysambu', 'type': 'area', 'subcounty': 'Roysambu Sub County', 'alternatives': [], 'score': 45},
            {'name': 'Embakasi', 'type': 'area', 'subcounty': 'Embakasi East Sub County', 'alternatives': [], 'score': 50},
            
            # Nairobi - Transport
            {'name': 'Jomo Kenyatta International Airport', 'type': 'transport', 'subcounty': 'Embakasi South Sub County', 'alternatives': ['JKIA', 'Jomo Kenyatta Airport'], 'score': 100},
            {'name': 'Wilson Airport', 'type': 'transport', 'subcounty': 'Langata Sub County', 'alternatives': [], 'score': 80},
            {'name': 'Railways Station', 'type': 'transport', 'subcounty': 'Starehe Sub County', 'alternatives': ['Railway Station'], 'score': 70},
            
            # Nairobi - Hospitals
            {'name': 'Kenyatta National Hospital', 'type': 'hospital', 'subcounty': 'Starehe Sub County', 'alternatives': ['KNH'], 'score': 95},
            {'name': 'Nairobi Hospital', 'type': 'hospital', 'subcounty': 'Starehe Sub County', 'alternatives': [], 'score': 85},
            {'name': 'Aga Khan Hospital', 'type': 'hospital', 'subcounty': 'Starehe Sub County', 'alternatives': ['Aga Khan'], 'score': 80},
            {'name': 'Karen Hospital', 'type': 'hospital', 'subcounty': 'Langata Sub County', 'alternatives': [], 'score': 70},
            
            # Nairobi - Education
            {'name': 'University of Nairobi', 'type': 'education', 'subcounty': 'Starehe Sub County', 'alternatives': ['UoN'], 'score': 90},
            {'name': 'Kenyatta University', 'type': 'education', 'subcounty': 'Kasarani Sub County', 'alternatives': ['KU'], 'score': 85},
            {'name': 'Strathmore University', 'type': 'education', 'subcounty': 'Dagoretti North Sub County', 'alternatives': ['Strathmore'], 'score': 80},
            {'name': 'USIU', 'type': 'education', 'subcounty': 'Kasarani Sub County', 'alternatives': ['United States International University'], 'score': 75},
            
            # Other Cities - Key Places
            {'name': 'Nyali Cinemax', 'type': 'shopping', 'subcounty': 'Nyali', 'alternatives': ['Cinemax'], 'score': 70},
            {'name': 'Fort Jesus', 'type': 'attraction', 'subcounty': 'Mvita', 'alternatives': [], 'score': 85},
            {'name': 'Mega Plaza', 'type': 'shopping', 'subcounty': 'Kisumu Central', 'alternatives': [], 'score': 60},
            {'name': 'Westside Mall', 'type': 'shopping', 'subcounty': 'Nakuru Town West', 'alternatives': [], 'score': 55},
            {'name': 'Zion Mall', 'type': 'shopping', 'subcounty': 'Kapseret', 'alternatives': [], 'score': 50},
        ]
        
        places_created = 0
        places_skipped = 0
        
        with transaction.atomic():
            for place_data in places_data:
                try:
                    # Find the sub-county
                    subcounty = SubCounty.objects.filter(
                        sub_county_name__iexact=place_data['subcounty']
                    ).first()
                    
                    if not subcounty:
                        # Try partial match
                        subcounty = SubCounty.objects.filter(
                            sub_county_name__icontains=place_data['subcounty'].split()[0]
                        ).first()
                    
                    if not subcounty:
                        self.stdout.write(f"  ⚠ Sub-county not found: {place_data['subcounty']}")
                        places_skipped += 1
                        continue
                    
                    # Check if place already exists
                    existing_place = PopularPlace.objects.filter(
                        place_name__iexact=place_data['name'],
                        sub_county=subcounty
                    ).first()
                    
                    if existing_place:
                        self.stdout.write(f"  ↻ Already exists: {place_data['name']}")
                        places_skipped += 1
                        continue
                    
                    # Create the place
                    place = PopularPlace.objects.create(
                        place_name=place_data['name'],
                        place_type=place_data['type'],
                        sub_county=subcounty,
                        alternative_names=place_data.get('alternatives', []),
                        popularity_score=place_data.get('score', 50),
                        is_verified=True
                    )
                    
                    self.stdout.write(f"  ✓ Created: {place.place_name} ({subcounty.sub_county_name})")
                    places_created += 1
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ Error creating {place_data['name']}: {str(e)}")
                    places_skipped += 1
                    continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Seeding complete! Created {places_created} places, skipped {places_skipped}'
            )
        ) 