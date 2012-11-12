
def sj_run(self, lang, source):
    stdout, stderr, exitstatus, runtime, error = wrapper.run(lang, source, "",
            timelimit=1.0)
    return (exitstatus, error)

def testCompilerProfileErrors(language, webapp):
    assert wrapper.enabled_languages["c"][ "execution_profile"].__class__.__name__ == "CompilerProfile"
    assert self.sj_run("c",
            "int main(int argc, char** argv) { return 0; }"), (0, ""))
    assert self.sj_run("c",
            "(int argc, char** argv) { }"), (1, "compilation_error"))
    assert self.sj_run("c",
            "int main(int argc, char** argv) { return 1; }"), (1, "runtime_error"))
    assert self.sj_run("c",
            "#include <time.h>\nint main(int argc, char** argv) { "
            "sleep(20); return 0; }"), (-9, "runtime_timelimit"))

def testInterpreterProfileErrors(language, webapp):
    assert wrapper.enabled_languages["python"][
            "execution_profile"].__class__.__name__, "InterpreterProfile")
    assert self.sj_run("python",
            "print 'hi'\n"), (0, ""))
    assert self.sj_run("python",
            "raise 'error'\n"), (1, "runtime_error"))
    assert self.sj_run("python",
            "import time\ntime.sleep(20)"), (-9, "runtime_timelimit"))

def testVMProfileErrors(language, webapp):
    assert wrapper.enabled_languages["java"][
            "execution_profile"].__class__.__name__, "VMProfile")
    assert self.sj_run("java",
            "class Main { public static void main(String[] args) { } }"), (0, ""))
    assert self.sj_run("java",
            "object extends { 0 }"), (1, "compilation_error"))
    assert self.sj_run("java",
            "class Main { public static void main(String[] args) throws Exception "
            "{ throw new Exception(); } }"), (1, "runtime_error"))
    assert self.sj_run("java",
            "class Main { public static void main(String[] args) throws Exception "
            "{ Thread.sleep(20000); } }"), (-9, "runtime_timelimit"))
