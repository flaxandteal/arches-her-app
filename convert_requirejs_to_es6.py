#!/usr/bin/env python3
"""
Arches 8.1 Migration Script - RequireJS to ES6 Modules Converter
This script automatically converts JavaScript files from RequireJS format to ES6 modules
"""

import os
import re
import sys
from pathlib import Path

# Common import mappings
IMPORT_MAPPINGS = {
    'knockout': 'ko',
    'jquery': '$',
    'underscore': '_',
    'moment': 'moment',
    'arches': 'arches',
}

# Template path mapping
TEMPLATE_PATTERNS = [
    (r"'text!templates/views/(.+?)'", r"'templates/views/\1'"),
    (r'"text!templates/views/(.+?)"', r'"templates/views/\1"'),
    (r"'text!report-templates/(.+?)'", r"'templates/views/report-templates/\1'"),
    (r'"text!report-templates/(.+?)"', r'"templates/views/report-templates/\1"'),
    (r"'text!component-templates/(.+?)'", r"'templates/views/component-templates/\1'"),
    (r'"text!component-templates/(.+?)"', r'"templates/views/component-templates/\1"'),
]

def extract_define_info(content):
    """Extract dependency list and function parameters from define() call"""
    # Match define([...], function(...) { ... })
    define_pattern = r"define\(\s*\[(.*?)\]\s*,\s*function\((.*?)\)\s*\{(.*)\}\s*\);?\s*$"
    match = re.search(define_pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    deps_str = match.group(1)
    params_str = match.group(2)
    body = match.group(3)
    
    # Parse dependencies
    deps = []
    for dep in re.findall(r"['\"]([^'\"]+)['\"]", deps_str):
        deps.append(dep.strip())
    
    # Parse parameters
    params = [p.strip() for p in params_str.split(',') if p.strip()]
    
    return {
        'dependencies': deps,
        'parameters': params,
        'body': body
    }

def convert_to_import(dep, param):
    """Convert a dependency to an ES6 import statement"""
    # Handle text! template imports
    if dep.startswith('text!'):
        template_path = dep.replace('text!', '')
        # Apply template path transformations
        for pattern, replacement in TEMPLATE_PATTERNS:
            template_path = re.sub(pattern.replace("'", ""), replacement.replace("'", ""), template_path)
        
        # Ensure .htm extension
        if not template_path.endswith('.htm'):
            template_path += '.htm'
        
        # Generate a variable name from the path
        var_name = param if param else Path(template_path).stem.replace('-', '_') + 'Template'
        return f"import {var_name} from '{template_path}';"
    
    # Side-effect imports (no parameter)
    if not param:
        return f"import '{dep}';"
    
    # Regular imports
    return f"import {param} from '{dep}';"

def fix_arches_urls(body):
    """Replace arches.urls references with generateArchesURL calls"""
    # This is a simple replacement - may need manual review
    # Pattern: arches.urls.some_url -> generateArchesURL('arches:some_url')
    def replace_url(match):
        url_name = match.group(1)
        return f"generateArchesURL('arches:{url_name}')"
    
    # Simple property access
    body = re.sub(r"arches\.urls\.(\w+)", replace_url, body)
    
    return body

def convert_file(filepath):
    """Convert a single file from RequireJS to ES6"""
    print(f"Converting: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract define information
    define_info = extract_define_info(content)
    if not define_info:
        print(f"  ⚠️  Could not parse define() - skipping")
        return False
    
    # Generate imports
    imports = []
    template_var = None
    uses_generate_url = False
    uses_arches = False
    
    for dep, param in zip(define_info['dependencies'], define_info['parameters']):
        import_stmt = convert_to_import(dep, param)
        imports.append(import_stmt)
        
        # Track if we have a template import
        if dep.startswith('text!'):
            template_var = param if param else 'template'
        
        # Track if arches is used
        if dep == 'arches':
            uses_arches = True
    
    # Check if body uses arches.urls
    body = define_info['body']
    if 'arches.urls' in body:
        uses_generate_url = True
        body = fix_arches_urls(body)
    
    # Add generateArchesURL import if needed
    if uses_generate_url and not any('generate-arches-url' in imp for imp in imports):
        imports.insert(0, "import { generateArchesURL } from '@/arches/utils/generate-arches-url.ts';")
    
    # Find the LAST return statement at the module level (the module's export)
    # Use rfind to search backwards for the last 'return' statement
    body_stripped = body.rstrip()
    last_return_pos = body_stripped.rfind('\n    return ')
    
    if last_return_pos == -1:
        # Try without indentation
        last_return_pos = body_stripped.rfind('\nreturn ')
    
    if last_return_pos != -1:
        # Extract everything after 'return ' up to the semicolon or end
        return_section = body_stripped[last_return_pos:]
        return_match = re.search(r'return\s+(.*?);?\s*$', return_section, re.DOTALL)
        if return_match:
            returned_value = return_match.group(1).strip()
            # Remove the return statement from body
            body = body[:last_return_pos]
        else:
            print("  ⚠️  Found return keyword but couldn't parse it")
            returned_value = None
    else:
        print("  ⚠️  No return statement found")
        returned_value = None
    
    # Handle template in component registration
    if template_var and returned_value:
        # Replace { require: 'text!...' } with template variable
        returned_value = re.sub(
            r"template:\s*\{\s*require:\s*['\"]text![^'\"]+['\"]\s*\}",
            f"template: {template_var}",
            returned_value
        )
    
    # Build new file content
    new_content = '\n'.join(imports) + '\n\n'
    new_content += body.strip() + '\n\n'
    if returned_value:
        new_content += f'export default {returned_value};'
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✓ Converted successfully")
    return True

def find_js_files(directory):
    """Find all JavaScript files in directory"""
    js_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.js'):
                js_files.append(os.path.join(root, file))
    return js_files

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_requirejs_to_es6.py <directory>")
        print("Example: python convert_requirejs_to_es6.py arches_her/media/js")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)
    
    js_files = find_js_files(directory)
    print(f"Found {len(js_files)} JavaScript files")
    print()
    
    converted = 0
    skipped = 0
    
    for filepath in js_files:
        try:
            if convert_file(filepath):
                converted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            skipped += 1
        print()
    
    print("=" * 60)
    print(f"Conversion complete!")
    print(f"  Converted: {converted}")
    print(f"  Skipped: {skipped}")
    print()
    print("⚠️  IMPORTANT: Please manually review all converted files!")
    print("   - Check template imports have correct paths")
    print("   - Verify generateArchesURL() calls are correct")
    print("   - Test all components thoroughly")

if __name__ == '__main__':
    main()
