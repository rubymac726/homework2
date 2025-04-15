import os
import sys
from django.apps import apps

def setup_django(project_name):
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project_name}.settings')
    sys.path.append(os.getcwd())
    import django
    django.setup()

def main():
    project_name = input("Enter your Django project name: ").strip()
    if not project_name:
        print("Project name is required!")
        sys.exit(1)
        
    setup_django(project_name)
    
    print("\nDatabase Cleanup Options:")
    print("1. Clean entire project")
    print("2. Clean specific app")
    print("3. Clean specific model")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        for app_config in apps.get_app_configs():
            if not app_config.name.startswith('django.'):
                clean_app(app_config)
    elif choice == '2':
        app_list = [
            app.label for app in apps.get_app_configs() 
            if not app.name.startswith('django.')
        ]
        print("\nAvailable Apps:")
        for i, app in enumerate(app_list, 1):
            print(f"{i}. {app}")
        
        try:
            choice = int(input("\nSelect app number: ")) - 1
            clean_app(apps.get_app_config(app_list[choice]))
        except (ValueError, IndexError):
            print("Invalid selection")

    elif choice == '3':
        app_list = [
            app.label for app in apps.get_app_configs() 
            if not app.name.startswith('django.')
        ]
        print("\nAvailable Apps:")
        for i, app in enumerate(app_list, 1):
            print(f"{i}. {app}")
        
        try:
            app_choice = int(input("\nSelect app number: ")) - 1
            selected_app = app_list[app_choice]
            app_config = apps.get_app_config(selected_app)
            
            # Convert generator to list to fix subscript error
            models = list(app_config.get_models())
            model_list = [model.__name__ for model in models]
            print("\nAvailable Models:")
            for i, model in enumerate(model_list, 1):
                print(f"{i}. {model}")
                
            model_choice = int(input("\nSelect model number: ")) - 1
            selected_model = models[model_choice]
            
            count = selected_model.objects.count()
            if count == 0:
                print(f"No records found in {selected_model.__name__}")
            else:
                print(f"Found {count} records in {selected_model.__name__}")
                if input("Delete these records? (y/n): ").lower() == 'y':
                    selected_model.objects.all().delete()
                    print(f"Deleted {count} records")
                    
        except (ValueError, IndexError):
            print("Invalid selection")

def clean_app(app_config):
    for model in app_config.get_models():
        count = model.objects.count()
        if count == 0:
            continue
            
        print(f"Found {count} records in {model.__name__}")
        if input(f"Delete these records? (y/n): ").lower() == 'y':
            model.objects.all().delete()
            print(f"Deleted {count} records")

if __name__ == "__main__":
    main()