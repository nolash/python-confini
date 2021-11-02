def to_constant_name(directive, section):
    return '{}_{}'.format(section.upper(), directive.upper())
