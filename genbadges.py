import subprocess
from genbadge import Badge
import pymerger

# Version
version = Badge(left_txt="Version",
                right_txt=pymerger.__version__, color="violet")
version.write_to("badges/version.svg", use_shields=False)

# License
license_ = Badge(left_txt="License",
                 right_txt="MIT", color="grey")
license_.write_to("badges/license.svg", use_shields=False)

# Python
license_ = Badge(left_txt="Python",
                 right_txt="3.8 | 3.9 | 3.10 | 3.11", color="#007ec6")
license_.write_to("badges/python.svg", use_shields=False)

# Tests
subprocess.check_call(
    "pytest --junitxml=reports/junit/junit.xml --html=reports/junit/report.html && \
        genbadge tests -o badges/tests.svg -n Tests", shell=True)

# Coverage
subprocess.call(
    "coverage run --source=pymerger -m unittest discover && coverage report && coverage html && coverage \
        xml -o reports/coverage/coverage.xml && genbadge coverage -o badges/coverage.svg -n Coverage", shell=True)
