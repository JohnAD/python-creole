#!/usr/bin/env python
# coding: utf-8


"""
    creole2html unittest
    ~~~~~~~~~~~~~~~~~~~~
    
    Here are only some tests witch doesn't work in the cross compare tests.
    
    Info: There exist some situations with different whitespace handling
        between creol2html and html2creole.

    Test the creole markup.

    :copyleft: 2008-2011 by python-creole team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import unittest
import StringIO

from tests.utils.base_unittest import BaseCreoleTest
from tests import test_macros

from creole import creole2html
from creole.creole2html import example_macros


class TestCreole2html(unittest.TestCase):
    """
    Tests around creole2html API and macro function.
    """
    def test_stderr(self):
        """
        Test if the traceback information send to a stderr handler.
        """
        my_stderr = StringIO.StringIO()
        creole2html(
            markup_string=u"<<notexist1>><<notexist2>><</notexist2>>",
            verbose=2, stderr=my_stderr, debug=False
        )
        error_msg = my_stderr.getvalue()

        # Check if we get a traceback information into our stderr handler
        must_have = (
            "<pre>", "</pre>",
            "Traceback",
            "AttributeError:",
            "has no attribute 'notexist1'",
            "has no attribute 'notexist2'",
        )
        for part in must_have:
            self.failUnless(
                part in error_msg,
                "String %r not found in:\n******\n%s******" % (part, error_msg)
            )

    def test_example_macros1(self):
        """
        Test the default "html" macro, found in ./creole/default_macros.py
        """
        html = creole2html(
            markup_string=u"<<html>><p>foo</p><</html>><bar?>",
            verbose=1,
            macros=example_macros
#            stderr=sys.stderr, debug=False
        )
        self.assertEqual(html, u'<p>foo</p>\n<p>&lt;bar?&gt;</p>\n')

    def test_example_macros2(self):
        html = creole2html(
            markup_string=u"<<html>>{{{&lt;nocode&gt;}}}<</html>>",
            verbose=1,
            macros=example_macros
#            stderr=sys.stderr, debug=False
        )
        self.assertEqual(html, u'{{{&lt;nocode&gt;}}}\n')

    def test_example_macros3(self):
        html = creole2html(
            markup_string=u"<<html>>1<</html>><<html>>2<</html>>",
            verbose=1,
            macros=example_macros,
#            stderr=sys.stderr, debug=False
        )
        self.assertEqual(html, u'1\n2\n')

    def test_macro_dict(self):
        """
        simple test for the "macro API"
        """
        def test(text, foo, bar):
            return u"|".join([foo, bar, text])

        html = creole2html(
            markup_string=u"<<test bar='b' foo='a'>>c<</test>>",
            macros={"test": test}
        )
        self.assertEqual(html, u'a|b|c\n')

    def test_macro_callable(self):
        """
        simple test for the "macro API"
        """
        def testmacro():
            pass

        self.failUnlessRaises(DeprecationWarning,
            creole2html,
            markup_string=u"<<test no=1 arg2='foo'>>bar<</test>>",
            macros=testmacro
        )







class TestCreole2htmlMarkup(BaseCreoleTest):

    def assertCreole(self, *args, **kwargs):
        self.assert_Creole2html(*args, **kwargs)

    #--------------------------------------------------------------------------

    def test_creole_basic(self):
        out_string = creole2html(u"a text line.")
        self.assertEqual(out_string, "<p>a text line.</p>\n")

    def test_lineendings(self):
        """ Test all existing lineending version """
        out_string = creole2html(u"first\nsecond")
        self.assertEqual(out_string, u"<p>first<br />\nsecond</p>\n")

        out_string = creole2html(u"first\rsecond")
        self.assertEqual(out_string, u"<p>first<br />\nsecond</p>\n")

        out_string = creole2html(u"first\r\nsecond")
        self.assertEqual(out_string, u"<p>first<br />\nsecond</p>\n")

    #--------------------------------------------------------------------------

    def test_creole_linebreak(self):
        self.assertCreole(r"""
            Force\\linebreak
        """, """
            <p>Force<br />
            linebreak</p>
        """)

    def test_html_lines(self):
        self.assertCreole(r"""
            This is a normal Text block witch would
            escape html chars like < and > ;)
            
            So you can't insert <html> directly.
            
            <p>This escaped, too.</p>
        """, """
            <p>This is a normal Text block witch would<br />
            escape html chars like &lt; and &gt; ;)</p>
            
            <p>So you can't insert &lt;html&gt; directly.</p>
            
            <p>&lt;p&gt;This escaped, too.&lt;/p&gt;</p>
        """)

    def test_escape_char(self):
        self.assertCreole(r"""
            ~#1
            http://domain.tld/~bar/
            ~http://domain.tld/
            [[Link]]
            ~[[Link]]
        """, """
            <p>#1<br />
            <a href="http://domain.tld/~bar/">http://domain.tld/~bar/</a><br />
            http://domain.tld/<br />
            <a href="Link">Link</a><br />
            [[Link]]</p>
        """)

    def test_cross_paragraphs(self):
        self.assertCreole(r"""
            Bold and italics should //not be...

            ...able// to **cross 
            
            paragraphs.**
        """, """
            <p>Bold and italics should //not be...</p>
            
            <p>...able// to **cross</p>
            
            <p>paragraphs.**</p>
        """)

    def test_list_special(self):
        """
        optional whitespace before the list 
        """
        self.assertCreole(r"""
            * Item 1
            ** Item 1.1
             ** Item 1.2
                ** Item 1.3
                    * Item2
            
                # one
              ## two
        """, """
        <ul>
            <li>Item 1
            <ul>
                <li>Item 1.1</li>
                <li>Item 1.2</li>
                <li>Item 1.3</li>
            </ul></li>
            <li>Item2</li>
        </ul>
        <ol>
            <li>one
            <ol>
                <li>two</li>
            </ol></li>
        </ol>
        """)

    def test_macro_basic(self):
        """
        Test the three diferent macro types with a "unittest macro"
        """
        self.assertCreole(r"""
            There exist three different macro types:
            A <<test_macro1 args="foo1">>bar1<</test_macro1>> in a line...
            ...a single <<test_macro1 foo="bar">> tag,
            or: <<test_macro1 a=1 b=2 />> closed...
            
            a macro block:
            <<test_macro2 char="|">>
            the
            text
            <</test_macro2>>
            the end
        """, r"""
            <p>There exist three different macro types:<br />
            A [test macro1 - kwargs: args='foo1',text=u'bar1'] in a line...<br />
            ...a single [test macro1 - kwargs: foo='bar',text=None] tag,<br />
            or: [test macro1 - kwargs: a=1,b=2,text=None] closed...</p>
            
            <p>a macro block:</p>
            the|text
            <p>the end</p>
        """,
            macros=test_macros,
        )

    def test_macro_html1(self):
        self.assertCreole(r"""
            html macro:
            <<html>>
            <p><<this is broken 'html', but it will be pass throu>></p>
            <</html>>
            
            inline: <<html>>&#x7B;...&#x7D;<</html>> code
        """, r"""
            <p>html macro:</p>
            <p><<this is broken 'html', but it will be pass throu>></p>
            
            <p>inline: &#x7B;...&#x7D; code</p>
        """, #debug=True
            macros=example_macros,
        )

    def test_macro_not_exist1(self):
        """
        not existing macro with creole2html.HtmlEmitter(verbose=1):
        A error message should be insertet into the generated code
        
        Two tests: with verbose=1 and verbose=2, witch write a Traceback
        information to a given "stderr"
        """
        source_string = r"""
            macro block:
            <<notexists>>
            foo bar
            <</notexists>>
            
            inline macro:
            <<notexisttoo foo="bar">>
        """
        should_string = r"""
            <p>macro block:</p>
            [Error: Macro 'notexists' doesn't exist]
            
            <p>inline macro:<br />
            [Error: Macro 'notexisttoo' doesn't exist]
            </p>
        """

        self.assertCreole(source_string, should_string, verbose=1)

        #----------------------------------------------------------------------
        # Test with verbose=2 ans a StringIO stderr handler

    def test_macro_not_exist2(self):
        """
        not existing macro with creole2html.HtmlEmitter(verbose=0):
        
        No error messages should be inserted.
        """
        self.assertCreole(r"""
            macro block:
            <<notexists>>
            foo bar
            <</notexists>>
            
            inline macro:
            <<notexisttoo foo="bar">>
        """, r"""
            <p>macro block:</p>
            
            <p>inline macro:<br />
            </p>
        """,
            verbose=0
        )

    def test_image(self):
        """ test image tag with different picture text """
        self.assertCreole(r"""
            {{foobar1.jpg}}
            {{/path1/path2/foobar2.jpg}}
            {{/path1/path2/foobar3.jpg|foobar3.jpg}}
        """, """
            <p><img src="foobar1.jpg" alt="foobar1.jpg" /><br />
            <img src="/path1/path2/foobar2.jpg" alt="/path1/path2/foobar2.jpg" /><br />
            <img src="/path1/path2/foobar3.jpg" alt="foobar3.jpg" /></p>
        """)

    def test_image_unknown_extension(self):
        self.assertCreole(r"""
            # {{/path/to/image.ext|image ext}} one
            # {{/no/extension|no extension}} two
            # {{/image.xyz}} tree
        """, """
            <ol>
                <li><img src="/path/to/image.ext" alt="image ext" /> one</li>
                <li><img src="/no/extension" alt="no extension" /> two</li>
                <li><img src="/image.xyz" alt="/image.xyz" /> tree</li>
            </ol>
        """)

    def test_links(self):
        self.assertCreole(r"""
            [[/foobar/Creole_(Markup)]]
            [[http://de.wikipedia.org/wiki/Creole_(Markup)|Creole@wikipedia]]
        """, """
            <p><a href="/foobar/Creole_(Markup)">/foobar/Creole_(Markup)</a><br />
            <a href="http://de.wikipedia.org/wiki/Creole_(Markup)">Creole@wikipedia</a></p>
        """)

    def test_wiki_style_line_breaks(self):

        html = creole2html(
            markup_string=self._prepare_text(u"""
                with blog line breaks, every line break would be convertet into <br />
                with wiki style not.
                
                This is the first line,\\\\and this is the second.
                
                new line
                 block 1
                
                new line
                 block 2
                
                end
            """),
            blog_line_breaks=False
        )
        self.assertEqual(html, self._prepare_text(u"""
            <p>with blog line breaks, every line break would be convertet into &lt;br /&gt;with wiki style not.</p>
            
            <p>This is the first line,<br />
            and this is the second.</p>
            
            <p>new line block 1</p>
            
            <p>new line block 2</p>
            
            <p>end</p>
            
        """))


    def test_headline_spaces(self):
        """
        https://code.google.com/p/python-creole/issues/detail?id=15
        """
        html = creole2html(markup_string=u"== Headline1 == \n== Headline2== ")
        self.assertEqual(html, self._prepare_text(u"""
            <h2>Headline1</h2>
            <h2>Headline2</h2>
            
        """))

    def test_tt(self):
        self.assertCreole(r"""
            inline {{{<escaped>}}} and {{{ **not strong** }}}...
            ...and ##**strong** Teletyper## ;)
        """, """
            <p>inline <tt>&lt;escaped&gt;</tt> and <tt> **not strong** </tt>...<br />
            ...and <tt><strong>strong</strong> Teletyper</tt> ;)</p>
        """)



if __name__ == '__main__':
    unittest.main()
#if __name__ == '__main__':
#    suite = unittest.TestLoader().loadTestsFromTestCase(TestCreole2html)
#    unittest.TextTestRunner().run(suite)
