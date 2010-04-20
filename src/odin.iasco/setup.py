from setuptools import setup,find_packages

setup(
        name="odin.iasco",
        version="1.0.2",
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
        install_requires=['setuptools','numpy','matplotlib',
		#'basemap',
		'pymatlab',
		'mocker'],
        tests_require='mocker',
        test_suite="tests",
        eager_resources=['matlab/IASCO.m','matlab/MakeWinds.m','matlab/SMR_501hdf_read.m','matlab/SMR_544hdf_read.m','matlab/assimilateG.m','matlab/define_assgridG.m','matlab/readecmwfmult.m','matlab/Tools/mjd2utc.m','matlab/Tools/read_l2_smr.m','matlab/Tools/utc2mjd.m']
        )

