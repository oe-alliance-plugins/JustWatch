from setuptools import setup
import setup_translate

pkg = 'Extensions.JustWatch'
setup(name='enigma2-plugin-extensions-justwatch',
       version='3.0',
       description='JustWatch streaming search for Enigma2',
       package_dir={pkg: 'JustWatch'},
       packages=[pkg],
       package_data={pkg: ['images/search/1920/*.png', 'images/search/1280/*.png', 'images/country/*.png', 'images/spinner/*.png', 'images/*.png', '*.png', '*.xml', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass=setup_translate.cmdclass,  # for translation
      )
