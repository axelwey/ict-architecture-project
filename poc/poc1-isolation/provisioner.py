import os

os.system("""
docker run -it --rm \
--name sandbox-temp \
--cpus="0.5" \
--memory="256m" \
poc-sandbox bash
""")
