#!/usr/bin/env python3
import glob,sys,geopip,numpy
#geocoder
#from pygeocoder import Geocoder

from obspy.core.event import Catalog
from obspy.clients.fdsn import client
from obspy.core import UTCDateTime
from obspy.geodetics import locations2degrees
from os.path import expanduser
home = expanduser("~")

def lineMagnitude(x1, y1, x2, y2):
    lineMagnitude = numpy.sqrt(numpy.power((x2 - x1), 2)+ numpy.power((y2 - y1), 2))
    return lineMagnitude

#Calc minimum distance from a point and a line segment (i.e. consecutive vertices in a polyline).
def DistancePointLine(px, py, x1, y1, x2, y2):
    #http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
    LineMag = lineMagnitude(x1, y1, x2, y2)

    if LineMag < 0.00000001:
        DistancePointLine = numpy.sqrt(numpy.power((px - x1), 2)+ numpy.power((py - y1), 2)) # 9999
        return DistancePointLine

    u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
    u = u1 / (LineMag * LineMag)

    if (u < 0.00001) or (u > 1):
        #// closest point does not fall within the line segment, take the shorter distance
        #// to an endpoint
        ix = lineMagnitude(px, py, x1, y1)
        iy = lineMagnitude(px, py, x2, y2)
        if ix > iy:
            DistancePointLine = iy
        else:
            DistancePointLine = ix
    else:
        # Intersecting point is on the line, use the formula
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        DistancePointLine = lineMagnitude(px, py, ix, iy)

    return DistancePointLine

def scfinderauthor(origin, lineauthors=['scfinder']):

    alpes=[7, 44.89, 9.42, 46.7]
    fromAlpes = DistancePointLine(origin.longitude,
                                                   origin.latitude,
                                                   *alpes)
    authors = []
    for a in lineauthors:
        authors+=[a]
        if fromAlpes*110.<80 :
            authors += ['scfdalpine']
        elif fromAlpes*110.<250:
            authors += ['scfdforela']
        else:
            from mpl_toolkits.basemap import Basemap
            bm = Basemap()
            if origin.depth / 1000 > 40:
                authors += ['scfd85sym']
            elif bm.is_land(origin.longitude, origin.latitude):
                authors += ['scfdcrust']
            else:
                authors += ['scfd20asym']
    return authors

def eventdistance(la, lo, de, e):
    laloref=[la,lo]
    o = e.preferred_origin() 
    lalo = [o.latitude, o.longitude]
    d = 11000*locations2degrees(lalo[0],lalo[1],laloref[0],laloref[1])
    return  ((d**2 + (de-o.depth)**2)**.5)/1000
                 

def findevent(lalode,t,events):
    refevent = None
    nearest=999
    closest=999
    for e in events:
        tdiff = t-e.preferred_origin().time
        distance = eventdistance(lalode[0],lalode[1],lalode[2], e)
        if ((distance<nearest and abs(tdiff)<abs(closest)) or
            (distance<nearest*2 and abs(tdiff)<abs(closest)) or
            (distance<nearest and abs(tdiff)<abs(closest)*2)):
            closest = tdiff
            nearest = distance
            refevent = e
    return refevent, closest, nearest
                
def isincountries(la,lo,countrycodes,dthresh=1.4):
    if countrycodes is None:
        return True
    inside=False
    lalo=[la,lo]
    for lad in [la+dthresh,la-dthresh,la]:
        for lod in [lo+dthresh,lo-dthresh,lo]:
            gcode=geopip.search(lng=lod, lat=lad)
            if gcode is None or gcode['ISO2'] is None:
                continue
            if gcode['ISO2'].lower() in countrycodes:
                return True
    if gcode is None or gcode['ISO2'] is None:#gcode.country_code is None:
        return False

def printsummary(true_positives,false_positives):
    total=len(true_positives)+len(false_positives)*1.0
    return ' & '.join(['%.1f %sT+'%(len(true_positives)*100./total, '%'),
                       '%.1f %sF+ | '%(len(false_positives)*100./total, '%')])
 
