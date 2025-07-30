import json
import re

def fix_notebook_queries():
    """Fix SQL queries in the notebook that reference non-existent columns"""
    
    # Read the notebook
    with open('notebooks/02_complete_pipeline_demo.ipynb', 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Fix the problematic queries
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            
            # Fix channel_name query in fct_messages
            old_query = '''SELECT 
                channel_name,
                COUNT(*) as message_count,
                COUNT(CASE WHEN has_image THEN 1 END) as image_count
            FROM analytics.fct_messages
            GROUP BY channel_name
            ORDER BY message_count DESC'''
            
            new_query = '''SELECT 
                c.channel_name,
                COUNT(*) as message_count,
                COUNT(CASE WHEN fm.has_image THEN 1 END) as image_count
            FROM analytics.fct_messages fm
            JOIN analytics.dim_channels c ON fm.channel_id = c.channel_id
            GROUP BY c.channel_name
            ORDER BY message_count DESC'''
            
            if old_query in source:
                print("🔧 Fixing channel_name query...")
                cell['source'] = [source.replace(old_query, new_query)]
            
            # Fix object_class query in fct_image_detections
            old_query2 = '''SELECT 
                object_class,
                COUNT(*) as detection_count,
                AVG(confidence_score) as avg_confidence
            FROM analytics.fct_image_detections
            WHERE object_class IN ('bottle', 'person', 'truck', 'refrigerator')
            GROUP BY object_class
            ORDER BY detection_count DESC'''
            
            new_query2 = '''SELECT 
                detected_object_class as object_class,
                COUNT(*) as detection_count,
                AVG(confidence_score) as avg_confidence
            FROM analytics.fct_image_detections
            WHERE detected_object_class IN ('bottle', 'person', 'truck', 'refrigerator')
            GROUP BY detected_object_class
            ORDER BY detection_count DESC'''
            
            if old_query2 in source:
                print("🔧 Fixing object_class query...")
                cell['source'] = [source.replace(old_query2, new_query2)]
    
    # Write the fixed notebook
    with open('notebooks/02_complete_pipeline_demo_fixed.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print("✅ Notebook queries fixed!")

if __name__ == "__main__":
    fix_notebook_queries() 