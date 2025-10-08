from django.db import migrations
from django.core.management import call_command
from django.db import connection
import os
import glob
import pkg_resources

def load_package_data(apps, schema_editor):
    """
    Load all package data in the correct order for Arches 8.1
    This replicates what the Arches package installer does
    """
    
    package_name = 'arches_her'  # Use the Python module name, not the package distribution name
    
    try:
        # Step 1: Load ontologies
        print("=" * 80)
        print("Loading ontologies...")
        print("=" * 80)
        try:
            ontologies_path = pkg_resources.resource_filename(package_name, 'data/ontologies')
            if os.path.exists(ontologies_path):
                # Load CIDOC CRM ontology
                cidoc_path = os.path.join(ontologies_path, 'cidoc_crm')
                if os.path.exists(cidoc_path):
                    ontology_config = os.path.join(cidoc_path, 'ontology_config.json')
                    if os.path.exists(ontology_config):
                        try:
                            call_command('load_ontology', '-s', cidoc_path)
                            print(f"Successfully loaded CIDOC CRM ontology from {cidoc_path}")
                        except Exception as e:
                            print(f"Error loading CIDOC CRM ontology: {e}")
                
                # Load Linked Art ontology if present
                linkedart_path = os.path.join(ontologies_path, 'linkedart')
                if os.path.exists(linkedart_path):
                    ontology_config = os.path.join(linkedart_path, 'ontology_config.json')
                    if os.path.exists(ontology_config):
                        try:
                            call_command('load_ontology', '-s', linkedart_path)
                            print(f"Successfully loaded Linked Art ontology from {linkedart_path}")
                        except Exception as e:
                            print(f"Error loading Linked Art ontology: {e}")
        except Exception as e:
            print(f"Error loading ontologies: {e}")
        
        # Step 2: Load extensions (datatypes)
        print("\n" + "=" * 80)
        print("Loading extensions (datatypes)...")
        print("=" * 80)
        try:
            extensions_path = pkg_resources.resource_filename(package_name, 'data/extensions')
            if os.path.exists(extensions_path):
                # Register datatypes by importing the modules
                datatypes_path = os.path.join(extensions_path, 'datatypes')
                if os.path.exists(datatypes_path):
                    for filename in os.listdir(datatypes_path):
                        if filename.endswith('.py') and filename != '__init__.py':
                            print(f"Found datatype module: {filename}")
                    # Note: Datatypes are typically auto-registered when the app is loaded
                    print("Datatypes will be registered when the application starts")
        except Exception as e:
            print(f"Error loading extensions: {e}")
        
        # Step 3: Load widgets
        print("\n" + "=" * 80)
        print("Loading widgets...")
        print("=" * 80)
        try:
            widgets_path = pkg_resources.resource_filename(package_name, 'data/widgets')
            if os.path.exists(widgets_path):
                for filename in sorted(os.listdir(widgets_path)):
                    if filename.endswith('.json'):
                        widget_file = os.path.join(widgets_path, filename)
                        try:
                            call_command('widget', 'register', '-s', widget_file)
                            print(f"Successfully registered widget: {filename}")
                        except Exception as e:
                            print(f"Error registering widget {filename}: {e}")
        except Exception as e:
            print(f"Error loading widgets: {e}")
        
        # Step 4: Load resource models (graphs)
        print("\n" + "=" * 80)
        print("Loading resource models (graphs)...")
        print("=" * 80)
        try:
            graphs_path = pkg_resources.resource_filename(package_name, 'data/graphs/resource_models')
            if os.path.exists(graphs_path):
                for filename in sorted(os.listdir(graphs_path)):
                    if filename.endswith('.json'):
                        graph_file = os.path.join(graphs_path, filename)
                        try:
                            call_command('packages', '-o', 'import_graphs', '-s', graph_file)
                            print(f"Successfully imported graph: {filename}")
                        except Exception as e:
                            print(f"Error importing graph {filename}: {e}")
        except Exception as e:
            print(f"Error loading graphs: {e}")
        
        # Step 5: Run preliminary SQL (after graphs are imported)
        print("\n" + "=" * 80)
        print("Running preliminary SQL (after graphs)...")
        print("=" * 80)
        try:
            preliminary_sql_path = pkg_resources.resource_filename(package_name, 'data/preliminary_sql')
            if os.path.exists(preliminary_sql_path):
                sql_files = sorted(glob.glob(os.path.join(preliminary_sql_path, '*.sql')))
                for sql_file in sql_files:
                    try:
                        with open(sql_file, 'r') as f:
                            sql = f.read()
                            with connection.cursor() as cursor:
                                cursor.execute(sql)
                        print(f"Successfully executed preliminary SQL: {os.path.basename(sql_file)}")
                    except Exception as e:
                        print(f"Error executing {os.path.basename(sql_file)}: {e}")
                        # Don't raise - continue with next SQL file
            else:
                print("No preliminary SQL directory found")
        except Exception as e:
            print(f"Error running preliminary SQL: {e}")
        
        # Step 6: Load reference data - concepts
        print("\n" + "=" * 80)
        print("Loading reference data (concepts)...")
        print("=" * 80)
        try:
            concepts_path = pkg_resources.resource_filename(package_name, 'data/reference_data/concepts')
            if os.path.exists(concepts_path):
                concept_files = sorted(glob.glob(os.path.join(concepts_path, '*.xml')))
                for concept_file in concept_files:
                    if os.path.basename(concept_file) != '.gitkeep':
                        try:
                            call_command('packages', '-o', 'import_reference_data', '-s', concept_file)
                            print(f"Successfully imported concepts: {os.path.basename(concept_file)}")
                        except Exception as e:
                            print(f"Error importing {os.path.basename(concept_file)}: {e}")
        except Exception as e:
            print(f"Error loading concepts: {e}")
        
        # Step 7: Load reference data - collections
        print("\n" + "=" * 80)
        print("Loading reference data (collections)...")
        print("=" * 80)
        try:
            collections_path = pkg_resources.resource_filename(package_name, 'data/reference_data/collections')
            if os.path.exists(collections_path):
                collection_files = sorted(glob.glob(os.path.join(collections_path, '*.xml')))
                for collection_file in collection_files:
                    if os.path.basename(collection_file) != '.gitkeep':
                        try:
                            call_command('packages', '-o', 'import_reference_data', '-s', collection_file)
                            print(f"Successfully imported collections: {os.path.basename(collection_file)}")
                        except Exception as e:
                            print(f"Error importing {os.path.basename(collection_file)}: {e}")
        except Exception as e:
            print(f"Error loading collections: {e}")
        
        # Step 8: Run post SQL (after graphs and reference data)
        print("\n" + "=" * 80)
        print("Running post SQL...")
        print("=" * 80)
        try:
            post_sql_path = pkg_resources.resource_filename(package_name, 'data/post_sql')
            if os.path.exists(post_sql_path):
                sql_files = sorted(glob.glob(os.path.join(post_sql_path, '*.sql')))
                for sql_file in sql_files:
                    try:
                        with open(sql_file, 'r') as f:
                            sql = f.read()
                            with connection.cursor() as cursor:
                                cursor.execute(sql)
                        print(f"Successfully executed post SQL: {os.path.basename(sql_file)}")
                    except Exception as e:
                        print(f"Error executing {os.path.basename(sql_file)}: {e}")
        except Exception as e:
            print(f"Error running post SQL: {e}")
        
        
            
    except Exception as e:
        print(f"Error loading package resources: {e}")
        raise

class Migration(migrations.Migration):

    initial = True
    
    dependencies = [
        # Both required for importing graphs - can install in any order
        ('models', '12394_resource_identifier'),
        ('guardian', '0002_generic_permissions_index'),
    ]

    operations = [
        migrations.RunPython(load_package_data),
    ]