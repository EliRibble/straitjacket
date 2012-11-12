from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

scala = Language('Scala',
    profile                     = exec_profiles.VMProfile(straitjacket_settings),
    version_switch              = '-version',
    binary                      = 'scalac',
    vm_command                  = lambda source: ['scala', 'Main'],
    filename                    = 'source.scala',
    compiler_apparmor_profile   = 'straitjacket/compiler/scala',
    vm_apparmor_profile         = 'straitjacket/compiled/scala',
    compiler_timeout            = 40)

LanguageTest('test-simple', scala,
    source      = ( 'object Main {                                               \n'
                    'def main(args: Array[String]) {                             \n'
                    'println("Hello from Scala")                                 \n'
                    '}                                                           \n'
                    '}                                                           \n'
                  ),
    stdout      = 'Hello from Scala\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', scala,
    source      = ( 'import scala.io._                                           \n'
                    'object Main {                                               \n'
                    'def main(args: Array[String]) {                             \n'
                    'val s = Source.fromFile("/etc/hosts")                       \n'
                    's.getLines.foreach( (line) => {                             \n'
                    'println(line.trim)                                          \n'
                    '})                                                          \n'
                    '}                                                           \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = 'java.io.FileNotFoundException: /etc/hosts \(Permission denied\)',
    returncode  = 0)

LanguageTest('test-rlimit', scala,
    source      = ( 'object Main {                                               \n'
                    'def main(args: Array[String]) {                             \n'
                    'val data = new Array[String](1073741824)                    \n'
                    'data                                                        \n'
                    '}                                                           \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = 'java.lang.OutOfMemoryError: Java heap space\n',
    returncode  = 0)

LanguageTest('test-application-trait', scala,
    source      = ( 'object Main extends Application {                           \n'
                    'println("hello from scala")                                 \n'
                    '}                                                           \n'
                  ),
    stdout      = 'hello from scala\n',
    stderr      = '',
    returncode  = 0)

