#!/usr/bin/env python3
import glob, matplotlib.pyplot, matplotlib.ticker

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

def main(options):
    data={}
    for f in glob.glob(options.input):
        print(f)
        with open(f) as file:
            data[f] = [ line for line in file.read().splitlines() if "T+" in line or "F+" in line ]    
    
    Tp={}
    Fp={}
    for f in data:
        mtype = f.split('-')[-2]
        m = float(f.split('-')[-1])
        t = float(data[f][-1].split('|')[0].split(' ')[0])
        f = float(data[f][-1].split('|')[0].split(' ')[3])
        if mtype not in Tp:
            Tp[mtype]={}
            Fp[mtype]={}
        Tp[mtype][m] = t
        Fp[mtype][m] = f

    #print(Tp)
    #print(Fp)
    fig,axes=matplotlib.pyplot.subplots()
    ax = axes
    mtypes =  list(set([mtype for mtype in Tp]+[mtype for mtype in Fp]))
    def plot(Er,mtypes,ax,label='T+ M$_{%s}$-based',lstyles=['-',':'],**opt):
        for mtype in Er:
            s=mtypes.index(mtype)
            x=[m for m in Er[mtype]]
            y=[Er[mtype][m] for m in Er[mtype]]
            o=argsort(x)
            ax.plot([x[i] for i in o], [y[i] for i in o], ls=lstyles[s], label='T+ M$_{%s}$-based'%mtype,**opt)
    plot(Tp,mtypes,ax,color='C0')
    bx = ax.twinx()
    plot(Fp,mtypes,bx,label='F+ M$_{%s}$-based',color='C1')
    
    ax.legend(title='EEW error %$_{age}$')
    bx.legend(title='EEW error %$_{age}$')
    ax.set_xlabel('Magnitude threshold')
    bx.set_ylabel('F+ Percentage')
    ax.set_ylabel('T+ Percentage')
    
    ax.tick_params(top=True, bottom=True,
                   labelbottom=True, labeltop=True,
                   which='both')
    ax.grid(b=True, which='major', color='gray', linestyle='dashdot', zorder=-999)
    for axis in [ax.xaxis,ax.yaxis]:
        axis.label.set_size('small')
        axis.label.set_weight('bold')
        axis.label.set_fontstyle('oblique')
        axis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        axis.grid(which='minor', color='beige',  ls='-', zorder=-999)

    bx.yaxis.label.set_color('C1')
    bx.tick_params(axis='y', colors='C1')

    fig.savefig('fig.png',bbox_inches='tight',dpi=512,facecolor='none',transparent=False)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, 
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-i','--input',
                        default='./EEW-*-*',
                        #type=string,
                        help='Path to preprocessed error check.')

    args = parser.parse_args()

    main(args)
