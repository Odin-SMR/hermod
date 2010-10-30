from setuptools import setup,find_packages

setup(
        name="odin.iasco",
        version="1.0.4",
        description = 'Package for processing images with IASCO. Includes processing of wind and odin data, images and updates of databases and the odin homepage',
	package_data= {'':['matlab/*.m','matlab/*.mat'],},
        entry_points= {"console_scripts": 
                       ["blackbox_run = odin.iasco.blackbox_main:main", 
                        "mark_db = odin.iasco.mark_iasco_db:main",
                        "addlevel3 = odin.iasco.addlevel3:main"]},
        packages = find_packages(),
        namespace_packages = ['odin'],
        zip_safe=False,
        author='Marcus Jansson, Erik Zakrisson',
        author_email='marcus.jansson@chalmers.se, erik.zakrisson@chalmers.se',
        url='http://odin.rss.chalmers.se',
        install_requires=[
            'setuptools',
            'numpy>=1.3.0',
            'matplotlib>=0.99.1',
		    'basemap>=0.99',
		    'pymatlab==0.1.3',
            'scipy>=0.6.0',
		],
        tests_require='mocker',
        test_suite="odin.iasco.tests.alltests.test_suite",
        eager_resources=['matlab/IASCO.m','matlab/MakeWinds.m','matlab/SMR_501hdf_read.m','matlab/SMR_544hdf_read.m','matlab/assimilateG.m','matlab/define_assgridG.m','matlab/readecmwfmult.m','matlab/Tools/mjd2utc.m','matlab/Tools/read_l2_smr.m','matlab/Tools/utc2mjd.m']
        )

