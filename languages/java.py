from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

java = Language('Java',
    profile                     = exec_profiles.VMProfile(straitjacket_settings),
    version_switch              = '-version',
    binary                      = 'javac',
    compilation_command         = lambda source: ['env', 'JAVA_TOOL_OPTIONS=-Xmx256m -Xms256m -Xss256k', 'javac', 'Main.java'],
    vm_command                  = lambda source: ['java', '-Xmx256m', '-Xms256m', '-Xss256k', 'Main'],
    filename                    = 'Main.java',
    compiler_apparmor_profile   = 'straitjacket/compiler/java',
    vm_apparmor_profile         = 'straitjacket/compiled/java')

LanguageTest('test-simple', java,
    source      = ( 'public class Main {                                         \n'
                    'public static void main(String[] args) {                    \n'
                    'System.out.println("Hello from Java");                      \n'
                    '}                                                           \n'
                    '}                                                           \n'
                  ),
    stdout      = 'Hello from Java\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', java,
    source      = ( 'import java.io.*;                                           \n'
                    'public class Main {                                         \n'
                    'public static void main(String[] args) {                    \n'
                    'try {                                                       \n'
                    'DataInputStream in = new DataInputStream(                   \n'
                    'new FileInputStream("/etc/hosts"));                         \n'
                    'BufferedReader br = new BufferedReader(new InputStreamReader(in));\n'
                    'String line;                                                \n'
                    'while ((line = br.readLine()) != null) {                    \n'
                    'System.out.println(line);                                   \n'
                    '}                                                           \n'
                    'in.close();                                                 \n'
                    '} catch (Exception e) {                                     \n'
                    'System.err.println("SJ Error: " + e.getMessage());          \n'
                    '}                                                           \n'
                    '}                                                           \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = 'SJ Error: /etc/hosts \(Permission denied\)\n',
    returncode  = 0)

LanguageTest('test-rlimit', java,
    source      = ( 'public class Main {                                         \n'
                    'public static void main(String[] args) {                    \n'
                    'int[] data = new int[1073741824];                           \n'
                    '}                                                           \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = 'Exception in thread "main" java.lang.OutOfMemoryError',
    returncode  = 1)

