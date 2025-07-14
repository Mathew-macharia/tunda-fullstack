from django.core.management.base import BaseCommand, CommandError
from core.models import SystemSettings


class Command(BaseCommand):
    help = 'Set M-Pesa API credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--consumer-key',
            type=str,
            help='M-Pesa Consumer Key from Daraja Portal',
        )
        parser.add_argument(
            '--consumer-secret',
            type=str,
            help='M-Pesa Consumer Secret from Daraja Portal',
        )
        parser.add_argument(
            '--business-shortcode',
            type=str,
            help='M-Pesa Business Shortcode (Till/PayBill Number)',
        )
        parser.add_argument(
            '--passkey',
            type=str,
            help='M-Pesa STK Push Passkey',
        )
        parser.add_argument(
            '--environment',
            type=str,
            choices=['sandbox', 'production'],
            default='sandbox',
            help='M-Pesa Environment (sandbox/production)',
        )
        parser.add_argument(
            '--callback-url',
            type=str,
            help='M-Pesa Callback URL for payment notifications',
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Set credentials interactively',
        )

    def handle(self, *args, **options):
        """Set M-Pesa credentials"""
        
        if options['interactive']:
            self.handle_interactive()
        else:
            self.handle_arguments(options)

    def handle_interactive(self):
        """Handle interactive credential setting"""
        self.stdout.write(
            self.style.WARNING(
                'Setting M-Pesa credentials interactively. '
                'Press Enter to skip a setting and keep current value.'
            )
        )
        
        settings_to_set = [
            ('mpesa_consumer_key', 'Consumer Key'),
            ('mpesa_consumer_secret', 'Consumer Secret'),
            ('mpesa_business_shortcode', 'Business Shortcode'),
            ('mpesa_passkey', 'Passkey'),
            ('mpesa_environment', 'Environment (sandbox/production)'),
            ('mpesa_callback_url', 'Callback URL'),
        ]
        
        for setting_key, display_name in settings_to_set:
            current_value = SystemSettings.objects.get_setting(setting_key, '')
            current_display = f' (current: {current_value})' if current_value else ''
            
            value = input(f'{display_name}{current_display}: ').strip()
            
            if value:
                # Validate environment
                if setting_key == 'mpesa_environment' and value not in ['sandbox', 'production']:
                    self.stdout.write(
                        self.style.ERROR(f'Invalid environment: {value}. Must be sandbox or production.')
                    )
                    continue
                
                # Update setting
                setting, created = SystemSettings.objects.get_or_create(
                    setting_key=setting_key,
                    defaults={'setting_value': value, 'setting_type': 'string'}
                )
                if not created:
                    setting.setting_value = value
                    setting.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated {display_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\nM-Pesa credentials updated successfully!')
        )

    def handle_arguments(self, options):
        """Handle command line arguments"""
        settings_map = {
            'consumer_key': 'mpesa_consumer_key',
            'consumer_secret': 'mpesa_consumer_secret',
            'business_shortcode': 'mpesa_business_shortcode',
            'passkey': 'mpesa_passkey',
            'environment': 'mpesa_environment',
            'callback_url': 'mpesa_callback_url',
        }
        
        updated_count = 0
        
        for arg_name, setting_key in settings_map.items():
            value = options.get(arg_name)
            if value:
                setting, created = SystemSettings.objects.get_or_create(
                    setting_key=setting_key,
                    defaults={'setting_value': value, 'setting_type': 'string'}
                )
                if not created:
                    setting.setting_value = value
                    setting.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated {setting_key}: {value}')
                )
                updated_count += 1
        
        if updated_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    'No credentials provided. Use --interactive flag for interactive setup '
                    'or provide specific arguments.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nUpdated {updated_count} M-Pesa settings!')
            ) 