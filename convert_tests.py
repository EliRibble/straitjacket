import ConfigParser

def _get_pattern(my_config, section, pattern_name):
    pattern = my_config.get(section, pattern_name)
    if pattern.startswith('\A'): pattern = pattern[2:]
    if pattern.endswith('\Z'): pattern = pattern[:-2]
    return pattern
    
for language in ['d', 'fortran', 'go', 'guile', 'haskell', 'java', 'javascript', 'lua', 'ocaml', 'perl', 'php', 'python', 'ruby1.8', 'ruby1.9', 'scala', 'scheme']:
    my_config = ConfigParser.SafeConfigParser()
    my_config.read('./config/lang-{0}.conf'.format(language))
    new_test = ''
    for section in my_config.sections():
        if not section.startswith('test-'):
            continue
        new_test += "LanguageTest('{0}', {1},\n".format(section, language)
        new_test += "    source      = ( '{:<60}\\n'\n".format(my_config.get(section, 'source').split('\n')[0])
        for source_line in my_config.get(section, 'source').split('\n')[1:]:
            new_test += "                    '{:<60}\\n'\n".format(source_line)
        new_test += "                  )\n"
        new_test += "    stdout      = '{0}'\n".format(_get_pattern(my_config, section, 'stdout'))
        new_test += "    stderr      = '{0}'\n".format(_get_pattern(my_config, section, 'stderr'))
        new_test += "    returncode  = {0}\n".format(my_config.get(section, 'exitstatus'))

        error = my_config.get(section, 'error')
        new_test += "    error       = {0}\n".format("'" + error + "'" if error else 'None')
        new_test += "\n"
    with open('./config/{0}.py'.format(language), 'w') as f:
        f.write(new_test)
            
