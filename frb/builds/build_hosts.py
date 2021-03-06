""" Top-level module to build or re-build the JSON files for
FRB host galaxies"""

from pkg_resources import resource_filename
import os
import sys
import warnings

from IPython import embed

import numpy as np

from astropy.coordinates import SkyCoord
from astropy import units
from astropy.table import Table
from astropy.coordinates import match_coordinates_sky

from frb.galaxies import frbgalaxy, defs
from frb.galaxies import photom as frbphotom
from frb.galaxies import ppxf
from frb.galaxies import nebular
from frb.surveys import des
from frb.surveys import sdss
from frb.surveys import wise
from frb.surveys import panstarrs

try:
    import extinction
except ImportError:
    print("extinction package not loaded.  Extinction corrections will fail")

try:
    from frb.galaxies import cigale
except ModuleNotFoundError:
    warnings.warn("You haven't installed pcigale and won't be able to do that analysis")

from linetools.spectra.xspectrum1d import XSpectrum1D

db_path = os.getenv('FRB_GDB')
if db_path is None:
    print("Warning, you need to set $FRB_GDB to build hosts")
    #embed(header='You need to set $FRB_GDB')


def build_host_121102(build_photom=False):
    """
    Generate the JSON file for FRB 121102

    Writes to 121102/FRB121102_host.json

    All of the data currently comes from Tendulkar et al. 2017

    Args:
        build_photom (bool, optional): Generate the photometry file in the Galaxy_DB

    """
    FRB_coord = SkyCoord('05h31m58.698s +33d8m52.59s', frame='icrs')
    # Eyeball Tendulkar+17 PA
    gal_coord = FRB_coord.directional_offset_by(-45 * units.deg, 286e-3 * units.arcsec)

    # Instantiate
    host121102 = frbgalaxy.FRBHost(gal_coord.ra.value, gal_coord.dec.value, '121102')

    # Redshift
    host121102.set_z(0.19273, 'spec', err=0.00008)

    # Photometry -- Tendulkar 2017
    photom_file = os.path.join(db_path, 'Repeater', 'Tendulkar2017', 'tendulkar2017_photom.ascii')
    if build_photom:
        photom = Table()
        #photom['Name'] = ['HG121102']  DO NOT USE str columns!
        photom['ra'] = [host121102.coord.ra.value]
        photom['dec'] = host121102.coord.dec.value
        #
        photom['GMOS_N_r'] = 25.1
        photom['GMOS_N_r_err'] = 0.1
        photom['GMOS_N_i'] = 23.9
        photom['GMOS_N_i_err'] = 0.1
        # Write
        photom = frbphotom.merge_photom_tables(photom, photom_file)
        photom.write(photom_file, format=frbphotom.table_format, overwrite=True)
    host121102.parse_photom(Table.read(photom_file, format=frbphotom.table_format))

    # Nebular lines
    neb_lines = {}
    neb_lines['Halpha'] = 0.652e-16
    neb_lines['Halpha_err'] = 0.009e-16
    neb_lines['Halpha_Al'] = 0.622
    #
    neb_lines['Hbeta'] = 0.118e-16
    neb_lines['Hbeta_err'] = 0.011e-16
    neb_lines['Hbeta_Al'] = 0.941
    #
    neb_lines['[OIII] 5007'] = 0.575e-16
    neb_lines['[OIII] 5007_err'] = 0.011e-16
    neb_lines['[OIII] 5007_Al'] = 0.911
    #
    neb_lines['[NII] 6584'] = 0.030e-16  # * units.erg/units.cm**2/units.s      # Upper limit
    neb_lines['[NII] 6584_err'] = -999.  # * units.erg/units.cm**2/units.s      # Upper limit
    neb_lines['[NII] 6584_Al'] = 0.619

    AV = 2.42

    # Extinction correct
    for key in neb_lines.keys():
        if '_err' in key:
            continue
        if 'Al' in key:
            continue
        # Ingest
        host121102.neb_lines[key] = neb_lines[key] * 10 ** (neb_lines[key + '_Al'] * AV / 2.5)
        if neb_lines[key + '_err'] > 0:
            host121102.neb_lines[key + '_err'] = neb_lines[key + '_err'] * 10 ** (neb_lines[key + '_Al'] * AV / 2.5)
        else:
            host121102.neb_lines[key + '_err'] = neb_lines[key + '_err']

    # Vette
    for key in host121102.neb_lines.keys():
        if '_err' in key:
            continue
        assert key in defs.valid_neb_lines

    # Morphology
    host121102.morphology['reff_ang'] = 0.41
    host121102.morphology['reff_ang_err'] = 0.06
    #
    host121102.morphology['n'] = 2.2
    host121102.morphology['n_err'] = 1.5
    #
    host121102.morphology['b/a'] = 0.25
    host121102.morphology['b/a_err'] = 0.13

    # Derived quantities
    host121102.derived['M_r'] = -17.0  # AB; Tendulkar+17
    host121102.derived['M_r_err'] = 0.2  # Estimated by JXP
    host121102.derived['SFR_nebular'] = 0.23  # MSun/yr; Tendulkar+17
    host121102.derived['Mstar'] = 5.5e7  # Msun; Tendulkar+17
    host121102.derived['Mstar_err'] = 1.5e7  # Msun; Tendulkar+17
    host121102.derived['Z_spec'] = -0.16  # Tendulkar+17 on a scale with Solar O/H = 8.86
    host121102.derived['Z_spec_err'] = -999.  # Tendulkar+17

    # Vet
    assert host121102.vet_all()

    # Write
    path = resource_filename('frb', 'data/Galaxies/121102')
    host121102.write_to_json(path=path, overwrite=True)


