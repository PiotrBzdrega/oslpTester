import yaml
import os

def read():
    with open('ScriptTest/RebootAndWaitForRegister/recipe.yaml', 'r') as file:
        content = yaml.safe_load(file)
    print(content)
    
    yaml.