from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    """
    This function will return list of requirements from the requirements.txt file.
    """
    requirement_list: List[str] = []

    try:
        with open('requirements.txt', 'r') as file:
            lines=file.readlines()
            for line in lines:
                requirement = line.strip()
                if requirement and requirement != "-e ." and not requirement.startswith("#"):
                    requirement_list.append(requirement)

    except FileNotFoundError:
        print("requirements.txt file not found. ")

    
    return requirement_list
print(get_requirements())

setup(
    name='AI_Trip_Planner',
    version='0.1.0',
    author='Prabjot Singh',
    author_email='prabjotda@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements()
)