# My App

### Description
This app contains the graph models for the Arches HER package.
This is not a full working app for HER, it is only for basic use to show graph structures.

### Installation

Arches HER Demo.

You can add the arches example into your project in a few easy steps

1. Install if from this repo (or clone this repo and pip install it locally). 
```
pip install git+https://github.com/flaxandteal/arches-her-app.git
```

2. Add `"arches_her"` to the INSTALLED_APPS setting in the demo project's settings.py file below the demo project:
```
INSTALLED_APPS = [
    ...
    "demo",
    "arches_her",
]
```

3. Version your dependency on `"arches_her"` in `pyproject.toml`:
```
dependencies = [
    "arches>=8.1.0a0",
    "arches_her @ git+https://github.com/flaxandteal/arches-her-app",
]
```

4. From your project run the load package command for the app to add the model data:
```
python manage.py packages -o load_package -a arches_her
```

5. Next be sure to rebuild your project's frontend to include the plugin:
```
npm run build_development
```