def build_host_180924(build_photom=True):
    """
    Generate the JSON file for FRB 180924
    
    All data are from Bannister et al. 2019
        https://ui.adsabs.harvard.edu/abs/2019Sci...365..565B/abstract

    Writes to 180924/FRB180924_host.json

    Args:
        build_photom (bool, optional): Generate the photometry file in the Galaxy_DB
    """
    frbname = '180924'
    gal_coord = SkyCoord('J214425.25-405400.81', unit=(units.hourangle, units.deg))

    # Instantiate
    host = frbgalaxy.FRBHost(gal_coord.ra.value, gal_coord.dec.value, '180924')

    # Redshift -- JXP measured from multiple data sources
    host.set_z(0.3212, 'spec')

    # Morphology
    host.parse_galfit(os.path.join(db_path, 'CRAFT', 'Bannister2019',
                                   'HG180924_DES_galfit.log'), 0.263)

    # Photometry
    # DES
    search_r = 2*units.arcsec
    des_srvy = des.DES_Survey(gal_coord, search_r)
    des_tbl = des_srvy.get_catalog(print_query=True)
    host.parse_photom(des_tbl)

    # Grab the table (requires internet)
    photom_file = os.path.join(db_path, 'CRAFT', 'Bannister2019', 'bannister2019_photom.ascii')
    if build_photom:
        photom = Table()
        photom['Name'] = ['HG{}'.format(frbname)]
        photom['ra'] = host.coord.ra.value
        photom['dec'] = host.coord.dec.value
        photom['VLT_g'] = 21.38
        photom['VLT_g_err'] = 0.04
        photom['VLT_I'] = 20.10
        photom['VLT_I_err'] = 0.02
        # Add in DES
        for key in host.photom.keys():
            photom[key] = host.photom[key]
        # Merge/write
        photom = frbphotom.merge_photom_tables(photom, photom_file)
        photom.write(photom_file, format=frbphotom.table_format, overwrite=True)

    # Parse
    host.parse_photom(Table.read(photom_file, format=frbphotom.table_format))
    #host.parse_photom(des_tbl)

    # PPXF
    host.parse_ppxf(os.path.join(db_path, 'CRAFT', 'Bannister2019', 'HG180924_MUSE_ppxf.ecsv'))

    # Derived quantities

    # AV
    host.calc_nebular_AV('Ha/Hb')

    # SFR
    host.calc_nebular_SFR('Ha')
    host.derived['SFR_nebular_err'] = -999.

    # CIGALE
    host.parse_cigale(os.path.join(db_path, 'CRAFT', 'Bannister2019',
                                   'HG180924_CIGALE.fits'), 0.263)

    # Vet all
    host.vet_all()

    # Write
    path = resource_filename('frb', 'data/Galaxies/180924')
    host.write_to_json(path=path)


