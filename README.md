# My App

### Description
This app contains the base HER package for arches.

### Installation

Arches Example... (thanks to Cyrus for the base text from the Dashboard example).

You can add the arches example into your project in a few easy steps

1. Install if from this repo (or clone this repo and pip install it locally). 
```
pip install git+https://github.com/flaxandteal/arches-her-app.git
```

2. Add `"arches-her"` to the INSTALLED_APPS setting in the demo project's settings.py file below the demo project:
```
INSTALLED_APPS = [
    ...
    "demo",
    "arches-her",
]
```

3. Version your dependency on `"arches-her"` in `pyproject.toml`:
```
dependencies = [
    "arches>=8.1.0a0",
    "arches-her",
]
```

4. From your project run the load package command for the app to add the model data:
```
python manage.py packages -o load_package -a arches-her
```

5. Next be sure to rebuild your project's frontend to include the plugin:
```
npm run build_development
```