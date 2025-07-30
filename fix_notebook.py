import json

# Read the notebook
with open('notebooks/02_complete_pipeline_demo.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Find and fix the dbt directory path
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        if 'dbt_dir = project_root / "pharma_dbt"' in source:
            # Replace the problematic line
            new_source = source.replace(
                'dbt_dir = project_root / "pharma_dbt"',
                'dbt_dir = Path.cwd().parent / "pharma_dbt"'
            )
            new_source = new_source.replace(
                'os.chdir(dbt_dir)',
                '''print(f"📁 dbt directory: {dbt_dir}")
if dbt_dir.exists():
    os.chdir(dbt_dir)
    print(f"✅ Changed to dbt directory: {os.getcwd()}")
else:
    print(f"❌ dbt directory not found: {dbt_dir}")
    raise FileNotFoundError(f"dbt directory not found: {dbt_dir}")'''
            )
            cell['source'] = new_source
            print("✅ Fixed dbt directory path in notebook")

# Write the fixed notebook
with open('notebooks/02_complete_pipeline_demo_fixed.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("✅ Fixed notebook created: notebooks/02_complete_pipeline_demo_fixed.ipynb") 