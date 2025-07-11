#!/bin/bash
set -e

# Rename the package directory
if [ -d "container_os" ]; then
    mv container_os dockevos
    echo "✅ Renamed container_os/ to dockevos/"
fi

# Update setup.py
sed -i 's/packages=find_packages(include=\[\'container_os/\packages=find_packages(include=[\'dockevos/g' setup.py
sed -i 's/container_os.__main__/dockevos.__main__/g' setup.py
sed -i "s/'container_os': \['\*\/\*\']/'dockevos': ['*\/*']/g" setup.py

# Update run.sh
sed -i 's/import container_os/import dockevos/g' run.sh
sed -i 's/python3 -m container_os/python3 -m dockevos/g' run.sh

# Update __main__.py
sed -i 's/container_os = ContainerOSMVP()/dockevos = ContainerOSMVP()/g' dockevos/__main__.py
sed -i 's/asyncio.run(container_os.start())/asyncio.run(dockevos.start())/g' dockevos/__main__.py

# Update MANIFEST.in
sed -i 's/container_os/dockevos/g' MANIFEST.in

# Update any Python files in the package
find dockevos -type f -name "*.py" -exec sed -i 's/from container_os/from dockevos/g' {} \;
find dockevos -type f -name "*.py" -exec sed -i 's/import container_os/import dockevos/g' {} \;

echo "✅ Package renamed from container_os to dockevos"
echo "💡 You may want to run: make clean && pip uninstall -y dockevos && pip install -e ."
