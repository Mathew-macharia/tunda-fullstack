from django.core.management.base import BaseCommand
from core.models import SystemSettings

class Command(BaseCommand):
    help = 'Initialize delivery system settings including distance-based pricing'

    def handle(self, *args, **options):
        self.stdout.write('Initializing delivery system settings...')
        
        # Initialize all default settings (including new distance-based ones)
        SystemSettings.objects.initialize_default_settings()
        
        # Display current delivery-related settings
        delivery_settings = [
            'base_delivery_fee',
            'free_delivery_threshold', 
            'weight_threshold_light',
            'weight_surcharge_light',
            'weight_threshold_heavy',
            'weight_surcharge_heavy',
            'delivery_fee_per_km',
            'max_delivery_distance_km',
            'multi_farm_consolidation_fee'
        ]
        
        self.stdout.write('\nCurrent delivery settings:')
        self.stdout.write('-' * 50)
        
        for setting_key in delivery_settings:
            try:
                setting = SystemSettings.objects.get(setting_key=setting_key)
                self.stdout.write(f'{setting_key}: {setting.setting_value} ({setting.description})')
            except SystemSettings.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'{setting_key}: Not found')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\nSuccessfully initialized delivery settings!')
        )
        
        # Show Google Maps API status
        from django.conf import settings
        if hasattr(settings, 'GOOGLE_MAPS_API_KEY') and settings.GOOGLE_MAPS_API_KEY:
            self.stdout.write(
                self.style.SUCCESS('Google Maps API key is configured.')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Google Maps API key not configured. '
                    'Distance calculation will use fallback methods.'
                )
            ) 