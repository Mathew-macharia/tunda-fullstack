import os
import django
from django.contrib.auth.hashers import make_password
from datetime import datetime
from faker import Faker
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunda.settings.base')
django.setup()

# Hashed password for "Ashesi.me254"
PASSWORD_HASH = "pbkdf2_sha256$600000$s084rxPXoUbJcI7G679MKC$PUtY0+dHWiROcD8c7ibYapXB0h+mrfaHPLnS7biGnZQ="

# Initialize Faker with 'en_US' locale for Western/English first names
fake_english = Faker('en_US')

# List of common Kenyan last names (can be expanded)
kenyan_last_names = [
    "Ochieng", "Mwangi", "Kipchoge", "Wanjiku", "Onyango", "Chebet", "Koech",
    "Njoroge", "Wambui", "Mutiso", "Cheruiyot", "Kamau", "Adhiambo", "Okoth",
    "Muthoni", "Kimani", "Juma", "Wafula", "Akinyi", "Ngugi", "Kariuki",
    "Muli", "Njeri", "Maina", "Wairimu", "Kiptoo", "Otieno", "Mburu",
    "Kwamboka", "Gichuhi", "Nyambura", "Lagat", "Omondi", "Wanjiru", "Kuria",
    "Makau", "Atieno", "Odhiambo", "Mugambi", "Waweru", "Kemboi", "Anyango",
    "Kibet", "Marete", "Wangari", "Barasa", "Awino", "Rotich", "Muriuki",
    "Nyaga", "Sifuna", "Nduku", "Kilonzo", "Wanjala", "Ouma", "Githinji",
    "Masika", "Korir", "Mugure", "Wasike", "Achieng", "Kiprono", "Muriithi",
    "Nyamu", "Wanyonyi", "Ochieng", "Muthoka", "Chepkemoi", "Kipkorir", "Mugendi",
    "Wanjohi", "Oduor", "Gathoni", "Kipkirui", "Muthiani", "Chepkoech", "Kiprop",
    "Mugwimi", "Wanjiru", "Opiyo", "Gathungu", "Kiprotich", "Muthama", "Cheptoo",
    "Kipruto", "Mugwira", "Wanjiru", "Owuor", "Gatimu", "Kipchumba", "Muthiani",
    "Chepkirui", "Kipkemboi", "Mugwira", "Wanjiru", "Ochieng", "Muthoka", "Chepkemoi"
]


def generate_kenyan_phone_number(index):
    # Generate a realistic-looking Kenyan phone number (e.g., starting with 07 or 2547)
    # and ensure uniqueness by incorporating the index
    # Using a common prefix like 07XX or 2547XX
    base_number = 700000000 + index # Start from a base and increment
    return f"254{base_number}"

def generate_sql_script(num_users=200, num_farmers=30, num_riders=15, num_admins=1):
    sql_statements = []
    table_name = "users_user"
    
    # Columns in the users_user table (based on backend/users/models.py)
    columns = [
        "password", "last_login", "is_superuser", "first_name", "last_name",
        "phone_number", "user_role", "email", "profile_photo_url", "is_active",
        "preferred_language", "sms_notifications", "email_notifications",
        "marketing_notifications", "order_updates", "weather_alerts",
        "price_alerts", "last_login_ip", "is_verified", "verification_code",
        "verification_code_expires", "created_at", "updated_at", "is_staff"
    ]

    user_index = 0

    # Generate admin users
    for i in range(num_admins):
        first_name = fake_english.first_name()
        last_name = random.choice(kenyan_last_names)
        phone_number = generate_kenyan_phone_number(user_index)
        email = f"{first_name.lower()}.{last_name.lower()}.admin{i+1}@example.com"
        user_role = "admin"
        is_staff = 1
        is_superuser = 1
        
        sql_statements.append(
            f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ("
            f"'{PASSWORD_HASH}', NULL, {is_superuser}, '{first_name}', '{last_name}', "
            f"'{phone_number}', '{user_role}', '{email}', NULL, 1, "
            f"'sw', 1, 1, "
            f"0, 1, 1, "
            f"1, NULL, 0, NULL, "
            f"NULL, NOW(), NOW(), {is_staff});"
        )
        user_index += 1

    # Generate farmer users
    for i in range(num_farmers):
        first_name = fake_english.first_name()
        last_name = random.choice(kenyan_last_names)
        phone_number = generate_kenyan_phone_number(user_index)
        email = f"{first_name.lower()}.{last_name.lower()}.farmer{i+1}@example.com"
        user_role = "farmer"
        is_staff = 0
        is_superuser = 0
        
        sql_statements.append(
            f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ("
            f"'{PASSWORD_HASH}', NULL, {is_superuser}, '{first_name}', '{last_name}', "
            f"'{phone_number}', '{user_role}', '{email}', NULL, 1, "
            f"'sw', 1, 1, "
            f"0, 1, 1, "
            f"1, NULL, 0, NULL, "
            f"NULL, NOW(), NOW(), {is_staff});"
        )
        user_index += 1

    # Generate rider users
    for i in range(num_riders):
        first_name = fake_english.first_name()
        last_name = random.choice(kenyan_last_names)
        phone_number = generate_kenyan_phone_number(user_index)
        email = f"{first_name.lower()}.{last_name.lower()}.rider{i+1}@example.com"
        user_role = "rider"
        is_staff = 0
        is_superuser = 0
        
        sql_statements.append(
            f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ("
            f"'{PASSWORD_HASH}', NULL, {is_superuser}, '{first_name}', '{last_name}', "
            f"'{phone_number}', '{user_role}', '{email}', NULL, 1, "
            f"'sw', 1, 1, "
            f"0, 1, 0, " # Riders don't need weather/price alerts
            f"0, NULL, 0, NULL, "
            f"NULL, NOW(), NOW(), {is_staff});"
        )
        user_index += 1

    # Generate customer users to reach num_users total
    current_users = num_admins + num_farmers + num_riders
    num_customers = num_users - current_users
    if num_customers < 0:
        num_customers = 0 # Ensure we don't try to create negative customers

    for i in range(num_customers):
        first_name = fake_english.first_name()
        last_name = random.choice(kenyan_last_names)
        phone_number = generate_kenyan_phone_number(user_index)
        email = f"{first_name.lower()}.{last_name.lower()}.customer{i+1}@example.com"
        user_role = "customer"
        is_staff = 0
        is_superuser = 0
        
        sql_statements.append(
            f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ("
            f"'{PASSWORD_HASH}', NULL, {is_superuser}, '{first_name}', '{last_name}', "
            f"'{phone_number}', '{user_role}', '{email}', NULL, 1, "
            f"'sw', 1, 1, "
            f"0, 1, 0, " # Customers don't need weather/price alerts
            f"0, NULL, 0, NULL, "
            f"NULL, NOW(), NOW(), {is_staff});"
        )
        user_index += 1
        
    return "\n".join(sql_statements)

if __name__ == "__main__":
    # Ensure at least 200 users, with specified farmers and riders
    total_users_needed = max(200, 30 + 15 + 1) # At least 200, or sum of specified roles if higher
    
    sql_script_content = generate_sql_script(
        num_users=total_users_needed,
        num_farmers=30,
        num_riders=15,
        num_admins=1
    )
    
    output_file_path = "backend/create_users.sql"
    with open(output_file_path, "w") as f:
        f.write(sql_script_content)
    print(f"SQL script generated successfully at {output_file_path}")
