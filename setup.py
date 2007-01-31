from distutils.core import setup,Extension
setup(name='hermod',
        version='1.1.0',
        package_dir={'hermod': ''},
        packages=['hermod', 'hermod.l1b','hermod.l2','hermod.pdc'],
        description = 'Routines to simplify and improve speed of odinprocessing',
        author='Joakim Möller',
        author_email='joakim.moller@chalmers.se',
        url='http://diamond.rss.chamers.se',
        scripts=['scripts/insertFiles','scripts/readFreq','scripts/rerunOrbits','scripts/getL1bFiles','scripts/getL1b'],
        ext_modules = [
        Extension('hermod.l1b.ReadHDF', 
            ['l1b/readhdfmodule.c'], 
            libraries = ['mfhdf','df','jpeg','z'] 
            ) 
        ] 
        )

