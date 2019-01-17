# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
import re
from pygments.lexer import *
from pygments.token import *


class CSSLexer(RegexLexer):
    name = "CSS"
    aliases = ['css']
    filenames = ['*.css']
    flags = re.DOTALL

    tokens = {
        b"root": [
            (r"", Text, b"rules"),
        ],
        b"comment": [
            (r"\*/", Comment, b"#pop"),
            (r".", Comment)
        ],
        b"at-rule": [
            include(b"values"),
            (r";", Punctuation, b"#pop"),
            (r"{\s*}", Punctuation, b"#pop"),
            (r"{(?=[^;}]*{)", Punctuation, (b"#pop", b"rules")),
            (r"{(?=[^{}]*;)", Punctuation, (b"#pop", b"decls")),
            (r"", Text, b"#pop")
        ],
        b"rules": [
            (r"/\*", Comment, b"comment"),
            (r"\s+", Text),
            (r"@[\w-]+", Name, b"at-rule"),
            (r"}", Punctuation, b"#pop"),
            (r"([^{]+)({)", bygroups(Name.Tag, Punctuation), b"decls"),
        ],
        b"decls": [
            (r";", Punctuation),
            (r"@[\w-]+", Name, b"at-rule"),
            (r"([\w-]+)\s*(:)", bygroups(Keyword, Punctuation)),
            include(b"values"),
            (r"}", Punctuation, b"#pop"),
            (r".+", Text)
        ],
        b"values": [
            (r"/\*", Comment, b"comment"),
            (r"[(),/]", Punctuation),
            (r"([+-]?(?:\d+(?:\.\d+)?|\d*\.\d+)[eE][+-]?(?:\d+(?:\.\d+)?|\d*\.\d+))([a-zA-Z-]+|%)", bygroups(Literal.Number, Literal)),
            (r"[+-]?(?:\d+(?:\.\d+)?|\d*\.\d+)[eE][+-]?(?:\d+(?:\.\d+)?|\d*\.\d+)", Literal.Number),
            (r"([+-]?(?:\d+(?:\.\d+)?|\d*\.\d+))([a-zA-Z-]+|%)", bygroups(Literal.Number, Literal)),
            (r"[+-]?(?:\d+(?:\.\d+)?|\d*\.\d+)", Literal.Number),
            (r"(url)(\()([^)]*)(\))", bygroups(Name.Function, Punctuation, Literal.String, Punctuation)),
            (r"([\w-]+)(\()", bygroups(Name.Function, Punctuation)),
            (r"\"[^\"]*\"", Literal.String),
            (r"'[^']*'", Literal.String),
            (r"#?[\w-]+", Text),
            (r"\s+", Text)
        ]
    }


def applyLexerExtensions(lexer, md):
    extraRules = []
    for entry in md.extraPygments:
        # TODO this is a potential security vulnerability when running bikeshed on a public server...
        # TODO handle errors
        entryDict = eval(entry)
        #if type(entryDict) is not dict:
        #    die("Extra Pygments Rules metadata should have the form: 'state' : (regex, actions...)")
        extraRules.append(entryDict)
    tokens = dict()
    for ruleDict in extraRules:
        for state, rule in ruleDict.items():
            if state == b"<all>":
                for baseState, rules in type(lexer).tokens.items():
                    if baseState not in tokens:
                        tokens[baseState] = []
                    tokens[baseState].append(rule)
            else:
                if state not in tokens:
                    tokens[state] = []
                tokens[state].append(rule)
    for rules in tokens.values():
        rules.append(inherit)
    newLexerType = type(b"CustomLexer", (type(lexer),), {b"tokens": tokens})
    return newLexerType()
