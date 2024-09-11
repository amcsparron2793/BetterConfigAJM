"""
BetterConfigAJM.py

More streamlined ConfigParser with fewer options available. Inherits from ConfigParser

"""

import configparser
from os import mkdir
from os.path import isfile, join, isdir

from typing import List
# TYPE_CHECKING is always false at runtime (why remains a mystery?),
# so if TYPE_CHECKING import XXXX won't actually be imported. Having the Logger type hint below
# in single quotes allows type hinting without importing. This is also good for preventing circular imports
from logging import Logger
from pathlib import Path

class BetterConfigAJM(configparser.ConfigParser):
    def __init__(self, config_filename, config_dir, config_list_dict: List[dict] = None, logger: Logger = None):
        super().__init__()
        if logger:
            self._logger = logger
        else:
            self._logger = Logger("DUMMY_LOGGER")

        self.config_list_dict = config_list_dict
        self.config_filename = config_filename
        self.config_dir = config_dir
        self.config_location = join(config_dir, config_filename).replace('\\', '/')

        if type(self) != BetterConfigAJM:
            self.post_init()

    def post_init(self):
        """ TODO: will this work?

        BaseClass Initialization:
            In the __init__ method of BaseClass, a type check is performed using type(self) is not BaseClass.
            Conditional Execution:
            If the instance being created is not of type BaseClass (i.e., it is a subclass), the post_init method is called.
            post_init is defined as a method that should be implemented by subclasses, throwing a NotImplementedError if it isn't.
        :return:
        """
        if (not hasattr(self, 'config_list_dict')
                or self.__getattr__(self, 'config_list_dict') is None):
            self.config_list_dict = self.default_config
        # making this resolve to an absolute path
        self.config_location = Path(self.config_location).resolve()

    def _read_config(self):
        if isfile(self.config_location):
            try:
                self.read(self.config_location)
                self._logger.info(f"config successfully read from {self.config_location}")
            except configparser.Error as e:
                self._logger.error(e, exc_info=True)
                raise e
        else:
            try:
                raise FileNotFoundError(f"Could not find config file {self.config_location}")
            except FileNotFoundError as e:
                self._logger.error(e, exc_info=True)
                raise e

    def _write_config(self):  # , config_list_dict: List[dict]):
        def _file_io(location):
            with open(location, 'w') as f:
                self.write(f)
            self._logger.info(f'Config written to {location}.')
            return location

        if isdir(self.config_dir):
            self._logger.debug(f"config directory ({self.config_dir}) found")
            pass
        else:
            mkdir(self.config_dir)
            self._logger.debug(f"config directory ({self.config_dir}) created")

        if not isfile(self.config_location):
            try:
                self['DEFAULT'] = self.config_list_dict[0]['DEFAULT']
            except KeyError:
                try:
                    raise KeyError("DEFAULT key must always be first in the config_list_dict")
                except KeyError as e:
                    self._logger.error(e, exc_info=True)
                    raise e
                except AttributeError as e:
                    self._logger.error(e, exc_info=True)
                    raise e
            for i in self.config_list_dict:
                for key, value in i.items():
                    if key != 'DEFAULT':
                        self[key] = value
            # then write the config to a file
            _file_io(self.config_location)
        else:
            self._logger.info(f"config file \'{self.config_location}\' detected")

    def GetConfig(self):
        """
        get_config() either builds a .ini config file from a given list_dict
        (self.config_list_dict) OR reads it from a given path (self.config_location).
        """
        # if a config location is given and the file exists, then read from it
        if self.config_location and isfile(self.config_location):
            self._logger.info("Given config location exists, attempting read.")
            self._read_config()
        # if a config list dict AND a config location are given,
        # then write it to the given location, and read it back into a variable
        elif self.config_list_dict is not None and self.config_location is not None:
            self._logger.info("list dict AND config_location given, attempting to write ListDict to location")
            self._write_config()
            self._logger.info("Reading config back into variable...")
            self._read_config()
        # if a config location is not given, but a config list dict IS,
        # then write it to the default location, and read it back into a variable
        elif self.config_location is None and self.config_list_dict is not None:
            # TODO: deprecated, should be deleted?
            self._write_config()
            self._read_config()
        else:
            raise AttributeError("GetConfig requires either "
                                 "a valid config location, "
                                 "or a list_dict of configuration params")
        return self
