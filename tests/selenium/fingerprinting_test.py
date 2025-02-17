#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest
import unittest

import pbtest


class FingerprintingTest(pbtest.PBSeleniumTest):
    """Tests to make sure fingerprinting detection works as expected."""

    def detected_fingerprinting(self, domain):
        return self.js("""let tracker_origin = window.getBaseDomain("{}");
let tabData = chrome.extension.getBackgroundPage().badger.tabData;
return (
  Object.keys(tabData).some(tab_id => {{
    let fpData = tabData[tab_id].fpData;
    return fpData &&
      fpData.hasOwnProperty(tracker_origin) &&
      fpData[tracker_origin].canvas &&
      fpData[tracker_origin].canvas.fingerprinting === true;
  }})
);""".format(domain))

    def get_fillText_source(self):
        return self.js("""
            const canvas = document.getElementById("writetome");
            const ctx = canvas.getContext("2d");
            return ctx.fillText.toString();
        """)

    def setUp(self):
        # enable local learning
        self.load_url(self.options_url)
        self.wait_for_script("return window.OPTIONS_INITIALIZED")
        self.find_el_by_css('#local-learning-checkbox').click()

    @pytest.mark.flaky(reruns=3, condition=pbtest.shim.browser_type == "firefox")
    def test_canvas_fingerprinting_detection(self):
        FIXTURE_URL = (
            "https://efforg.github.io/privacybadger-test-fixtures/html/"
            "fingerprinting.html"
        )
        FINGERPRINTING_DOMAIN = "cdn.jsdelivr.net"

        # clear pre-trained/seed tracker data
        self.load_url(self.options_url)
        self.js("chrome.extension.getBackgroundPage().badger.storage.clearTrackerData();")

        # visit the page
        self.load_url(FIXTURE_URL)

        # open popup and check slider state
        self.load_pb_ui(FIXTURE_URL)
        sliders = self.get_tracker_state()
        self.assertIn(
            FINGERPRINTING_DOMAIN,
            sliders['notYetBlocked'],
            "Canvas fingerprinting domain should be reported in the popup"
        )

        # check that we detected canvas fingerprinting specifically
        self.load_url(self.options_url)
        self.assertTrue(
            self.detected_fingerprinting(FINGERPRINTING_DOMAIN),
            "Canvas fingerprinting resource was detected as a fingerprinter."
        )

    # Privacy Badger overrides a few functions on canvas contexts to check for fingerprinting.
    # In previous versions, it would restore the native function after a single call. Unfortunately,
    # this would wipe out polyfills that had also overridden the same functions, such as the very
    # popular "hidpi-canvas-polyfill".
    def test_canvas_polyfill_clobbering(self):
        FIXTURE_URL = (
            "https://efforg.github.io/privacybadger-test-fixtures/html/"
            "fingerprinting_canvas_hidpi.html"
        )

        # visit the page
        self.load_url(FIXTURE_URL)

        # check that we did not restore the native function (should be hipdi polyfill)
        self.assertNotIn("[native code]", self.get_fillText_source(),
            "Canvas context fillText is not native version (polyfill has been retained)."
        )


if __name__ == "__main__":
    unittest.main()
