from django.core.management.base import BaseCommand
from locations.models import County, SubCounty

class Command(BaseCommand):
    help = 'Populate counties and sub-counties with sample Kenya data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating counties and sub-counties...'))

        counties_data = {
            'Nairobi': {
                'code': 'NRB',
                'sub_counties': [
                    ('Westlands', 'WLD'),
                    ('Dagoretti North', 'DGN'),
                    ('Dagoretti South', 'DGS'),
                    ('Langata', 'LNG'),
                    ('Kibra', 'KBR'),
                    ('Roysambu', 'RSB'),
                    ('Kasarani', 'KSR'),
                    ('Ruaraka', 'RRK'),
                    ('Embakasi South', 'EBS'),
                    ('Embakasi North', 'EBN'),
                    ('Embakasi Central', 'EBC'),
                    ('Embakasi East', 'EBE'),
                    ('Embakasi West', 'EBW'),
                    ('Makadara', 'MKD'),
                    ('Kamukunji', 'KMK'),
                    ('Starehe', 'STR'),
                    ('Mathare', 'MTH'),
                ]
            },
            'Kiambu': {
                'code': 'KMB',
                'sub_counties': [
                    ('Thika Town', 'TKT'),
                    ('Ruiru', 'RRU'),
                    ('Juja', 'JJA'),
                    ('Gatundu South', 'GTS'),
                    ('Gatundu North', 'GTN'),
                    ('Githunguri', 'GTH'),
                    ('Kiambu Town', 'KMT'),
                    ('Kiambaa', 'KMA'),
                    ('Kabete', 'KBT'),
                    ('Kikuyu', 'KKY'),
                    ('Limuru', 'LMR'),
                    ('Lari', 'LRI'),
                ]
            },
            'Nakuru': {
                'code': 'NKR',
                'sub_counties': [
                    ('Nakuru Town East', 'NTE'),
                    ('Nakuru Town West', 'NTW'),
                    ('Bahati', 'BHT'),
                    ('Subukia', 'SBK'),
                    ('Rongai', 'RNG'),
                    ('Menengai West', 'MNW'),
                    ('Molo', 'MLO'),
                    ('Njoro', 'NJR'),
                    ('Naivasha', 'NVS'),
                    ('Gilgil', 'GGL'),
                    ('Kuresoi South', 'KRS'),
                    ('Kuresoi North', 'KRN'),
                ]
            },
            'Mombasa': {
                'code': 'MSA',
                'sub_counties': [
                    ('Changamwe', 'CGW'),
                    ('Jomba', 'JMB'),
                    ('Kisauni', 'KSN'),
                    ('Nyali', 'NYL'),
                    ('Likoni', 'LKN'),
                    ('Mvita', 'MVT'),
                ]
            },
            'Kajiado': {
                'code': 'KJD',
                'sub_counties': [
                    ('Kajiado North', 'KJN'),
                    ('Kajiado Central', 'KJC'),
                    ('Kajiado East', 'KJE'),
                    ('Kajiado West', 'KJW'),
                    ('Kajiado South', 'KJS'),
                ]
            },
            'Machakos': {
                'code': 'MCH',
                'sub_counties': [
                    ('Machakos Town', 'MCT'),
                    ('Athi River', 'ATR'),
                    ('Mavoko', 'MVK'),
                    ('Kathiani', 'KTH'),
                    ('Matungulu', 'MTG'),
                    ('Yatta', 'YTT'),
                    ('Kangundo', 'KGD'),
                    ('Masinga', 'MSG'),
                ]
            },
        }

        # Create counties and sub-counties
        for county_name, county_info in counties_data.items():
            county, created = County.objects.get_or_create(
                county_name=county_name,
                defaults={'county_code': county_info['code']}
            )
            
            if created:
                self.stdout.write(f'Created county: {county_name}')
            else:
                self.stdout.write(f'County already exists: {county_name}')

            # Create sub-counties
            for sub_county_name, sub_county_code in county_info['sub_counties']:
                sub_county, created = SubCounty.objects.get_or_create(
                    county=county,
                    sub_county_name=sub_county_name,
                    defaults={'sub_county_code': sub_county_code}
                )
                
                if created:
                    self.stdout.write(f'  Created sub-county: {sub_county_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated {County.objects.count()} counties '
                f'and {SubCounty.objects.count()} sub-counties!'
            )
        ) 