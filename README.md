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

For Nicaragua:
```
python2 ./main.py -b 2016 -c "ni"  -T MVS  -m 5  -E 9 -M 9 -q 0.8  > MVS5
python2 ./main.py -b 2016 -c "ni"  -T MVS  -m 6  -E 9 -M 9 -q 0.8  > MVS6
python2 ./main.py -b 2016 -c "ni"  -T MVS,Mfd  -m 5  -E 9 -M 9 -q 0.8  > M5
python2 ./main.py -b 2016 -c "ni"  -T MVS,Mfd  -m 6  -E 9 -M 9 -q 0.8  > M6
```

## Limits
- For quick parsing, it is based on sceewlog disk reports not on SeisComP database
...
