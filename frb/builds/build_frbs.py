""" Module to generate individual FRB files """

from pkg_resources import resource_filename

import numpy as np

from astropy import units
from astropy.coordinates import SkyCoord

from frb import frb


def frb_121102():
    """
    FRB 121102
        All of the data currently comes from Tendulkar et al. 2017
        https://ui.adsabs.harvard.edu/abs/2017ApJ...834L...7T/abstract
    """
    frb121102 = frb.FRB('FRB121102', 'J053158.7+330852.5',
                        558.1*units.pc/units.cm**3,
                        z_frb=0.19273)
    # NE2001
    frb121102.set_DMISM()
    # Error ellipse
    frb121102.set_ee(0.1, 0.1, 0., 95.)
    # References
    frb121102.refs = ['Tendulkar2017']
    # Write
    frb121102.write_to_json()
    # Test
    frb121102.from_json('FRB121102.json')


def frb_180916():
    """
     FRB 180916.J0158+65
        All of the data currently comes from Marcote et al. 2020
        https://ui.adsabs.harvard.edu/abs/2020Natur.577..190M/abstract
    """
    coord = SkyCoord("01h58m00.75017s 65d43m00.3152s", frame='icrs')
    name = 'FRB180916'
    frb180916 = frb.FRB(name, coord,
                        348.76*units.pc / units.cm**3,
                        z_frb=0.0337)
    # Error ellipse
    frb180916.set_ee(0.0023, 0.0023, 0., 68.)
    # Error in DM
    frb180916.DM_err = 0.10 * units.pc / units.cm**3
    # NE2001
    frb180916.set_DMISM()
    #
    #frb180924.fluence = 16 * units.Jy * units.ms
    #frb180924.fluence_err = 1 * units.Jy * units.ms
    #
    # References
    frb180916.refs = ['Marcote2020']
    # Write
    path = resource_filename('frb', 'data/FRBs')
    frb180916.write_to_json(path=path)

def frb_180924():
    """
    FRB 180924
        All of the data currently comes from Bannister et al. 2019
        https://ui.adsabs.harvard.edu/abs/2019Sci...365..565B/abstract
    """
    frb180924 = frb.FRB('FRB180924', 'J214425.26-405400.1',
                        361.4*units.pc / units.cm**3,
                        z_frb=0.3212)
    # Error in DM (Bannister 2019)
    frb180924.DM_err = 0.06 * units.pc / units.cm**3

    # NE2001
    frb180924.set_DMISM()

    # Bannister 2019
    frb180924.fluence = 16 * units.Jy * units.ms
    frb180924.fluence_err = 1 * units.Jy * units.ms
    frb180924.RM = 14 * units.rad / units.m**2
    frb180924.RM_err = 1 * units.rad / units.m**2
    frb180924.lpol = 80.  # %
    frb180924.lpol_err = 10.
    # Error ellipse
    frb180924.set_ee(a=100./1e3, b=100./1e3, theta=0., cl=68.)

    # References
    frb180924.refs = ['Bannister2019']

    # Write
    path = resource_filename('frb', 'data/FRBs')
    frb180924.write_to_json(path=path)

def frb_181112():
    """
    Generate the JSON file for FRB 181112
        All of the data comes from Prochaska+2019, Science, in press

    Returns:

    """
    frb181112 = frb.FRB('FRB181112', 'J214923.63-525815.33',
                        589.27 * units.pc / units.cm**3,
                        z_frb=0.4755)
    # Error in DM
    frb181112.DM_err = 0.03 * units.pc / units.cm**3
    # Error ellipse
    frb181112.set_ee(a=555.30/1e3, b=152.93/1e3, theta=120.15, cl=68.)
    # RM
    frb181112.RM = 10.9 * units.rad / units.m**2
    frb181112.RM_err = 0.9 * units.rad / units.m**2

    # NE2001
    frb181112.set_DMISM()

    # References
    frb181112.refs = ['Prochaska2019']

    # Write
    path = resource_filename('frb', 'data/FRBs')
    frb181112.write_to_json(path=path)

def frb_190102():
    """Bhandari+20, ApJL --
    """
    fname = 'FRB190102'
    wv_oiii = 6466.48
    z_OIII = wv_oiii / 5008.239 - 1
    frb190102 = frb.FRB(fname, 'J212939.7-792832.3', # Pulled from Slack 26-03-2019
                        362 * units.pc / units.cm**3,
                        z_frb=z_OIII)
    # Error ellipse [REQUIRED]
    frb190102.set_ee(0.1, 0.1, 0., 95.)

    # Error in DM
    frb190102.DM_err = 1 * units.pc / units.cm**3

    # NE2001
    frb190102.set_DMISM()
    # RM
    #frb190102.RM = 10 * units.rad / units.m**2
    #frb190102.RM_err = 1 * units.rad / units.m**2

    # References
    frb190102.refs = ['Bhandari2019']

    # Write
    path = resource_filename('frb', 'data/FRBs')
    frb190102.write_to_json(path=path)


