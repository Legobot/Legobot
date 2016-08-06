from setuptools import setup, find_packages

setup(
    name='Legobot',

    version='0.2.1',

    py_modules=['Legobot'],

    description="A flexible platform for easily creating interactive IRC bots",

    author="Kevin McCabe and Bren Briggs",

    url="https://github.com/bbriggs/Legobot",

    classifiers=[
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(exclude=['contrib', 'docs']),

    #install_requires=['socket','select','string','ssl','threading','Queue','datetime','time','random'],
)
