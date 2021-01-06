import os
from pathlib import Path

from conans import CMake, ConanFile, tools


class QtBreezeIconsConan(ConanFile):
    name = 'ECM'
    # KDE stable version
    kde_stable_version = '5.77.0'
    license = 'LGPL-2.1-only'
    description = 'Conan recipe for KDE Extra CMake Modules'
    url = 'https://github.com/DragoonBoots/conan-ECM'
    topics = ["CMake"]
    exports = ('version.txt',)
    no_copy_source = True

    def set_version(self):
        version_file_path = Path(self.recipe_folder) / 'version.txt'
        if version_file_path.is_file():
            with version_file_path.open(mode='rt') as version_file:
                self.version = version_file.readline().strip()
        else:
            self.version = self.kde_stable_version

    def source(self):
        git = tools.Git()
        git.clone('https://invent.kde.org/frameworks/extra-cmake-modules.git', branch='v{}'.format(self.version),
                  shallow=True)

    def _configure_cmake(self) -> CMake:
        cmake = CMake(self)
        # This will create generated icons (e.g. 24x24 versions)
        cmake.definitions['SKIP_LICENSE_TESTS'] = True
        cmake.definitions['BUILD_HTML_DOCS'] = False
        cmake.definitions['BUILD_MAN_DOCS'] = False
        cmake.definitions['BUILD_QTHELP_DOCS'] = False
        cmake.definitions['BUILD_TESTING'] = False
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.resdirs = ['share']
        self.cpp_info.build_modules = ['share/ECM/cmake']

    def package_id(self):
        self.info.header_only()