def build_host_181112(build_photom=False):
    """ Build the host galaxy data for FRB 181112

    All of the data comes from Prochaska+2019, Science

    Args:
        build_photom (bool, optional):

    """
    frbname = '181112'
    FRB_coord = SkyCoord('J214923.63-525815.39',
                         unit=(units.hourangle, units.deg))  # Cherie;  2019-04-17 (Slack)
    # Coord from DES
    Host_coord = SkyCoord('J214923.66-525815.28',
                          unit=(units.hourangle, units.deg))  # from DES

    # Instantiate
    host181112 = frbgalaxy.FRBHost(Host_coord.ra.value, Host_coord.dec.value, frbname)
    host181112.frb_coord = FRB_coord

    # Redshift
    host181112.set_z(0.4755, 'spec', err=7e-5)

    # ############
    # Photometry

    # DES
    # Grab the table (requires internet)
    search_r = 2 * units.arcsec
    des_srvy = des.DES_Survey(Host_coord, search_r)
    des_tbl = des_srvy.get_catalog(print_query=True)

    host181112.parse_photom(des_tbl)

    # VLT -- Lochlan 2019-05-02
    # VLT -- Lochlan 2019-06-18
    photom_file = os.path.join(db_path, 'CRAFT', 'Prochaska2019', 'prochaska2019_photom.ascii')
    if build_photom:
        photom = Table()
        photom['Name'] = ['HG{}'.format(frbname)]
        photom['ra'] = host181112.coord.ra.value
        photom['dec'] = host181112.coord.dec.value
        photom['VLT_g'] = 22.57
        photom['VLT_g_err'] = 0.04
        photom['VLT_I'] = 21.51
        photom['VLT_I_err'] = 0.04
        # Add in DES
        for key in host181112.photom.keys():
            photom[key] = host181112.photom[key]
        # Merge/write
        photom = frbphotom.merge_photom_tables(photom, photom_file)
        photom.write(photom_file, format=frbphotom.table_format, overwrite=True)
    host181112.parse_photom(Table.read(photom_file, format=frbphotom.table_format))

    # Nebular lines
    host181112.parse_ppxf(os.path.join(db_path, 'CRAFT', 'Prochaska2019', 'HG181112_FORS2_ppxf.ecsv'))

    # Adjust errors on Ha, [NII] because of telluric

    # Derived quantities
    host181112.calc_nebular_AV('Ha/Hb', min_AV=0.)

    # Ha is tough in telluric
    host181112.calc_nebular_SFR('Hb', AV=0.15)  # Photometric
    # This would be an upper limit
    #host.calc_nebular_SFR('Ha')

    # CIGALE
    host181112.parse_cigale(os.path.join(db_path, 'CRAFT', 'Prochaska2019', 'HG181112_CIGALE.fits'))

    # Write
    path = resource_filename('frb', 'data/Galaxies/{}'.format(frbname))
    host181112.write_to_json(path=path)


