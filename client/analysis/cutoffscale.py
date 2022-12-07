import matplotlib as mpl
import matplotlib.scale as mscale
import matplotlib.dates as mdates
import matplotlib.transforms as mtransforms
from matplotlib.ticker import (
    NullFormatter, ScalarFormatter, LogFormatterSciNotation, LogitFormatter,
    NullLocator, LogLocator, AutoLocator, AutoMinorLocator,
    SymmetricalLogLocator, LogitLocator)
    
import numpy as np

class CutoffScale(mscale.ScaleBase):
    """
    Axis scale composed of arbitrary piecewise linear transformations.
    The axis can undergo discrete jumps, "accelerations", or "decelerations"
    between successive thresholds.
    """
    #: The registered scale name
    name = 'cutoff'

    def __init__(self, axis, args):
        """
        Parameters
        ----------
        args : thresh_1, scale_1, ..., thresh_N, [scale_N], optional
            Sequence of "thresholds" and "scales". If the final scale is
            omitted (i.e. you passed an odd number of arguments) it is set
            to ``1``. Each ``scale_i`` in the sequence can be interpreted
            as follows:

            * If ``scale_i < 1``, the axis is decelerated from ``thresh_i`` to
              ``thresh_i+1``. For ``scale_N``, the axis is decelerated
              everywhere above ``thresh_N``.
            * If ``scale_i > 1``, the axis is accelerated from ``thresh_i`` to
              ``thresh_i+1``. For ``scale_N``, the axis is accelerated
              everywhere above ``thresh_N``.
            * If ``scale_i == numpy.inf``, the axis *discretely jumps* from
              ``thresh_i`` to ``thresh_i+1``. The final scale ``scale_N``
              *cannot* be ``numpy.inf``.

        See also
        --------
        proplot.constructor.Scale

        Example
        -------
        >>> import proplot as pplt
        >>> import numpy as np
        >>> scale = pplt.CutoffScale(10, 0.5)  # move slower above 10
        >>> scale = pplt.CutoffScale(10, 2, 20)  # move faster between 10 and 20
        >>> scale = pplt.CutoffScale(10, np.inf, 20)  # jump from 10 to 20
        """
        # NOTE: See https://stackoverflow.com/a/5669301/4970632
        super().__init__(axis)
        args = list(args)
        if len(args) % 2 == 1:
            args.append(1)
        self.args = args
        self.threshs = args[::2]
        self.scales = args[1::2]
        self._transform = CutoffTransform(self.threshs, self.scales)

    def set_default_locators_and_formatters(self, axis):
        # docstring inherited
        axis.set_major_locator(AutoLocator())
        axis.set_major_formatter(ScalarFormatter())
        axis.set_minor_formatter(NullFormatter())
        # update the minor locator for x and y axis based on rcParams
        if (axis.axis_name == 'x' and mpl.rcParams['xtick.minor.visible'] or
                axis.axis_name == 'y' and mpl.rcParams['ytick.minor.visible']):
            axis.set_minor_locator(AutoMinorLocator())
        else:
            axis.set_minor_locator(NullLocator())

    def get_transform(self):
        """Return the `.FuncTransform` associated with this scale."""
        return self._transform

class CutoffTransform(mtransforms.Transform):
    input_dims = 1
    output_dims = 1
    has_inverse = True
    is_separable = True

    def __init__(self, threshs, scales, zero_dists=None):
        # The zero_dists array is used to fill in distances where scales and
        # threshold steps are zero. Used for inverting discrete transorms.
        super().__init__()
        dists = np.diff(threshs)
        scales = np.asarray(scales)
        threshs = np.asarray(threshs)
        if len(scales) != len(threshs):
            raise ValueError(f'Got {len(threshs)} but {len(scales)} scales.')
        if any(scales < 0):
            raise ValueError('Scales must be non negative.')
        if scales[-1] in (0, np.inf):
            raise ValueError('Final scale must be finite.')
