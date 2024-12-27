import ctypes
import os

from .utils import get_dependency_filename

# Get the absolute path to the directory containing this file.
root_dir = os.path.abspath(os.path.dirname(__file__))

# Construct the full path to the dependency library file.
# get_dependency_filename() is assumed to return a platform-specific filename (e.g., libclient.so, client.dll).
library_path = f'{root_dir}/dependencies/{get_dependency_filename()}'

# Load the shared library.  ctypes.cdll.LoadLibrary loads the shared library at the specified path.
library = ctypes.cdll.LoadLibrary(library_path)

# Define the argument and return types for the 'request' function.
# This is crucial for proper interaction with the C/C++ library.
# argtypes specifies the expected argument types for the function.  Here it's a char pointer (string).
# restype specifies the return type of the function.  Here it's also a char pointer (string).
# https://bogdanfinn.gitbook.io/open-source-oasis/shared-library/exposed-methods
request = library.request
request.argtypes = [ctypes.c_char_p] # Expects a string as input
request.restype = ctypes.c_char_p  # Returns a string

# Define the argument and return types for the 'getCookiesFromSession' function.
# Similar to 'request', this function takes a string and returns a string.
getCookiesFromSession = library.getCookiesFromSession
getCookiesFromSession.argtypes = [ctypes.c_char_p] # Expects a string (session ID) as input
getCookiesFromSession.restype = ctypes.c_char_p  # Returns a string (cookies)

# Define the argument and return types for the 'addCookiesToSession' function.
# This function takes a string (presumably cookies) and returns a string (possibly a status indicator).
addCookiesToSession = library.addCookiesToSession
addCookiesToSession.argtypes = [ctypes.c_char_p] # Expects a string (cookies) as input
addCookiesToSession.restype = ctypes.c_char_p  # Returns a string

# Define the argument and return types for the 'freeMemory' function.
# This function presumably takes a pointer to memory allocated by the library and frees it.
freeMemory = library.freeMemory
freeMemory.argtypes = [ctypes.c_char_p] # Expects a char pointer (to be freed)
freeMemory.restype = ctypes.c_char_p  # Returns a string (potentially a status/confirmation)

# Define the argument and return types for the 'destroySession' function.
# This function takes a string (presumably a session ID) and returns a string (likely a status indicator).
destroySession = library.destroySession
destroySession.argtypes = [ctypes.c_char_p] # Expects a string (session ID) as input
destroySession.restype = ctypes.c_char_p  # Returns a string

# Define the return type for the 'destroyAll' function.
# This function takes no arguments and returns a string.
destroyAll = library.destroyAll
destroyAll.restype = ctypes.c_char_p  # Returns a string