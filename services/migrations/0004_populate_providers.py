from django.db import migrations
from django.contrib.auth.hashers import make_password

def populate_providers(apps, schema_editor):
    ServiceProvider = apps.get_model('services', 'ServiceProvider')
    ServiceCategory = apps.get_model('services', 'ServiceCategory')
    User = apps.get_model('auth', 'User')
    
    # Provider data with 5 providers per category
    PROVIDER_DATA = {
        "Women's Salon & Spa": [
            {
                "name": "Sarah Martinez",
                "age": 32,
                "rating": 4.9,
                "price_per_hour": 45,
                "contact_number": "+1 (555) 234-5678",
                "address": "123 Beauty Lane, Downtown District",
                "service_code": "WS001",
                "description": "Certified hair stylist with 12+ years of experience specializing in modern cuts, balayage, and bridal styling. Passionate about bringing out your natural beauty with personalized care and attention to detail.",
            },
            {
                "name": "Emily Chen",
                "age": 28,
                "rating": 5.0,
                "price_per_hour": 50,
                "contact_number": "+1 (555) 345-6789",
                "address": "456 Glam Street, Midtown Plaza",
                "service_code": "WS002",
                "description": "Award-winning makeup artist and beauty expert. Specializing in Korean beauty treatments, facial spa services, and event makeup. Your confidence is my canvas!",
            },
            {
                "name": "Priya Sharma",
                "age": 35,
                "rating": 4.8,
                "price_per_hour": 42,
                "contact_number": "+1 (555) 456-7890",
                "address": "789 Salon Avenue, Eastside",
                "service_code": "WS003",
                "description": "Expert in traditional and contemporary hair treatments. From classic updos to trendy highlights, I bring 15 years of salon experience to make every visit special. Walk in stressed, walk out fabulous!",
            },
            {
                "name": "Jessica Williams",
                "age": 30,
                "rating": 4.7,
                "price_per_hour": 48,
                "contact_number": "+1 (555) 567-8901",
                "address": "321 Beauty Boulevard, Westend",
                "service_code": "WS004",
                "description": "Passionate about organic hair care and sustainable beauty practices. Certified in keratin treatments, extensions, and color correction. Let's create your dream look together!",
            },
            {
                "name": "Michelle Rodriguez",
                "age": 26,
                "rating": 4.9,
                "price_per_hour": 44,
                "contact_number": "+1 (555) 678-9012",
                "address": "654 Style Street, Northside",
                "service_code": "WS005",
                "description": "Young and creative stylist specializing in bold colors, creative cuts, and Instagram-worthy looks. Trained in LA and NYC, bringing the latest trends to your doorstep!",
            }
        ],
        
        "Men's Salon & Massage": [
            {
                "name": "Marcus Thompson",
                "age": 38,
                "rating": 4.9,
                "price_per_hour": 35,
                "contact_number": "+1 (555) 789-0123",
                "address": "111 Barbershop Row, Downtown",
                "service_code": "MS001",
                "description": "Master barber with 18 years of experience. Specializing in classic cuts, modern fades, and precision beard sculpting. Your grooming is my craft.",
            },
            {
                "name": "David Kim",
                "age": 29,
                "rating": 5.0,
                "price_per_hour": 38,
                "contact_number": "+1 (555) 890-1234",
                "address": "222 Groom Street, Fashion District",
                "service_code": "MS002",
                "description": "Professional barber trained in Seoul and New York. Expert in Asian hair textures, contemporary styling, and traditional hot towel shaves. Precision is my promise.",
            },
            {
                "name": "Anthony Rivers",
                "age": 42,
                "rating": 4.8,
                "price_per_hour": 32,
                "contact_number": "+1 (555) 901-2345",
                "address": "333 Classic Avenue, Old Town",
                "service_code": "MS003",
                "description": "Traditional barbering meets modern style. 20+ years perfecting the art of straight razor shaves, gentleman's cuts, and beard maintenance. Old school quality, new school vibes.",
            },
            {
                "name": "Ryan O'Connor",
                "age": 31,
                "rating": 4.7,
                "price_per_hour": 36,
                "contact_number": "+1 (555) 012-3456",
                "address": "444 Fade Lane, Uptown",
                "service_code": "MS004",
                "description": "Fade specialist and hair tattoo artist. From business professional to street fresh, I create looks that match your lifestyle. Walk-ins welcome!",
            },
            {
                "name": "Carlos Mendez",
                "age": 34,
                "rating": 4.9,
                "price_per_hour": 40,
                "contact_number": "+1 (555) 123-4567",
                "address": "555 Barber Boulevard, Southside",
                "service_code": "MS005",
                "description": "Award-winning barber passionate about men's grooming. Expert in textured cuts, hair systems, and scalp treatments. Your look, perfected.",
            }
        ],
        
        "Cleaning Services": [
            {
                "name": "Maria Santos",
                "age": 45,
                "rating": 5.0,
                "price_per_hour": 30,
                "contact_number": "+1 (555) 234-5670",
                "address": "777 Clean Street, Central City",
                "service_code": "CL001",
                "description": "Professional cleaner with 20 years experience. Specializing in deep cleaning, eco-friendly products, and attention to every detail. Your home deserves the best!",
            },
            {
                "name": "Linda Johnson",
                "age": 38,
                "rating": 4.8,
                "price_per_hour": 28,
                "contact_number": "+1 (555) 345-6701",
                "address": "888 Sparkle Avenue, Riverside",
                "service_code": "CL002",
                "description": "Certified in green cleaning and allergen-free techniques. From regular maintenance to move-out cleaning, I make spaces shine. Reliable, thorough, and trustworthy.",
            },
            {
                "name": "Patricia Brown",
                "age": 41,
                "rating": 4.9,
                "price_per_hour": 32,
                "contact_number": "+1 (555) 456-7012",
                "address": "999 Tidy Lane, Lakeside",
                "service_code": "CL003",
                "description": "Detail-oriented cleaning professional specializing in post-construction cleanup and organizing services. I don't just clean, I transform spaces!",
            },
            {
                "name": "Rosa Hernandez",
                "age": 36,
                "rating": 4.7,
                "price_per_hour": 29,
                "contact_number": "+1 (555) 567-8123",
                "address": "101 Fresh Court, Hillside",
                "service_code": "CL004",
                "description": "Experienced in residential and commercial cleaning with focus on kitchens and bathrooms. Flexible scheduling, consistent quality, and eco-conscious products.",
            },
            {
                "name": "Jennifer Lee",
                "age": 33,
                "rating": 4.8,
                "price_per_hour": 31,
                "contact_number": "+1 (555) 678-9234",
                "address": "202 Pristine Place, Valley View",
                "service_code": "CL005",
                "description": "Modern cleaning solutions with traditional care. Expert in carpet cleaning, window washing, and seasonal deep cleans. Your satisfaction is guaranteed!",
            }
        ],
        
        "Electrician, Plumber & Carpenter": [
            {
                "name": "Robert Miller",
                "age": 47,
                "rating": 4.9,
                "price_per_hour": 55,
                "contact_number": "+1 (555) 789-0345",
                "address": "303 Circuit Drive, Industrial Park",
                "service_code": "EL001",
                "description": "Licensed master electrician with 25 years experience. Residential and commercial wiring, panel upgrades, and emergency repairs. Safety first, quality always.",
            },
            {
                "name": "James Anderson",
                "age": 39,
                "rating": 4.8,
                "price_per_hour": 52,
                "contact_number": "+1 (555) 890-1456",
                "address": "404 Voltage Street, Tech District",
                "service_code": "EL002",
                "description": "Certified electrician specializing in smart home installations, LED lighting, and energy-efficient solutions. Modern problems need modern solutions!",
            },
            {
                "name": "Michael Davis",
                "age": 44,
                "rating": 5.0,
                "price_per_hour": 58,
                "contact_number": "+1 (555) 901-2567",
                "address": "505 Power Lane, Business District",
                "service_code": "EL003",
                "description": "Expert in troubleshooting electrical issues, outdoor lighting, and generator installations. 20 years of reliable service, available for emergencies 24/7.",
            },
            {
                "name": "Daniel Wilson",
                "age": 35,
                "rating": 4.7,
                "price_per_hour": 50,
                "contact_number": "+1 (555) 012-3678",
                "address": "606 Amp Avenue, Suburban Area",
                "service_code": "EL004",
                "description": "Young and tech-savvy electrician focused on modern electrical systems, EV charger installations, and home automation. Licensed, insured, and ready to help!",
            },
            {
                "name": "Christopher Moore",
                "age": 51,
                "rating": 4.9,
                "price_per_hour": 56,
                "contact_number": "+1 (555) 123-4789",
                "address": "707 Electric Boulevard, Northgate",
                "service_code": "EL005",
                "description": "Veteran electrician with expertise in rewiring old homes, code compliance, and safety inspections. Your family's safety is my top priority.",
            }
        ],
        
        "Native Water Purifier": [
            {
                "name": "Thomas Jackson",
                "age": 43,
                "rating": 4.8,
                "price_per_hour": 48,
                "contact_number": "+1 (555) 234-5890",
                "address": "808 Pipeline Road, Waterfront",
                "service_code": "WP001",
                "description": "Master plumber with 22 years experience in leak detection, pipe repairs, and water heater installations. Fast response, fair prices, quality work.",
            },
            {
                "name": "Kevin Martinez",
                "age": 37,
                "rating": 4.9,
                "price_per_hour": 45,
                "contact_number": "+1 (555) 345-6901",
                "address": "909 Drain Street, Harbor District",
                "service_code": "WP002",
                "description": "Licensed plumber specializing in drain cleaning, fixture installations, and emergency plumbing. Available weekends and holidays. No job too big or small!",
            },
            {
                "name": "Brian Taylor",
                "age": 40,
                "rating": 5.0,
                "price_per_hour": 50,
                "contact_number": "+1 (555) 456-7902",
                "address": "1010 Flow Avenue, Eastgate",
                "service_code": "WP003",
                "description": "Expert plumber focused on bathroom and kitchen remodels, sump pump installations, and water filtration systems. Clean work, honest pricing.",
            },
            {
                "name": "Steven White",
                "age": 46,
                "rating": 4.7,
                "price_per_hour": 47,
                "contact_number": "+1 (555) 567-8013",
                "address": "1111 Plumbing Place, Westgate",
                "service_code": "WP004",
                "description": "Experienced in residential and commercial plumbing with specialty in gas line work and backflow prevention. Certified and insured for your peace of mind.",
            },
            {
                "name": "Patrick Harris",
                "age": 34,
                "rating": 4.8,
                "price_per_hour": 46,
                "contact_number": "+1 (555) 678-9124",
                "address": "1212 Valve Street, Southgate",
                "service_code": "WP005",
                "description": "Modern plumber with expertise in tankless water heaters, smart leak detectors, and eco-friendly plumbing solutions. Technology meets traditional craftsmanship!",
            }
        ],
        
        "Home Painting": [
            {
                "name": "William Clark",
                "age": 41,
                "rating": 4.9,
                "price_per_hour": 40,
                "contact_number": "+1 (555) 789-0235",
                "address": "1313 Color Lane, Arts District",
                "service_code": "PT001",
                "description": "Professional painter with 18 years experience in interior and exterior painting. Meticulous prep work, clean lines, and beautiful finishes guaranteed.",
            },
            {
                "name": "Richard Lewis",
                "age": 38,
                "rating": 4.8,
                "price_per_hour": 38,
                "contact_number": "+1 (555) 890-1346",
                "address": "1414 Brush Street, Creative Quarter",
                "service_code": "PT002",
                "description": "Detail-oriented painter specializing in cabinet refinishing, deck staining, and decorative finishes. Your vision, my expertise, perfect results!",
            },
            {
                "name": "Joseph Walker",
                "age": 45,
                "rating": 5.0,
                "price_per_hour": 42,
                "contact_number": "+1 (555) 901-2457",
                "address": "1515 Canvas Avenue, Painter's Row",
                "service_code": "PT003",
                "description": "Master painter focused on high-end residential work. Expert in color consultation, texture application, and wallpaper removal. Transforming spaces since 2005!",
            },
            {
                "name": "Charles Robinson",
                "age": 36,
                "rating": 4.7,
                "price_per_hour": 37,
                "contact_number": "+1 (555) 012-3568",
                "address": "1616 Palette Place, Midtown",
                "service_code": "PT004",
                "description": "Reliable painter offering interior, exterior, and commercial painting services. Free estimates, competitive rates, and satisfaction guaranteed!",
            },
            {
                "name": "Andrew Young",
                "age": 33,
                "rating": 4.8,
                "price_per_hour": 39,
                "contact_number": "+1 (555) 123-4679",
                "address": "1717 Stroke Street, Design District",
                "service_code": "PT005",
                "description": "Creative painter with background in fine arts. Specializing in accent walls, murals, and unique finishes. Let's add personality to your space!",
            }
        ],
        
        "AC & Appliance Repair": [
            {
                "name": "George King",
                "age": 49,
                "rating": 4.9,
                "price_per_hour": 60,
                "contact_number": "+1 (555) 234-5781",
                "address": "1818 Cool Drive, Climate Control Center",
                "service_code": "AC001",
                "description": "HVAC master technician with 26 years experience. Expert in all AC brands, duct work, and energy efficiency upgrades. EPA certified and fully insured.",
            },
            {
                "name": "Kenneth Scott",
                "age": 42,
                "rating": 4.8,
                "price_per_hour": 55,
                "contact_number": "+1 (555) 345-6792",
                "address": "1919 Breeze Avenue, HVAC Plaza",
                "service_code": "AC002",
                "description": "Certified AC technician specializing in installation, repair, and preventive maintenance. Same-day service available. Keep cool with professional care!",
            },
            {
                "name": "Raymond Green",
                "age": 39,
                "rating": 5.0,
                "price_per_hour": 58,
                "contact_number": "+1 (555) 456-7803",
                "address": "2020 Chill Street, Comfort Zone",
                "service_code": "AC003",
                "description": "AC specialist with focus on smart thermostats, zoning systems, and heat pump technology. Modern solutions for maximum comfort and savings!",
            },
            {
                "name": "Larry Adams",
                "age": 44,
                "rating": 4.7,
                "price_per_hour": 54,
                "contact_number": "+1 (555) 567-8914",
                "address": "2121 Frost Lane, Temperature District",
                "service_code": "AC004",
                "description": "Experienced HVAC tech offering 24/7 emergency service. Expert in refrigerant recovery, compressor replacement, and air quality systems.",
            },
            {
                "name": "Donald Baker",
                "age": 37,
                "rating": 4.8,
                "price_per_hour": 56,
                "contact_number": "+1 (555) 678-9025",
                "address": "2222 Arctic Boulevard, Cooling Center",
                "service_code": "AC005",
                "description": "Professional AC technician with specialty in commercial systems and large residential units. Honest diagnostics, transparent pricing, excellent service!",
            }
        ],
        
        "InstaHelp (Help in 15 mins)": [
            {
                "name": "Alex Turner",
                "age": 29,
                "rating": 4.9,
                "price_per_hour": 25,
                "contact_number": "+1 (555) 789-0136",
                "address": "2323 Quick Street, Help Center",
                "service_code": "IH001",
                "description": "Jack-of-all-trades ready for any task! From furniture assembly to tech setup, grocery runs to pet sitting. Fast, friendly, and reliable service!",
            },
            {
                "name": "Jordan Parker",
                "age": 26,
                "rating": 4.8,
                "price_per_hour": 22,
                "contact_number": "+1 (555) 890-1247",
                "address": "2424 Support Avenue, Service Hub",
                "service_code": "IH002",
                "description": "Your go-to helper for small jobs and errands. Moving boxes, yard work, organizing, shopping - I do it all with a smile. Available same day!",
            },
            {
                "name": "Taylor Brooks",
                "age": 31,
                "rating": 5.0,
                "price_per_hour": 28,
                "contact_number": "+1 (555) 901-2358",
                "address": "2525 Assist Lane, Helper's Corner",
                "service_code": "IH003",
                "description": "Experienced handyworker offering quick solutions for everyday needs. Handy with tools, tech-savvy, and always punctual. No job too small!",
            },
            {
                "name": "Morgan Hayes",
                "age": 24,
                "rating": 4.7,
                "price_per_hour": 20,
                "contact_number": "+1 (555) 012-3469",
                "address": "2626 Aid Street, Quick Response",
                "service_code": "IH004",
                "description": "Young, energetic, and ready to help with anything! Event setup, moving assistance, delivery pickup, or odd jobs. Flexible hours, great attitude!",
            },
            {
                "name": "Casey Reed",
                "age": 28,
                "rating": 4.8,
                "price_per_hour": 24,
                "contact_number": "+1 (555) 123-4570",
                "address": "2727 Helper Boulevard, Task Force",
                "service_code": "IH005",
                "description": "Multi-skilled helper specializing in home organization, minor repairs, and personal assistance. Background checked, insured, and ready when you need me!",
            }
        ]
    }
    
    # Populate providers
    for category_name, providers in PROVIDER_DATA.items():
        try:
            category = ServiceCategory.objects.get(name=category_name)
        except ServiceCategory.DoesNotExist:
            print(f"Warning: Category '{category_name}' not found. Skipping providers for this category.")
            continue
        
        for provider_data in providers:
            # Split name into first and last
            name_parts = provider_data['name'].split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # Create or get user
            username = provider_data['service_code'].lower()
            password = make_password('temporary_password_123')
            
            # Use get_or_create to avoid duplicates
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f"{username}@coole.service",
                    'password': password
                }
            )
            
            # Create provider profile
            ServiceProvider.objects.get_or_create(
                user=user,
                defaults={
                    'category': category,
                    'age': provider_data['age'],
                    'rating': provider_data['rating'],
                    'price_per_hour': provider_data['price_per_hour'],
                    'contact_number': provider_data['contact_number'],
                    'address': provider_data['address'],
                    'service_code': provider_data['service_code'],
                    'description': provider_data['description'],
                    'profile_pic': None 
                }
            )

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_serviceprovider_age'),
    ]

    operations = [
        migrations.RunPython(populate_providers),
    ]
