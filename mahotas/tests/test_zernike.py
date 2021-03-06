import numpy as np
from mahotas.features import zernike_moments
from mahotas.center_of_mass import center_of_mass
from math import atan2
from numpy import cos, sin, conjugate, pi, sqrt

def _slow_znl(Y,X,P,n,l):
    def _polar(r,theta):
        x = r * cos(theta)
        y = r * sin(theta)
        return 1.*x+1.j*y

    v = 0.+0.j
    def _factorial(n):
        if n == 0: return 1.
        return n * _factorial(n - 1)
    y,x = Y[0],X[0]
    for x,y,p in zip(X,Y,P):
        Vnl = 0.
        for m in range( int( (n-l)//2 ) + 1 ):
            Vnl += (-1.)**m * _factorial(n-m) /  \
                ( _factorial(m) * _factorial((n - 2*m + l) // 2) * _factorial((n - 2*m - l) // 2) ) * \
                ( sqrt(x*x + y*y)**(n - 2*m) * _polar(1.0, l*atan2(y,x)) )
        v += p * conjugate(Vnl)
    v *= (n+1)/pi
    return v 

def _slow_zernike(img, radius, D, cof=None):
    zvalues = []

    Y,X = np.where(img > 0)
    P = img[Y,X].ravel()
    if cof is None:
        cofy,cofx = center_of_mass(img)
    else:
        cofy,cofx = cof
    Yn = ( (Y -cofy)/radius).ravel()
    Xn = ( (X -cofx)/radius).ravel()
    k = (np.sqrt(Xn**2 + Yn**2) <= 1.)
    frac_center = np.array(P[k], np.double)
    frac_center /= frac_center.sum()
    Yn = Yn[k]
    Xn = Xn[k]
    frac_center = frac_center.ravel()

    for n in range(D+1):
        for l in range(n+1):
            if (n-l)%2 == 0:
                z = _slow_znl(Yn, Xn, frac_center, float(n), float(l))
                zvalues.append(abs(z))
    return np.array(zvalues)

def test_zernike():
    A = (np.arange(256) % 14).reshape((16, 16))
    slow = _slow_zernike(A, 8., 12)
    fast = zernike_moments(A, 8., 12)
    delta = np.array(slow) - fast
    assert np.abs(delta).max() < 0.001

def test_zernike_cm():
    A = (np.arange(256) % 14).reshape((16, 16))
    cm = (8.9,12.4)
    slow = _slow_zernike(A, 8., 12, cm)
    fast = zernike_moments(A, 8., 12, cm=cm)
    delta = np.array(slow) - fast
    assert np.abs(delta).max() < 0.001

