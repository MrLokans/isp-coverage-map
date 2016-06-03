### Description ###

Parsers of belorusian high-speed internet coverage.
Parses data from ISP's (Beltelecom and MTS is now supported) sites and exports data to different file formats (currently only CSV is supported).


### Installation ###
Clone repo
```bash
git clone https://github.com/MrLokans/isp-coverage-map
```

Install package
```bash
cd isp-coverage-map
sudo pip setup.py install
```

### Usage ###

Script may be used straight from the shell
```bash
isp_coverage --name mts mts_coverage.csv
```

or from python scripts

```python
from by_isp_coverage import CSV_Exporter, MTS_Parser

parser = MTS_Parser()
exporter = CSV_Exporter()

points = parser.get_points()
exporter.export_points(points, "mts_coverage.csv")
```

### Contributing, troubleshooting and issues ###
Send all issues to [project's issues](https://github.com/MrLokans/isp-coverage-map/issues)
You're free to send pull requests :)

