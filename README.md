# SeisComP-EEW-Error-Check

Parses MVS and Mfd in `.seiscomp*/log/EEW_reports/` (sceewlog) and checks EEW errors within given country codes, compared to event parameter provided via a given  authoritative fdsnws.

## Dependencies
- python3
- geopip
- obspy
- numpy

## Usage

See:
```
./main.py -h
```

## Example

For Switzerland:
```
./main.py -b 2021 -R http://arclink.ethz.ch:8080 -c "ch,li"  -T Mfd  -m 2.5  -E 3 -M 2 -q 0.5
```

## Limits
- For quick parsing, it is based on sceewlog disk reports not on SeisComP database
- Missing plot
...
