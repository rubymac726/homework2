import os
import sys
import csv
from django.apps import apps
from django.db import models
from django.db.models.fields import DateField, IntegerField, BooleanField
from importlib import import_module
from django.core.exceptions import ValidationError

class DataManager:
    def __init__(self):
        self.project_name = None
        self.app_name = None
        self.Model = None
    
    def setup_django(self, project_name):
        """Setup Django environment"""
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project_name}.settings')
        sys.path.append(os.getcwd())
        import django
        django.setup()
    
    def get_app_choice(self):
        """Show available apps and let user choose"""
        app_list = [
            app.label for app in apps.get_app_configs()
            if not app.name.startswith('django.')
        ]
        
        print("\nAvailable Apps:")
        for i, app in enumerate(app_list, 1):
            print(f"{i}. {app}")
            
        while True:
            choice = input("\nSelect app number: ").strip()
            if not choice:
                continue
                
            try:
                idx = int(choice) - 1
                return app_list[idx]
            except (ValueError, IndexError):
                print("Invalid selection, try again")

    def get_model_choice(self, app_name):
        """Show available models in selected app and let user choose"""
        app_config = apps.get_app_config(app_name)
        model_list = list(app_config.get_models())
        
        print(f"\nAvailable Models in {app_name}:")
        for i, model in enumerate(model_list, 1):
            print(f"{i}. {model.__name__}")
            
        while True:
            choice = input("\nSelect model number: ").strip()
            if not choice:
                continue
                
            try:
                idx = int(choice) - 1
                return model_list[idx]
            except (ValueError, IndexError):
                print("Invalid selection, try again")

    def display_main_menu(self):
        print("\n" + "="*50)
        print("DATA MANAGER".center(50))
        print("="*50)
        print("1. Import Data")
        print("2. Export Data")
        print("3. Exit")
        print("="*50)
        return input("Select option (1-3): ").strip()
    
    def get_input_path(self, prompt, default=None, file_type='file'):
        while True:
            path = input(prompt).strip()
            if not path and default:
                path = default
            
            path = os.path.abspath(path)
            
            if file_type == 'file' and not os.path.exists(path):
                print(f"Error: File not found at {path}")
                continue
            return path
    
    def handle_relationships(self, Model):
        """Detect and prepare relationship fields"""
        fk_fields = {}
        for field in Model._meta.fields:
            if field.is_relation and not field.auto_created:
                fk_fields[field.name] = {
                    'model': field.remote_field.model,
                    'lookup_field': field.target_field.name
                }
        return fk_fields
    
    def convert_field_value(self, field, value):
        """Convert input values to proper field types"""
        if isinstance(field, (DateField)):
            # Add date parsing logic here if needed
            return value
        elif isinstance(field, (IntegerField, BooleanField)):
            return field.to_python(value)
        return value
    
    def import_data(self):
        file_path = self.get_input_path("\nEnter CSV file path (relative or absolute): ")
        
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                model_fields = [f.name for f in self.Model._meta.fields if not f.auto_created]
                fk_fields = self.handle_relationships(self.Model)
                
                # Validate CSV fields
                missing = set(model_fields) - set(reader.fieldnames)
                if missing:
                    print(f"Missing required fields: {', '.join(missing)}")
                    return
                    
                extra = set(reader.fieldnames) - set(model_fields)
                if extra:
                    print(f"Ignoring extra fields: {', '.join(extra)}")

                # Handle existing data
                action = 'merge'
                if self.Model.objects.exists():
                    action = input("\nExisting data. [R]eplace, [M]erge, or [C]ancel? ").lower()
                    if action == 'r':
                        self.Model.objects.all().delete()
                        print("Existing data deleted.")
                    elif action not in ('m', ''):
                        print("Import cancelled.")
                        return

                # Process records
                records = []
                for i, row in enumerate(reader, 2):  # Start from line 2 (1-based)
                    try:
                        instance_data = {}
                        for field in model_fields:
                            value = row[field]
                            
                            # Handle relationships
                            if field in fk_fields:
                                related_model = fk_fields[field]['model']
                                lookup_field = fk_fields[field]['lookup_field']
                                try:
                                    instance_data[field] = related_model.objects.get(**{lookup_field: value})
                                except related_model.DoesNotExist:
                                    print(f"Line {i}: Related {field} with {lookup_field} '{value}' not found")
                                    raise ValidationError
                                except Exception as e:
                                    print(f"Line {i}: Error with {field} '{value}' - {str(e)}")
                                    raise ValidationError
                            else:
                                # Convert data types
                                model_field = self.Model._meta.get_field(field)
                                instance_data[field] = self.convert_field_value(model_field, value)
                                
                        records.append(self.Model(**instance_data))
                    
                    except ValidationError:
                        continue
                        
                # Confirm and import
                if records and input(f"\nImport {len(records)} records? (y/n): ").lower() == 'y':
                    self.Model.objects.bulk_create(records)
                    print(f"Successfully imported {len(records)} records")
        
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def export_data(self):
        default_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"{self.Model.__name__.lower()}_export.csv"
        )
        
        file_path = self.get_input_path(
            f"\nEnter destination CSV path (or press Enter for default: {default_path}): ",
            default=default_path,
            file_type='new_file'  # Changed from 'file' to 'new_file'
        )
        
        if not self.Model.objects.exists():
            print("No data to export")
            return
        
        fields = [f.name for f in self.Model._meta.fields if not f.auto_created]
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                
                for obj in self.Model.objects.all():
                    row = {}
                    for field in fields:
                        field_value = getattr(obj, field)
                        if isinstance(field_value, models.Model):
                            related_field = self.Model._meta.get_field(field).target_field.name
                            row[field] = getattr(field_value, related_field)
                        else:
                            row[field] = str(field_value)
                    writer.writerow(row)
            
            print(f"Exported {self.Model.objects.count()} records to {file_path}")
        
        except Exception as e:
            print(f"Export Error: {str(e)}")

def main():
    dm = DataManager()
    
    # Get project name
    dm.project_name = input("Enter Django project name: ").strip()
    if not dm.project_name:
        print("Project name is required!")
        sys.exit(1)
    
    # Setup environment
    dm.setup_django(dm.project_name)
    
    # Get app choice
    dm.app_name = dm.get_app_choice()
    
    # Get model choice
    dm.Model = dm.get_model_choice(dm.app_name)
    
    # Main loop
    while True:
        choice = dm.display_main_menu()
        if choice == '1':
            dm.import_data()
        elif choice == '2':
            dm.export_data()
        elif choice == '3':
            sys.exit(0)
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()