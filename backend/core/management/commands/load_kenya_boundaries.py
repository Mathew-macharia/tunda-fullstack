import json
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from locations.models import County, SubCounty
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load Kenya administrative boundaries data from external sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['github', 'api', 'hdx'],
            default='github',
            help='Data source to use (github, api, or hdx)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing records instead of skipping them'
        )

    def handle(self, *args, **options):
        source = options['source']
        update = options['update']
        
        self.stdout.write(
            self.style.SUCCESS(f'Loading Kenya boundaries from {source}...')
        )
        
        try:
            if source == 'github':
                self.load_from_github(update)
            elif source == 'api':
                self.load_from_api(update)
            elif source == 'hdx':
                self.load_from_hdx(update)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading data: {str(e)}')
            )
            logger.error(f'Error loading Kenya boundaries: {str(e)}')

    def load_from_github(self, update=False):
        """Load data from Mondieki's GitHub repository"""
        
        # GitHub raw URL for counties data
        counties_url = "https://raw.githubusercontent.com/Mondieki/kenya-counties-subcounties/master/counties.json"
        
        try:
            self.stdout.write('Downloading counties data from GitHub...')
            response = requests.get(counties_url, timeout=30)
            response.raise_for_status()
            
            counties_data = response.json()
            
            self.stdout.write(f'Processing {len(counties_data)} counties...')
            
            with transaction.atomic():
                counties_created = 0
                subcounties_created = 0
                
                for county_data in counties_data:
                    # Create or update county
                    county_name = county_data.get('name', '').strip()
                    county_code = county_data.get('code', 0)
                    county_capital = county_data.get('capital', '').strip()
                    
                    if not county_name:
                        continue
                    
                    county, created = County.objects.get_or_create(
                        county_name=county_name,
                        defaults={
                            'county_code': str(county_code).zfill(2)  # Ensure 2-digit code
                        }
                    )
                    
                    if created:
                        counties_created += 1
                        self.stdout.write(f'  ✓ Created county: {county_name}')
                    elif update:
                        county.county_code = str(county_code).zfill(2)
                        county.save()
                        self.stdout.write(f'  ↻ Updated county: {county_name}')
                    
                    # Process sub-counties
                    sub_counties = county_data.get('sub_counties', [])
                    for sub_county_name in sub_counties:
                        if not sub_county_name or not sub_county_name.strip():
                            continue
                            
                        sub_county_name = sub_county_name.strip()
                        
                        subcounty, created = SubCounty.objects.get_or_create(
                            sub_county_name=sub_county_name,
                            county=county,
                            defaults={'sub_county_code': f"{county.county_code}{len(county.sub_counties.all()):02d}"}
                        )
                        
                        if created:
                            subcounties_created += 1
                            self.stdout.write(f'    ✓ Created sub-county: {sub_county_name}')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully loaded {counties_created} counties and {subcounties_created} sub-counties'
                    )
                )
                
        except requests.RequestException as e:
            raise Exception(f"Failed to download data from GitHub: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON data: {str(e)}")

    def load_from_api(self, update=False):
        """Load data from Kenya Administrative API"""
        
        api_base_url = "https://kenya-administrative-boundaries-api-ken-admin-api.vercel.app/api"
        
        try:
            # Get counties
            self.stdout.write('Downloading counties from API...')
            counties_response = requests.get(f"{api_base_url}/counties", timeout=30)
            counties_response.raise_for_status()
            counties_data = counties_response.json()
            
            self.stdout.write(f'Processing {len(counties_data)} counties...')
            
            with transaction.atomic():
                counties_created = 0
                subcounties_created = 0
                
                for county_data in counties_data:
                    county_name = county_data.get('name', '').strip()
                    county_code = county_data.get('code', 0)
                    
                    if not county_name:
                        continue
                    
                    county, created = County.objects.get_or_create(
                        county_name=county_name,
                        defaults={'county_code': county_code}
                    )
                    
                    if created:
                        counties_created += 1
                        self.stdout.write(f'  ✓ Created county: {county_name}')
                
                # Get constituencies (which contain sub-county information)
                self.stdout.write('Downloading constituencies from API...')
                constituencies_response = requests.get(f"{api_base_url}/constituencies", timeout=30)
                constituencies_response.raise_for_status()
                constituencies_data = constituencies_response.json()
                
                for constituency_data in constituencies_data:
                    county_name = constituency_data.get('county', '').strip()
                    constituency_name = constituency_data.get('name', '').strip()
                    
                    if not county_name or not constituency_name:
                        continue
                    
                    try:
                        county = County.objects.get(county_name=county_name)
                        
                        subcounty, created = SubCounty.objects.get_or_create(
                            sub_county_name=constituency_name,
                            county=county,
                            defaults={'sub_county_code': f"{county.county_code}{len(county.sub_counties.all()):02d}"}
                        )
                        
                        if created:
                            subcounties_created += 1
                            self.stdout.write(f'    ✓ Created sub-county: {constituency_name}')
                            
                    except County.DoesNotExist:
                        self.stdout.write(f'    ⚠ County not found: {county_name}')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully loaded {counties_created} counties and {subcounties_created} sub-counties'
                    )
                )
                
        except requests.RequestException as e:
            raise Exception(f"Failed to download data from API: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON data: {str(e)}")

    def load_from_hdx(self, update=False):
        """Load data from Humanitarian Data Exchange"""
        
        # Note: HDX provides shapefiles which require additional processing
        # For now, we'll use a simplified approach with known data
        self.stdout.write('HDX integration requires shapefile processing - using fallback data...')
        
        # Fallback to GitHub method
        self.load_from_github(update) 