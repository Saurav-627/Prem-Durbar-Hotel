import os
import shutil

apps_dir = "."
apps = [d for d in os.listdir(apps_dir) if os.path.isdir(os.path.join(apps_dir, d)) and not d.startswith('.') and d not in ('config', '.venv', 'backups', 'static', 'templates', 'scripts')]

print("Found apps:", apps)

for app in apps:
    app_path = os.path.join(apps_dir, app)
    
    # 1. Handle urls folder -> urls.py
    urls_dir = os.path.join(app_path, "urls")
    urls_init = os.path.join(urls_dir, "__init__.py")
    if os.path.isdir(urls_dir) and os.path.isfile(urls_init):
        print(f"Converting {app}/urls/ -> {app}/urls.py")
        with open(urls_init, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace relative imports going up two levels to go up one level instead
        content = content.replace("from ..views", "from .views")
        content = content.replace("from ..models", "from .models")
        content = content.replace("from ..forms", "from .forms")
        content = content.replace("from ..", "from .")
        
        target_file = os.path.join(app_path, "urls.py")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        os.remove(urls_init)
        # remove empty directories if any, or shutil.rmtree
        shutil.rmtree(urls_dir)

    # 2. Handle admin folder -> admin.py
    admin_dir = os.path.join(app_path, "admin")
    admin_init = os.path.join(admin_dir, "__init__.py")
    if os.path.isdir(admin_dir) and os.path.isfile(admin_init):
        print(f"Converting {app}/admin/ -> {app}/admin.py")
        with open(admin_init, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Replace relative imports
        content = content.replace("from ..views", "from .views")
        content = content.replace("from ..models", "from .models")
        content = content.replace("from ..forms", "from .forms")
        content = content.replace("from ..", "from .")
        
        target_file = os.path.join(app_path, "admin.py")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        os.remove(admin_init)
        shutil.rmtree(admin_dir)

print("Cleanup complete!")