def main(options):
    reference = client.Client(options.reference)
    
    true_positives=[]
    false_positives=[]

    for f in glob.glob(options.reports):
        eventid = f.split('_')[-2]
        toprocess=False
        for y in range(options.begin,options.end):
            if str(y) in eventid:
                toprocess=True
                break
        if not toprocess:
            continue

        with open(f) as file:
            reports = [[elt.replace(' ','')[:19] for elt in line.split('|')] for line in file.read().splitlines()]
        #                                                           |#St.   |
        #Tdiff |Type|Mag.|Lat. |Lon. |Depth |origin time (UTC) |Lik.|Or.|Ma.|Str.|Len. |Author |Creation t. |Tdiff(current o.)
        #-----------------------------------------------

        if len(reports)>0 and len(reports[0])>0 and len(reports[0][0])==4 and reports[0][0]=='Mag.':
            reports=[ [report[3],'MVS',report[0],report[1],report[2],report[4],report[6],report[7],report[8],report[9],0,0,'scvsmag@localhost',report[5],report[3]] for report in reports if len(report)>=9 and report[0]!='Mag.' and 'MVS' in options.magtypes]
        #Mag.|Lat.  |Lon.   |tdiff |Depth |creation time (UTC)      |origin time (UTC)        |likeh.|#st.(org.) |#st.(mag.)

        reports=[report for report in reports if len(report)>9 and report[1] in options.magtypes and float(report[0])<=options.maxtimedelay]

        if len(reports)<1:
            continue

        maxmag = max([float(report[2]) for report in reports])
        maxlike = max([float(report[7]) for report in reports])
        
        if maxlike<options.minlikelihood:
            continue
        if maxmag<options.minmagnitude:
            continue
        
        longitude = numpy.median([float(report[4]) for report in reports])
        latitude = numpy.median([float(report[3]) for report in reports]) 
        lalo = [latitude, longitude]
        laloref=[options.latitude, options.longitude]
           
        if options.latitude is None:
            laloref = lalo
        if locations2degrees(lalo[0],lalo[1],laloref[0],laloref[1])>options.maxradius:
            continue
        if not isincountries(lalo[0],lalo[1],options.countrycodes):
            continue
                      
        to=numpy.sort([UTCDateTime(report[6]) for report in reports])[int(len(reports)/2)]
        evoptions={'starttime': to - options.time, #UTCDateTime('2970-12-31T23:59:59'),
                   'endtime':   to + options.time, #UTCDateTime('1970-01-01T01:01:01'),
                   'longitude': longitude,
                   'latitude':  latitude,
                   'maxradius': options.distance, 
                   }
        print(' | '.join([str(to), str(evoptions['latitude'])+', '+str(evoptions['longitude']), 'search...']))
        events=Catalog()
        try:
            events = reference.get_events(**evoptions)
        except:
            pass
        
        refevent = None
        finderauthors = ['scfinder']
        vsauthors = list(set([report[12].split('@')[0] for report in reports]))[:1]
        
        if len(events):
            #print('Found:')
            #print(events)
            refevent, delay, distance = findevent([evoptions['latitude'],
                                                   evoptions['longitude'],
                                                   numpy.median([float(report[5]) for report in reports])],
                                                   to, 
                                                   events)
            #print('Ref:')
            print(Catalog([refevent]))
            finderauthors = scfinderauthor(refevent.preferred_origin(), lineauthors=['scfinder'])
        
        done=[]
        for report in reports:
            if len(report)<9 or report[1] not in options.magtypes:
                continue
            if report[1] in done:
                continue
            if float(report[7])<options.minlikelihood:
                continue
            if float(report[2])<options.minmagnitude:
                continue
            if report[12].split('@')[0] not in finderauthors+vsauthors:
                continue

            done += [report[1]]
            
            lalo=[float(report[3]),float(report[4])]
            lalode=lalo+[float(report[5])]
            to = UTCDateTime(report[6])
            eloc = 9999
            emag = 99
            #print(' | '.join([str(report[6]), report[3]+', '+report[4], report[2]+' '+report[1], 'search...']))
            
            if refevent is not None:
                eloc = eventdistance(lalode[0],lalode[1],lalode[2], refevent)
                reforigin = refevent.preferred_origin()
                refmagnitude = refevent.preferred_magnitude()
                mmag = refmagnitude.mag + refmagnitude.mag_errors.uncertainty
                emag = float(report[2]) - refmagnitude.mag 
                
                if (mmag >= options.minmagnitude 
                    or emag<=options.maxmagnituderror):

                    true_positives += [(report[1], float(report[2]), float(report[7]),f)]
                    print('%s T+: Ot+ %s %s N %s E %s kmbsl %s %s L: %s dM: %s dloc: %s d km | %s'%(printsummary(true_positives,false_positives),
                          report[0],report[3],report[4],report[5],
                          report[1],
                          report[2],
                          report[7],
                          '%.1f'%emag,
                          '%d'%eloc,
                          f))
                    continue

            false_positives += [(report[1], float(report[2]), float(report[7]),f)]
            print('%s F+: Ot+ %s %s N %s E %s kmbsl %s %s L: %s dM: %s dloc: %s km | %s'%(printsummary(true_positives,false_positives),
                  report[0],report[3],report[4],report[5],
                  report[1],
                  report[2],
                  report[7],
                  '%.1f'%emag,
                  '%d'%eloc,
                  f))
            

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, 
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-r','--reports',
                        default='%s/.seiscomp3/log/EEW_reports/*report.txt'%home,
                        help='Absolute path to the sceewlog EEW reports.')
    parser.add_argument('-b', '--begin', 
                        type=int,
                        help='Year of earliest report to read',
                        default=1970)
    parser.add_argument('-e', '--end',
                        type=int,
                        help='Year of last report to read',
                        default=2970)
    parser.add_argument('-d', '--distance',
                        type=float,
                        help='Maximum allowed distance (degrees)',
                        default=0.5)
    parser.add_argument('-t', '--time',
                        type=int,
                        help='Maximum allowed time difference (second)',
                        default=50)
    parser.add_argument('-R', '--reference',
                        help='Reference FDSNWS server',
                        default='USGS')
    parser.add_argument('-m', '--minmagnitude',
                        type=float,
                        help='Minimum EEW magnitude',
                        default=2.5)
    parser.add_argument('-c', '--countrycodes',
                        help='Country codes (e.g., "ch,li")',
                        default=None)
    parser.add_argument('-l', '--latitude',
                        type=float,
                        help='latitude',
                        default=None)
    parser.add_argument('-L', '--longitude',
                        type=float,
                        help='Longitude',
                        default=None)
    parser.add_argument('-M', '--maxradius',
                        type=float,
                        help='Maximum distance to longitude and latitude',
                        default=1.0) 
    parser.add_argument('-q', '--minlikelihood',
                        type=float,
                        help='Minimum EEW likelihood (0 to 1, default -1 allows everything)',
                        default=-1.0)                          
    parser.add_argument('-D', '--maxtimedelay',
                        type=float,
                        help='Maximum allowed time delay (default 60)',
                        default=60.0)   
    parser.add_argument('-T', '--magtypes',
                        help='Magnitude types (default "MVS,Mfd")',
                        default='MVS,Mfd')   
    parser.add_argument('-E', '--maxmagnituderror',
                        type=float,
                        help='Max magnitude error',
                        default=0.5)

    args = parser.parse_args()

    main(args)
