from django.core.management.base import BaseCommand
from core.models import SystemSettings


class Command(BaseCommand):
    help = 'Initialize M-Pesa settings in the system'

    def handle(self, *args, **options):
        """Initialize M-Pesa settings"""
        
        # Initialize default settings (this will add M-Pesa settings if they don't exist)
        SystemSettings.objects.initialize_default_settings()
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully initialized M-Pesa settings. '
                'Please update the following settings in the admin panel or via management commands:'
            )
        )
        
        # List M-Pesa settings that need to be configured
        mpesa_settings = [
            'mpesa_consumer_key',
            'mpesa_consumer_secret', 
            'mpesa_business_shortcode',
            'mpesa_passkey',
            'mpesa_environment',
            'mpesa_callback_url'
        ]
        
        self.stdout.write('\nM-Pesa Settings to Configure:')
        for setting in mpesa_settings:
            try:
                current_value = SystemSettings.objects.get_setting(setting, 'NOT_SET')
                status = '✓ SET' if current_value and current_value != 'NOT_SET' else '✗ NOT SET'
                self.stdout.write(f'  {setting}: {status}')
            except:
                self.stdout.write(f'  {setting}: ✗ NOT SET')
        
        self.stdout.write(
            '\nTo set these values, use the admin panel or the set_mpesa_credentials command.'
        ) 