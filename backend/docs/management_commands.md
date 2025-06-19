# Management Commands

This document outlines the available Django management commands for the Tunda Soko marketplace project.

## Location Commands

### populate_locations

Populates the database with Kenya counties and sub-counties data.

```bash
python manage.py populate_locations
```

**What it creates:**
- Counties (Nairobi, Kiambu, Nakuru, Mombasa, Kajiado, Machakos)
- Sub-counties for each county (60 total)

**Usage Example:**
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# Run the command
python manage.py populate_locations
```

## Product Commands

### create_sample_data

Creates comprehensive sample data for development and testing.

```bash
python manage.py create_sample_data [--reset]
```

**Options:**
- `--reset`: Clear existing data before creating samples

**What it creates:**
- Sample locations (12 locations across counties)
- Product categories (5 categories: Vegetables, Fruits, Herbs, Grains, Legumes)
- Products (16 products across categories)
- Sample farmers (5 farmers with verified accounts)
- Sample customers (2 customers with verified accounts)
- Sample farms (5 farms with different characteristics)
- Product listings (20+ listings with realistic pricing)

**Sample Data Details:**

### Farmers Created
- John Mwangi (0712345001)
- Mary Njoki (0712345002)  
- Peter Kamau (0712345003)
- Grace Wanjiku (0712345004)
- David Kiprotich (0712345005)

**Default Password:** `password123`

### Customers Created
- Sarah Wanjiku (0712346001)
- James Ochieng (0712346002)

**Default Password:** `password123`

### Product Categories
1. **Vegetables** - Fresh leafy greens and vegetables
2. **Fruits** - Fresh seasonal fruits
3. **Herbs** - Fresh herbs and spices
4. **Grains** - Cereals and grain products
5. **Legumes** - Beans, peas, and legumes

### Sample Products
- **Vegetables:** Tomatoes, Spinach, Peppers, Kales, Carrots
- **Fruits:** Bananas, Mangoes, Passion Fruits, Avocados
- **Herbs:** Coriander, Mint, Rosemary
- **Grains:** Maize, Rice (non-perishable)
- **Legumes:** Green Beans, Peas

**Usage Examples:**
```bash
# Create sample data
python manage.py create_sample_data

# Reset and create fresh sample data
python manage.py create_sample_data --reset
```

## Usage Workflow

For setting up a development environment:

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Apply migrations
python manage.py migrate

# 4. Create counties and sub-counties
python manage.py populate_locations

# 5. Create sample marketplace data
python manage.py create_sample_data

# 6. Create a superuser (optional)
python manage.py createsuperuser
```

## Notes

- All sample users have default password: `password123`
- The `create_sample_data` command depends on counties being populated first
- Use `--reset` flag carefully as it will delete existing data
- Sample data includes realistic pricing and farm details
- All farmers and customers are created as verified users

## Admin Access

After running the commands, you can access:

- **Admin Panel:** http://localhost:8000/admin/
- **API Root:** http://localhost:8000/api/
- **Sample Farmer Login:** Any farmer phone number + password123
- **Sample Customer Login:** Any customer phone number + password123 

This document outlines the available Django management commands for the Tunda Soko marketplace project.

## Location Commands

### populate_locations

Populates the database with Kenya counties and sub-counties data.

```bash
python manage.py populate_locations
```

**What it creates:**
- Counties (Nairobi, Kiambu, Nakuru, Mombasa, Kajiado, Machakos)
- Sub-counties for each county (60 total)

**Usage Example:**
```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# Run the command
python manage.py populate_locations
```

## Product Commands

### create_sample_data

Creates comprehensive sample data for development and testing.

```bash
python manage.py create_sample_data [--reset]
```

**Options:**
- `--reset`: Clear existing data before creating samples

**What it creates:**
- Sample locations (12 locations across counties)
- Product categories (5 categories: Vegetables, Fruits, Herbs, Grains, Legumes)
- Products (16 products across categories)
- Sample farmers (5 farmers with verified accounts)
- Sample customers (2 customers with verified accounts)
- Sample farms (5 farms with different characteristics)
- Product listings (20+ listings with realistic pricing)

**Sample Data Details:**

### Farmers Created
- John Mwangi (0712345001)
- Mary Njoki (0712345002)  
- Peter Kamau (0712345003)
- Grace Wanjiku (0712345004)
- David Kiprotich (0712345005)

**Default Password:** `password123`

### Customers Created
- Sarah Wanjiku (0712346001)
- James Ochieng (0712346002)

**Default Password:** `password123`

### Product Categories
1. **Vegetables** - Fresh leafy greens and vegetables
2. **Fruits** - Fresh seasonal fruits
3. **Herbs** - Fresh herbs and spices
4. **Grains** - Cereals and grain products
5. **Legumes** - Beans, peas, and legumes

### Sample Products
- **Vegetables:** Tomatoes, Spinach, Peppers, Kales, Carrots
- **Fruits:** Bananas, Mangoes, Passion Fruits, Avocados
- **Herbs:** Coriander, Mint, Rosemary
- **Grains:** Maize, Rice (non-perishable)
- **Legumes:** Green Beans, Peas

**Usage Examples:**
```bash
# Create sample data
python manage.py create_sample_data

# Reset and create fresh sample data
python manage.py create_sample_data --reset
```

## Usage Workflow

For setting up a development environment:

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Apply migrations
python manage.py migrate

# 4. Create counties and sub-counties
python manage.py populate_locations

# 5. Create sample marketplace data
python manage.py create_sample_data

# 6. Create a superuser (optional)
python manage.py createsuperuser
```

## Notes

- All sample users have default password: `password123`
- The `create_sample_data` command depends on counties being populated first
- Use `--reset` flag carefully as it will delete existing data
- Sample data includes realistic pricing and farm details
- All farmers and customers are created as verified users

## Admin Access

After running the commands, you can access:

- **Admin Panel:** http://localhost:8000/admin/
- **API Root:** http://localhost:8000/api/
- **Sample Farmer Login:** Any farmer phone number + password123
- **Sample Customer Login:** Any customer phone number + password123 
 