def frb_190523():
    """Ravi+19, Nature --
        https://ui.adsabs.harvard.edu/abs/2019Natur.572..352R/abstract
    """
    fname = 'FRB190523'
    frb190523 = frb.FRB(fname, 'J134815.6+722811',
                        760.8 * units.pc / units.cm**3,
                        z_frb=0.660)
    # Error ellipse [REQUIRED]
    frb190523.set_ee(5, 2, 0., 340) # JXP eyeball
    # Error in DM
    frb190523.DM_err = 0.6 * units.pc / units.cm**3

    # Fluence
    frb190523.fluence = 280 * units.Jy * units.ms
    #frb180924.fluence_err = 1 * units.Jy * units.ms

    # NE2001
    frb190523.set_DMISM()

    # RM
    #frb190102.RM = 10 * units.rad / units.m**2
    #frb190102.RM_err = 1 * units.rad / units.m**2

    # References
    frb190523.refs = ['Ravi2019']

    # Write
    path = resource_filename('frb', 'data/FRBs')
    frb190523.write_to_json(path=path)

def frb_190608():
    """Bhandari+20, ApJL, Day+20, in prep. --
    Macquart al. Nature
    """
    fname = 'FRB190608'
    frb190608 = frb.FRB(fname, "J221604.77-075353.7",  # Pulled from Slack on 2020 Mar 18
                        339.8 * units.pc / units.cm**3,
                        z_frb=0.1177805)  # Taken from the SDSS table
    # Error ellipse [REQUIRED]
    frb190608.set_ee(0.19315, 0.18, 0., 68.) # Statistsical
    frb190608.set_ee(0.178292, 0.18, 0., 68., stat=False)  # Systematic
    # Error in DM
    frb190608.DM_err = 1 * units.pc / units.cm**3

    # NE2001
    frb190608.set_DMISM()
    # RM
    #frb190102.RM = 10 * units.rad / units.m**2
    #frb190102.RM_err = 1 * units.rad / units.m**2

    # References
    frb190608.refs = ['Bhandari2020','Day2020']

    # Write
    path = resource_filename('frb', 'data/FRBs')
    frb190608.write_to_json(path=path)


def frb_190611():
    """
    Macquart al. Nature
    Day et al. 2020
    """
    FRB_190611_coord = SkyCoord('J212258.91-792351.3',  # Day+2020
                                unit=(units.hourangle, units.deg))
    frb190611 = frb.FRB('FRB190611', FRB_190611_coord,
                        332.6 * units.pc / units.cm**3)
    # Error ellipse [REQUIRED]
    frb190611.set_ee(0.7, 0.7, 0., 68.)
    # Error in DM
    frb190611.DM_err = 1 * units.pc / units.cm**3

    # NE2001
    frb190611.set_DMISM()
    # RM
    #frb190611.RM = 20 * units.rad / units.m**2
    #frb190611.RM_err = 4 * units.rad / units.m**2

    # References
    frb190611.refs = ['MacQuart2019', 'Day2020']

    # Write
    path = resource_filename('frb', 'data/FRBs')
    frb190611.write_to_json(path=path)


def frb_190711():
    """MacQuart+20, Day+2020
    """
    fname = 'FRB190711'
    frb190711 = frb.FRB(fname, 'J215740.68-802128.8',  # MacQuarter+2020, Day+2020
                        587.9 * units.pc / units.cm ** 3,    # Day+2020
                        z_frb=0.52172)
    # Error ellipse
    frb190711.set_ee(0.3, 0.3, 0., 68.)  # (Statistical)
    frb190711.set_ee(0.38, 0.3, 0., 68., stat=False)  # Systematic

    # Error in DM
    frb190711.DM_err = 1 * units.pc / units.cm ** 3

    # NE2001
    frb190711.set_DMISM()
    # RM -- Day+2020
    frb190711.RM = 9 * units.rad / units.m**2
    frb190711.RM_err = 2 * units.rad / units.m**2

    # References
    frb190711.refs = ['MacQuart2019', 'Day+2020']

    # Write
    path = resource_filename('frb', 'data/FRBs')
    frb190711.write_to_json(path=path)


def main(inflg='all'):

    if inflg == 'all':
        flg = np.sum(np.array( [2**ii for ii in range(25)]))
    else:
        flg = int(inflg)

    # 121102
    if flg & (2**0):
        frb_121102()

    # 180924
    if flg & (2**1):  # 2
        frb_180924()

    # 181112
    if flg & (2**2):
        frb_181112()

    # 195023
    if flg & (2**3):
        frb_190523()

    # 190608
    if flg & (2**4):
        frb_190608()

    # 190102
    if flg & (2**5):
        frb_190102()

    # 190711
    if flg & (2**6): # 64
        frb_190711()

    # 190611
    if flg & (2**7):  # 128
        frb_190611()

    # 180916
    if flg & (2**8): # 256
        frb_180916()



# Command line execution
#  Only for testing
#  Use the Build script to build
if __name__ == '__main__':
    # FRB 121102
    frb_121102()



