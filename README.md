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

For a preview:
```
./main.py -b 2021 -R http://arclink.ethz.ch:8080 -c "ch,li"  -T Mfd  -m 2.5  -E 3 -M 2 -q 0.5
```

For a complete analysis:
```
for L in  $(seq 0 .1 1);
do 
	rm -r q${L}/*
	mkdir -p q${L} 
	for M in  $(seq 4 .1 6.5); 
	do 
		python2 ./main.py -b 2016 -c "ni"  -T MVS,Mfd  -m ${M}  -E 9 -M 9 -q $L  > q${L}/EEW-VS,fd-${M} ; 
		python2 ./main.py -b 2016 -c "ni"  -T MVS      -m ${M}  -E 9 -M 9 -q $L  > q${L}/EEW-VS-${M} ; 
		#cd q${L} && DISPLAY=:1 python2 ../plot.py && cd .. ;
	done;
done
```

## Limits
- For quick parsing, it is based on sceewlog disk reports not on SeisComP database
...
