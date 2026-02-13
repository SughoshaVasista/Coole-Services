from django.db import migrations

def populate_categories(apps, schema_editor):
    ServiceCategory = apps.get_model('services', 'ServiceCategory')
    
    categories = [
    {
        "name": "InstaHelp (Help in 15 mins)",
        "description": "Quick emergency home repair services delivered within 15 minutes by trained professionals."
    },
    {
        "name": "Women's Salon & Spa",
        "description": "Professional at-home beauty and wellness services by certified beauticians."
    },
    {
        "name": "Men's Salon & Massage",
        "description": "Complete grooming and relaxation services for men at your doorstep."
    },
    {
        "name": "Cleaning Services",
        "description": "Deep cleaning and sanitation services for homes and offices using advanced equipment."
    },
    {
        "name": "Electrician, Plumber & Carpenter",
        "description": "Reliable home maintenance and repair services by skilled technicians."
    },
    {
        "name": "Native Water Purifier",
        "description": "Professional RO installation and water purifier maintenance services."
    },
    {
        "name": "Home Painting",
        "description": "High-quality interior and exterior painting services with expert finishing."
    },
    {
        "name": "AC & Appliance Repair",
        "description": "Expert repair and servicing for AC and household appliances."
    }
]


    for cat_data in categories:
        # Use get_or_create to avoid duplicates if migration is re-run (though for data migration usually create is fine if transient)
        ServiceCategory.objects.get_or_create(name=cat_data['name'], defaults={'description': cat_data['description']})

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_categories),
    ]
