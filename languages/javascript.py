from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

javascript = Language('Javascript',
    profile             = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary              = 'node',
    filename            = 'source.js',
    apparmor_profile    = 'straitjacket/interpreter/node')

LanguageTest('test-simple', javascript,
    source      = ( 'function test() { console.log("hello js"); };               \n'
                    'test();                                                     \n'
                  ),
    stdout      = 'hello js\n',
    stderr      = '',
    returncode  = 0,
    error       = None)

LanguageTest('test-apparmor', javascript,
    source      = ( 'var fs = require("fs");                                     \n'
                    'fs.readFile("/etc/hosts", function (err, data) {            \n'
                    'if (err) throw err;                                         \n'
                    'console.log(data.toString());                               \n'
                    '});                                                         \n'
                  ),
    stdout      = '',
    stderr      = "Error: EACCES, open '/etc/hosts'",
    returncode  = 1,
    error       = 'runtime_error')

LanguageTest('test-rlimit', javascript,
    source      = ( 'var buffer1 = new Buffer(536870912);                        \n'
                    'var buffer2 = new Buffer(536870912);                        \n'
                    'var buffer3 = new Buffer(536870912);                        \n'
                    'console.log(buffer1.length + buffer2.length + buffer3.length);\n'
                  ),
    stdout      = '',
    stderr      = "terminate called after throwing an instance of 'std::bad_alloc'",
    returncode  = -6,
    error       = 'runtime_error')