#        if any(dists < 0):
#            raise ValueError('Thresholds must be monotonically increasing.')
#        if any((dists == 0) | (scales == 0)):
#            if zero_dists is None:
#                raise ValueError('Keyword zero_dists is required for discrete steps.')
#            if any((dists == 0) != (scales == 0)):
#                raise ValueError('Input scales disagree with discrete step locations.')
        self._scales = scales
        self._threshs = threshs
        with np.errstate(divide='ignore', invalid='ignore'):
            dists = np.concatenate((threshs[:1], dists / scales[:-1]))
            if zero_dists is not None and len(zero_dists):
                dists[scales[:-1] == 0] = zero_dists
            self._dists = dists

    def inverted(self):
        # Use same algorithm for inversion!
        threshs = np.cumsum(self._dists)  # thresholds in transformed space
        with np.errstate(divide='ignore', invalid='ignore'):
            scales = 1.0 / self._scales  # new scales are inverse
        zero_dists = np.diff(self._threshs)[scales[:-1] == 0]
        return CutoffTransform(threshs, scales, zero_dists=zero_dists)

    def transform_non_affine(self, a):
        # Cannot do list comprehension because this method sometimes
        # received non-1D arrays
        dists = self._dists
        scales = self._scales
        threshs = self._threshs
        aa = np.array(a)  # copy
        with np.errstate(divide='ignore', invalid='ignore'):
            for i, ai in np.ndenumerate(a):
                j = np.searchsorted(threshs, ai)
                if j > 0:
                    aa[i] = dists[:j].sum() + (ai - threshs[j - 1]) / scales[j - 1]
        return aa
        
mscale.register_scale(CutoffScale)
#
#import matplotlib.pyplot as plt
#from matplotlib.ticker import NullFormatter, FixedLocator
#
## Fixing random state for reproducibility
#np.random.seed(19680801)
#
## make up some data in the interval ]0, 1[
#y = np.random.normal(loc=0.5, scale=0.4, size=1000)
#y = y[(y > 0) & (y < 1)]
#y.sort()
#x = np.arange(len(y))
#
## plot with various axes scales
#fig, axs = plt.subplots(3, 2, figsize=(6, 8),
#                        constrained_layout=True)
#
## linear
#ax = axs[0, 0]
#ax.plot(x, y)
#ax.set_yscale('cutoff', args=[0.25, 0.5, 0.75, 2])
#ax.set_title('linear')
#ax.grid(True)
#
#
## log
#ax = axs[0, 1]
#ax.plot(x, y)
#ax.set_yscale('log')
#ax.set_title('log')
#ax.grid(True)
#
#
## symmetric log
#ax = axs[1, 1]
#ax.plot(x, y - y.mean())
#ax.set_yscale('symlog', linthresh=0.02)
#ax.set_title('symlog')
#ax.grid(True)
#
## logit
#ax = axs[1, 0]
#ax.plot(x, y)
#ax.set_yscale('logit')
#ax.set_title('logit')
#ax.grid(True)
#
#
## Function x**(1/2)
#def forward(x):
#    return x**(1/2)
#
#
#def inverse(x):
#    return x**2
#
#
#ax = axs[2, 0]
#ax.plot(x, y)
#ax.set_yscale('function', functions=(forward, inverse))
#ax.set_title('function: $x^{1/2}$')
#ax.grid(True)
#ax.yaxis.set_major_locator(FixedLocator(np.arange(0, 1, 0.2)**2))
#ax.yaxis.set_major_locator(FixedLocator(np.arange(0, 1, 0.2)))
#
#
## Function Mercator transform
#def forward(a):
#    a = np.deg2rad(a)
#    return np.rad2deg(np.log(np.abs(np.tan(a) + 1.0 / np.cos(a))))
#
#
#def inverse(a):
#    a = np.deg2rad(a)
#    return np.rad2deg(np.arctan(np.sinh(a)))
#
#ax = axs[2, 1]
#
#t = np.arange(0, 170.0, 0.1)
#s = t / 2.
#
#ax.plot(t, s, '-', lw=2)
#
#ax.set_yscale('function', functions=(forward, inverse))
#ax.set_title('function: Mercator')
#ax.grid(True)
#ax.set_xlim([0, 180])
#ax.yaxis.set_minor_formatter(NullFormatter())
#ax.yaxis.set_major_locator(FixedLocator(np.arange(0, 90, 10)))
#
#plt.show()