def build_host_190102(run_ppxf=False, build_photom=False):
    """ Build the host galaxy data for FRB 190102

    All of the data comes from Bhandrari+2020, ApJL, in press

    Args:
        build_photom (bool, optional):
    """
    frbname = '190102'
    # Stuart on June 17, 2019
    #  -- Astrometry.net !
    gal_coord = SkyCoord('J212939.60-792832.4',
                         unit=(units.hourangle, units.deg))  # Cherie;  07-Mar-2019
    # Instantiate
    host190102 = frbgalaxy.FRBHost(gal_coord.ra.value, gal_coord.dec.value, frbname)

    # Redshift -- Gaussian fit to [OIII 5007] in MagE
    #  Looks great on the other lines
    #  Ok on FORS2 Halpha
    wv_oiii = 6466.48
    z_OIII = wv_oiii / 5008.239 - 1
    host190102.set_z(z_OIII, 'spec')

    photom_file = os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'bhandari2019_photom.ascii')
    # VLT/FORS2 -- Pulled from draft on 2019-06-23
    # VLT/FORS2 -- Pulled from spreadsheet 2019-06-23
    if build_photom:
        photom = Table()
        photom['ra'] = [host190102.coord.ra.value]
        photom['dec'] = host190102.coord.dec.value
        photom['Name'] = host190102.name
        photom['VLT_u'] = 23.   # Dust corrected
        photom['VLT_u_err'] = -999.
        photom['VLT_g'] = 21.8  # Dust corrected
        photom['VLT_g_err'] = 0.1
        photom['VLT_I'] = 20.71 # Dust corrected
        photom['VLT_I_err'] = 0.05
        photom['VLT_z'] = 20.5 # Dust corrected
        photom['VLT_z_err'] = 0.2
        # Write
        photom = frbphotom.merge_photom_tables(photom, photom_file)
        photom.write(photom_file, format=frbphotom.table_format, overwrite=True)
    host190102.parse_photom(Table.read(photom_file, format=frbphotom.table_format))

    # PPXF
    if run_ppxf:
        # MagE
        results_file = os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'HG190102_MagE_ppxf.ecsv')
        spec_fit = os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'HG190102_MagE_ppxf.fits')
        meta, spectrum = host190102.get_metaspec(instr='MagE')
        R = meta['R']
        # Correct for Galactic extinction
        ebv = float(nebular.get_ebv(host190102.coord)['meanValue'])
        AV = ebv * 3.1  # RV
        #alAV = nebular.load_extinction('MW')
        #Al = alAV(spectrum.wavelength.value) * AV
        Al = extinction.ccm89(spectrum.wavelength.value, AV, 3.1)
        # New spec
        new_flux = spectrum.flux * 10**(Al/2.5)
        new_sig = spectrum.sig * 10**(Al/2.5)
        new_spec = XSpectrum1D.from_tuple((spectrum.wavelength, new_flux, new_sig))
        # Mask
        atmos = [(7550, 7750)]
        ppxf.run(new_spec, R, host190102.z, results_file=results_file, spec_fit=spec_fit, chk=True, atmos=atmos)
    host190102.parse_ppxf(os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'HG190102_MagE_ppxf.ecsv'))

    # Derived quantities

    # AV
    host190102.calc_nebular_AV('Ha/Hb')

    # SFR
    host190102.calc_nebular_SFR('Ha')

    # CIGALE
    host190102.parse_cigale(os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'HG190102_CIGALE.fits'))

    # Vet all
    host190102.vet_all()

    # Write -- BUT DO NOT ADD TO REPO (YET)
    path = resource_filename('frb', 'data/Galaxies/{}'.format(frbname))
    host190102.write_to_json(path=path)


def build_host_190523(build_photom=False):  #:run_ppxf=False, build_photom=False):
    """
    Build the host galaxy data for FRB 190523

    Most of the data is from Ravi+2019
        https://ui.adsabs.harvard.edu/abs/2019Natur.572..352R/abstract

    The exception is that CRAFT (S. Simha) have run CIGALE on the photometry for
    a consistent analysis with the ASKAP hosts.


    Args:
        build_photom:

    Returns:

    """
    frbname = '190523'
    gal_coord = SkyCoord(ra=207.06433, dec=72.470756, unit='deg')

    # Instantiate
    host190523 = frbgalaxy.FRBHost(gal_coord.ra.value, gal_coord.dec.value, frbname)

    # Load redshift table
    host190523.set_z(0.660, 'spec')

    # Morphology

    # Photometry

    # PanStarrs
    # Grab the table (requires internet)
    photom_file = os.path.join(db_path, 'DSA', 'Ravi2019', 'ravi2019_photom.ascii')
    if build_photom:
        search_r = 1 * units.arcsec
        ps_srvy = panstarrs.Pan_STARRS_Survey(gal_coord, search_r)
        ps_tbl = ps_srvy.get_catalog(print_query=True)
        photom = frbphotom.merge_photom_tables(ps_tbl, photom_file)
        photom.write(photom_file, format=frbphotom.table_format, overwrite=True)
    # Parse
    host190523.parse_photom(Table.read(photom_file, format=frbphotom.table_format))

    # PPXF
    '''
    if run_ppxf:
        results_file = os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'HG190608_SDSS_ppxf.ecsv')
        meta, spectrum = host190608.get_metaspec(instr='SDSS')
        spec_fit = None
        ppxf.run(spectrum, 2000., host190608.z, results_file=results_file, spec_fit=spec_fit, chk=True)
    host190608.parse_ppxf(os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'HG190608_SDSS_ppxf.ecsv'))
    '''

    # CIGALE -- PanStarrs photometry but our own CIGALE analysis
    host190523.parse_cigale(os.path.join(db_path, 'DSA', 'Ravi2019',
                                         'S1_190523_CIGALE.fits'))

    # Derived quantities
    host190523.derived['SFR_nebular'] = 1.3
    host190523.derived['SFR_nebular_err'] = -999.

    # Vet all
    host190523.vet_all()

    # Write -- BUT DO NOT ADD TO REPO (YET)
    path = resource_filename('frb', 'data/Galaxies/{}'.format(frbname))
    host190523.write_to_json(path=path)


