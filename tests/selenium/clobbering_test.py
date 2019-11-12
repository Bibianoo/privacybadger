#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

import pbtest


class ClobberingTest(pbtest.PBSeleniumTest):
    COOKIEBLOCK_JS = (
        "(function (domain) {"
        "  let bg = chrome.extension.getBackgroundPage();"
        "  bg.badger.storage.setupHeuristicAction(domain, bg.constants.COOKIEBLOCK);"
        "}(arguments[0]));"
    )

    def test_localstorage_clobbering(self):
        LOCALSTORAGE_TESTS = [
            # (test result element ID, expected stored, expected empty)
            ('get-item', "qwerty", "null"),
            ('get-property', "asdf", "undefined"),
            ('get-item-proto', "qwerty", "null"),
            ('get-item-srcdoc', "qwerty", "null"),
            ('get-property-srcdoc', "asdf", "undefined"),
            ('get-item-frames', "qwerty", "null"),
            ('get-property-frames', "asdf", "undefined"),
        ]
        # page loads a frame that writes to and reads from localStorage
        # TODO remove delays from fixture once race condition (https://crbug.com/478183) is fixed
        FIXTURE_URL = (
            "https://efforg.github.io/privacybadger-test-fixtures/html/"
            "clobbering.html"
        )
        FRAME_DOMAIN = "githack.com"

        # first allow localStorage to be set
        self.load_url(FIXTURE_URL)
        self.wait_for_and_switch_to_frame('iframe')
        for selector, expected, _ in LOCALSTORAGE_TESTS:
            # wait for each test to run
            self.wait_for_script(
                "return document.getElementById('%s')"
                ".textContent != '...';" % selector,
                timeout=2,
                message=(
                    "Timed out waiting for localStorage (%s) to finish ... "
                    "This probably means the fixture "
                    "errored out somewhere." % selector
                )
            )
            self.assertEqual(
                self.txt_by_css("#" + selector), expected,
                "localStorage (%s) was not read successfully"
                "for some reason" % selector
            )

        # mark the frame domain for cookieblocking
        self.load_url(self.options_url)
        self.js(self.COOKIEBLOCK_JS, FRAME_DOMAIN)

        # now rerun and check results for various localStorage access tests
        self.load_url(FIXTURE_URL)
        self.wait_for_and_switch_to_frame('iframe')
        for selector, _, expected in LOCALSTORAGE_TESTS:
            # wait for each test to run
            self.wait_for_script(
                "return document.getElementById('%s')"
                ".textContent != '...';" % selector,
                timeout=2,
                message=(
                    "Timed out waiting for localStorage (%s) to finish ... "
                    "This probably means the fixture "
                    "errored out somewhere." % selector
                )
            )
            self.assertEqual(
                self.txt_by_css("#" + selector), expected,
                "localStorage (%s) was read despite cookieblocking" % selector
            )

    def test_referrer_header(self):
        FIXTURE_URL = (
            "https://efforg.github.io/privacybadger-test-fixtures/html/"
            "referrer.html"
        )
        THIRD_PARTY_DOMAIN = "httpbin.org"

        # cookieblock the domain fetched by the fixture
        self.load_url(self.options_url)
        self.js(self.COOKIEBLOCK_JS, THIRD_PARTY_DOMAIN)

        # check the referrer header according to that domain
        self.load_url(FIXTURE_URL)
        self.wait_for_script(
            "return document.getElementById('referrer').textContent != '';")
        referrer = self.txt_by_css("#referrer")
        self.assertEqual(referrer[0:8], "Referer=", "Unexpected page output")
        self.assertEqual(
            referrer[8:],
            "https://efforg.github.io/",
            "Referrer header does not appear to be origin-only"
        )

if __name__ == "__main__":
    unittest.main()
