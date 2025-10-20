#!/usr/bin/env python3
"""
Create Excel template for sources import.
"""

import pandas as pd

# Sample data for template
data = {
    'our_channel_username': ['@mynewschannel', '@mynewschannel', '@mycommercechannel'],
    'source_name': ['Tech News', 'Business News', 'Tech Store'],
    'source_username': ['technews', 'businessnews', 'techstore'],
    'description': ['Technology news and updates', 'Business and financial news', 'Technology products and deals'],
    'default_image_url': ['https://example.com/tech.jpg', 'https://example.com/business.jpg', 'https://example.com/store.jpg'],
    'source_type': ['news', 'news', 'commerce'],
    'enabled': [True, True, True]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('tools/sources_template.xlsx', index=False)
print("Created sources_template.xlsx")
