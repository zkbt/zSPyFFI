'''Simulate some toy model light curves.'''

from imports import *
import zachopy.units as u


def parseCode(code):
    '''extract name and traits from a lightcurve code'''

    traits = {}
    name, traitstrings = code.split('|')
    for t in traitstrings.split(','):
        k, v = t.split('=')
        traits[k] = np.float(v)
    return name, traits

def generate(code):
    name, traits = parseCode(code)
    return globals()[name](**traits)

def random(options=['trapezoid', 'sin']):
    name = np.random.choice(options)
    if name == 'sin':
        P=10**np.random.uniform(*np.log10([0.1, 30.0]))
        E=np.random.uniform(0,P)
        A=10**np.random.uniform(*np.log10([0.0001, 0.02]))
        return sin(**locals())

    if name == 'trapezoid':
        P=10**np.random.uniform(*np.log10([0.1, 30.0]))
        E=np.random.uniform(0,P)

        mass = np.random.uniform(0.1, 1.5)
        radius = mass
        stellar_density = 3*mass*u.Msun/(4*np.pi*(radius*u.Rsun)**3)
        rsovera = (3*np.pi/u.G/(P*u.day)**2/stellar_density)**(1.0/3.0)
        T14 = rsovera*P/np.pi
        T23=np.random.uniform(0, T14)
        D=10**np.random.uniform(*np.log10([0.0001, 0.01]))

        return trapezoid(**locals())

def test(n=100,step=0.01, **kw):
    plt.cla()
    f = plt.figure(figsize=(5,10))
    ax = plt.subplot()
    o =0
    for i in range(n):
        lc = random(**kw)
        lc.demo(offset=o, ax=ax)
        o += step

    ax.set_ylim(step*n, 0)
    plt.draw()

class Cartoon(Talker):
    def __init__(self):
        Talker.__init__(self)

    def demo(self, tmin=0, tmax=27.4, cadence=30.0/60.0/24.0, offset=0, raw=False, ax=None):
        t = np.arange(tmin, tmax, cadence)
        if ax is None:
            plt.figure('demo', figsize=(8,3))
        else:
            plt.sca(ax)
        y = self.model(t)
        if raw:
            plt.plot(t, y+offset, alpha=0.25, linewidth=4, color='royalblue')
        plt.plot(t, self.integrated(t)+offset, alpha=0.5, linewidth=4, color='darkorange')
        plt.xlim(tmin,tmax)
        #plt.ylim(np.max(y)+0.01, np.min(y)-0.01)
        plt.xlabel('Time (days)')
        plt.ylabel('Flux (mag.)')

    @property
    def code(self):
        '''returns a string describing the cartoon lightcurve'''
        t = ''
        for k, v in self.traits.iteritems():
            t += '{k}={v},'.format(k=k,v=v)

        return '{0}({1})'.format(self.__class__.__name__, t[:-1])

    def integrated(self, t, exptime=30.0/60.0/24.0, resolution=100):

        nudges = np.linspace(-exptime/2.0, exptime/2.0, resolution)
        subsampled = t.reshape(1, t.shape[0]) + nudges.reshape(nudges.shape[0], 1)
        return np.log(np.exp(self.model(subsampled)).mean(0))

    def __repr__(self):
        return '<{0}>'.format(self.code)


class constant(Cartoon):
    def __init__(self, **kw):
        self.traits = {}
        Cartoon.__init__(self)

    def model(self, t):
        return 0.0

class sin(Cartoon):
    def __init__(self, P=3.1415926, E=0.0, A=0.1, **kw):
        self.traits = dict(P=P, E=E, A=A)
        Cartoon.__init__(self)

    def model(self,t):
        return self.traits['A']*np.sin(2*np.pi*(t - self.traits['E'])/self.traits['P'])

class trapezoid(Cartoon):
    def __init__(self, P=3.1415926, E=0.0, D=0.01, T23=0.1, T14=0.1, **kw):
        self.traits = dict(P=P, E=E, D=D, T23=T23, T14=T14)
        Cartoon.__init__(self)

    def closesttransit(self, t):
        return np.round((t-self.traits['E'])/self.traits['P'])*self.traits['P'] + self.traits['E']

    def timefrommidtransit(self, t):
        return t-self.closesttransit(t)

    def model(self,t):
        flux = np.zeros_like(t)
        dt = np.abs(self.timefrommidtransit(t))
        start, finish = self.traits['T23']/2.0, self.traits['T14']/2.0
        depth = self.traits['D']

        i = dt <= start
        flux[i] = depth
        i = (dt<=finish)*(dt>start)
        flux[i] = (finish-dt[i])/(finish-start)*depth

        return flux