def build_host_190608(run_ppxf=False, build_photom=False):
    """ Build the host galaxy data for FRB 190608

    All of the data comes from Bhandrari+2020, ApJL, in press

    Args:
        build_photom (bool, optional):
    """
    frbname = '190608'
    gal_coord = SkyCoord('J221604.90-075356.0',
                         unit=(units.hourangle, units.deg))  # Cherie;  07-Mar-2019

    # Instantiate
    host190608 = frbgalaxy.FRBHost(gal_coord.ra.value, gal_coord.dec.value, frbname)

    # Load redshift table
    ztbl = Table.read(os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'z_SDSS.ascii'),
                      format='ascii.fixed_width')
    z_coord = SkyCoord(ra=ztbl['RA'], dec=ztbl['DEC'], unit='deg')
    idx, d2d, _ = match_coordinates_sky(gal_coord, z_coord, nthneighbor=1)
    if np.min(d2d) > 0.5*units.arcsec:
        embed(header='190608')
    # Redshift -- SDSS
    host190608.set_z(ztbl[idx]['ZEM'], 'spec')

    # Morphology
    #host190608.parse_galfit(os.path.join(photom_path, 'CRAFT', 'Bannister2019',
    #                               'HG180924_galfit_DES.log'), 0.263)

    # Photometry

    # SDSS
    # Grab the table (requires internet)
    photom_file = os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'bhandari2019_photom.ascii')
    if build_photom:
        # VLT
        search_r = 1 * units.arcsec
        # SDSS
        sdss_srvy = sdss.SDSS_Survey(gal_coord, search_r)
        sdss_tbl = sdss_srvy.get_catalog(print_query=True)
        sdss_tbl['Name'] = 'HG190608'
        photom = frbphotom.merge_photom_tables(sdss_tbl, photom_file)
        # WISE
        wise_srvy = wise.WISE_Survey(gal_coord, search_r)
        wise_tbl = wise_srvy.get_catalog(print_query=True)
        wise_tbl['Name'] = 'HG190608'
        # Write
        photom = frbphotom.merge_photom_tables(wise_tbl, photom, debug=True)
        photom.write(photom_file, format=frbphotom.table_format, overwrite=True)
    # Parse
    host190608.parse_photom(Table.read(photom_file, format=frbphotom.table_format))

    # PPXF
    results_file = os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'HG190608_SDSS_ppxf.ecsv')
    if run_ppxf:
        meta, spectrum = host190608.get_metaspec(instr='SDSS')
        spec_fit = None
        ppxf.run(spectrum, 2000., host190608.z, results_file=results_file, spec_fit=spec_fit, chk=True)
    host190608.parse_ppxf(results_file)

    # Derived quantities

    # AV
    host190608.calc_nebular_AV('Ha/Hb')

    # SFR
    host190608.calc_nebular_SFR('Ha')
    #host.derived['SFR_nebular_err'] = -999.

    # CIGALE
    host190608.parse_cigale(os.path.join(db_path, 'CRAFT', 'Bhandari2019',
                                         'HG190608_CIGALE.fits'))
    # Vet all
    host190608.vet_all()

    # Write
    path = resource_filename('frb', 'data/Galaxies/{}'.format(frbname))
    host190608.write_to_json(path=path)


