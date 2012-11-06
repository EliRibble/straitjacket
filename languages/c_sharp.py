from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

c_sharp = Language('C#',
    profile                     = exec_profiles.VMProfile(straitjacket_settings),
    binary                      = 'gmcs',
    filename                    = 'source.cs',
    version_switch              = '--version',
    compilation_command         = lambda source: ["mono", "/usr/lib/mono/2.0/gmcs.exe", "-out:main.exe", source],
    vm_command                  = lambda source: ['env', "LD_PRELOAD=/var/local/straitjacket/lib/getpwuid_r_hijack.so", "mono", "main.exe"],
    compiler_apparmor_profile   = 'straitjacket/compiler/csharp',
    vm_apparmor_profile         = 'straitjacket/compiled/csharp'
)
LanguageTest('test-simple', c_sharp,
    source      = ( 'public class HelloWorld {                              \n'
                    '  public static void Main() {                          \n'
                    '    System.Console.WriteLine("hey c# world, sup?");    \n'
                    '  }                                                    \n'
                    '}'),
    stdout      = r'hey c# world, sup\?\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-rlimit', c_sharp,
    source      = ( 'public class TestRLimit {                  \n'
                    '  public static void Main() {              \n'
                    '    int[] numbers = new int[1073741824];   \n'
                    '  }                                        \n'
                    '}'),
    stdout      = '',
    stderr      = 'System.OutOfMemoryException: Out of memory',
    returncode  = 1)

LanguageTest('test-apparmor', c_sharp,
    source      = ( 'using System; using System.IO;             \n'
                    'public class TestAppArmor {                \n'
                    '   public static void Main() {             \n'
                    '       TextReader tr = new StreamReader("/etc/passwd");   \n'
                    '       Console.WriteLine(tr.ReadLine());   \n'
                    '       tr.Close();                         \n'
                    '   }                                       \n'
                    '}'),
    stdout      = '',
    stderr      = 'Access to the path "/etc/passwd" is denied.',
    returncode  = 1)

