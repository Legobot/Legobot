from setuptools import setup, find_packages

setup(
    name='Legobot',

    version='1.0.3dev1',

    license='GPLv2',

    py_modules=['Legobot'],

    description="A framework for creating interactive chatbots on various"
    "protocols",

    author="Kevin McCabe, Bren Briggs, and Drew Bronson",

    url="https://github.com/bbriggs/Legobot",

    classifiers=[
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3'
    ],

    packages=find_packages(exclude=['contrib', 'docs']),

    install_requires=['pykka', 'irc'],
)