def build_host_180916(run_ppxf=False, build_photom=False, build_cigale=False):
    """ Build the host galaxy data for FRB 180916

    All of the data currently comes from Marcote et al. 2020
    https://ui.adsabs.harvard.edu/abs/2020Natur.577..190M/abstract

    CIGALE will be published in Kasper et al. 2020

    Args:
        build_photom (bool, optional):
    """
    frbname = '180916'
    gal_coord = SkyCoord('J015800.28+654253.0',
                         unit=(units.hourangle, units.deg))

    # Instantiate
    host180916 = frbgalaxy.FRBHost(gal_coord.ra.value, gal_coord.dec.value, frbname)

    # Load redshift table
    #ztbl = Table.read(os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'z_SDSS.ascii'),
    #                  format='ascii.fixed_width')
    #z_coord = SkyCoord(ra=ztbl['RA'], dec=ztbl['DEC'], unit='deg')
    #idx, d2d, _ = match_coordinates_sky(gal_coord, z_coord, nthneighbor=1)
    #if np.min(d2d) > 0.5*units.arcsec:
    #    embed(header='190608')
    # Redshift -- SDSS
    #host180916.set_z(ztbl[idx]['ZEM'], 'spec')

    # Redshift
    host180916.set_z(0.0337, 'spec')

    # Morphology
    #host190608.parse_galfit(os.path.join(photom_path, 'CRAFT', 'Bannister2019',
    #                               'HG180924_galfit_DES.log'), 0.263)

    # Photometry
    EBV = nebular.get_ebv(gal_coord)['meanValue']  #
    print("EBV={} for the host of {}".format(EBV, frbname))

    # SDSS
    # Grab the table (requires internet)
    photom_file = os.path.join(db_path, 'CHIME', 'Marcote2020', 'marcote2020_photom.ascii')
    if build_photom:
        # SDSS
        search_r = 1 * units.arcsec
        sdss_srvy = sdss.SDSS_Survey(gal_coord, search_r)
        sdss_tbl = sdss_srvy.get_catalog(print_query=True)
        sdss_tbl['Name'] = host180916.name
        photom = frbphotom.merge_photom_tables(sdss_tbl, photom_file)
        # WISE
        wise_srvy = wise.WISE_Survey(gal_coord, search_r)
        wise_tbl = wise_srvy.get_catalog(print_query=True)
        wise_tbl['Name'] = host180916.name
        photom = frbphotom.merge_photom_tables(wise_tbl, photom, debug=True)
        # Write
        photom.write(photom_file, format=frbphotom.table_format, overwrite=True)
    # Parse
    photom = Table.read(photom_file, format=frbphotom.table_format)
    # Dust correction
    frbphotom.correct_photom_table(photom, EBV)
    # Parse
    host180916.parse_photom(photom)

    # CIGALE
    cigale_file = os.path.join(db_path, 'CHIME', 'Marcote2020', 'HG180619_CIGALE.fits')
    if build_cigale:
        cut_photom = photom.copy()
        # Remove WISE
        #for column in cut_photom.keys():
        #    if 'WISE' in column:
        #        cut_photom.remove_column(column)
        # Run
        cigale.host_run(cut_photom, host180916, cigale_file=cigale_file)

    host180916.parse_cigale(cigale_file)

    # PPXF
    #results_file = os.path.join(db_path, 'CRAFT', 'Bhandari2019', 'HG190608_SDSS_ppxf.ecsv')
    #if run_ppxf:
    #    meta, spectrum = host190608.get_metaspec(instr='SDSS')
    #    spec_fit = None
    #    ppxf.run(spectrum, 2000., host190608.z, results_file=results_file, spec_fit=spec_fit, chk=True)
    #host190608.parse_ppxf(results_file)

    # Derived quantities

    # AV
    #host190608.calc_nebular_AV('Ha/Hb')

    # SFR
    #host190608.calc_nebular_SFR('Ha')
    #host.derived['SFR_nebular_err'] = -999.

    # Vet all
    host180916.vet_all()

    # Write -- BUT DO NOT ADD TO REPO (YET)
    path = resource_filename('frb', 'data/Galaxies/{}'.format(frbname))
    host180916.write_to_json(path=path)


def main(inflg='all', options=None):
    # Options
    build_photom, build_cigale = False, False
    if options is not None:
        if 'photom' in options:
            build_photom = True
        if 'cigale' in options:
            build_cigale = True

    if inflg == 'all':
        flg = np.sum(np.array( [2**ii for ii in range(25)]))
    else:
        flg = int(inflg)

    # 121102
    if flg & (2**0):
        build_host_121102(build_photom=build_photom) # 1

    # 180924
    if flg & (2**1):
        build_host_180924(build_photom=build_photom)

    # 181112
    if flg & (2**2):
        build_host_181112(build_photom=build_photom)

    # 190523
    if flg & (2**3):
        build_host_190523(build_photom=build_photom)

    # 190608
    if flg & (2**4):
        build_host_190608(build_photom=build_photom)#, run_ppxf=True)

    # 190102
    if flg & (2**5):
        build_host_190102(build_photom=build_photom)

    # 180916
    if flg & (2**6):  # 64
        build_host_180916(build_photom=build_photom, build_cigale=build_cigale)


# Command line execution
if __name__ == '__main__':
    pass

