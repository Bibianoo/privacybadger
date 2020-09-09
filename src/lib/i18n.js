/*
 * This file is part of Adblock Plus <http://adblockplus.org/>,
 * Copyright (C) 2006-2013 Eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

(function () {

const LOCALE = chrome.i18n.getMessage('@@ui_locale'),
  ON_POPUP = (document.location.pathname == "/skin/popup.html");

function localizeFaqLink() {
  const LOCALIZED_HOMEPAGE_LOCALES = ['es'];
  if (ON_POPUP && LOCALIZED_HOMEPAGE_LOCALES.includes(LOCALE)) {
    // update FAQ link to point to localized version
    $('#help').prop('href', `https://privacybadger.org/${LOCALE}/#faq`);
  }
}

function setTextDirection() {
  function swap_css_property(selector, from, to) {
    let $els = $(selector);
    $els.each(i => {
      let $el = $($els[i]);
      $el.css(to, $el.css(from)).css(from, "unset");
    });
  }

  function toggle_css_value(selector, property, from, to) {
    let $els = $(selector);
    $els.each(i => {
      let $el = $($els[i]);
      if ($el.css(property) === from) {
        $el.css(property, to);
      }
    });
  }

  // https://www.w3.org/International/questions/qa-scripts#examples
  // https://developer.chrome.com/webstore/i18n?csw=1#localeTable
  // TODO duplicated in src/js/webrequest.js
  const RTL_LOCALES = ['ar', 'he', 'fa'];
  if (!RTL_LOCALES.includes(LOCALE)) {
    return;
  }

  // set body text direction
  document.body.setAttribute("dir", "rtl");

  // popup page
  if (ON_POPUP) {
    // fix floats
    ['#privacyBadgerHeader img', '#header-image-stack', '#instruction-logo', '#version'].forEach((selector) => {
      toggle_css_value(selector, "float", "left", "right");
    });
    ['#fittslaw', '#options', '#help', '#share', '.overlay_close'].forEach((selector) => {
      toggle_css_value(selector, "float", "right", "left");
    });

    // fix margin
    ['#options', '#fittslaw'].forEach(selector => {
      swap_css_property(selector, "margin-right", "margin-left");
    });

    // fix padding
    ['#instruction-logo'].forEach((selector) => {
      swap_css_property(selector, "padding-right", "padding-left");
    });

    // fix text alignment
    ['#instruction'].forEach((selector) => {
      toggle_css_value(selector, "text-align", "left", "right");
    });

  // options page
  } else if (document.location.pathname == "/skin/options.html") {
    // apply RTL workaround for jQuery UI tabs
    // https://zoomicon.wordpress.com/2009/10/15/how-to-use-jqueryui-tabs-in-right-to-left-layout/
    let css = document.createElement("style");
    css.type = "text/css";
    css.textContent = `
.ui-tabs { direction: rtl; }
.ui-tabs .ui-tabs-nav li.ui-tabs-selected,
  .ui-tabs .ui-tabs-nav li.ui-state-default { float: right; }
.ui-tabs .ui-tabs-nav li a { float: right; }
`;
    document.body.appendChild(css);

    // fix margins
    ['#check-dnt-policy-row', '#hide-widgets-row'].forEach((selector) => {
      swap_css_property(selector, "margin-left", "margin-right");
    });
    ['#allowlist-form > div > div > div'].forEach((selector) => {
      swap_css_property(selector, "margin-right", "margin-left");
    });

    // fix floats
    ['.btn-silo', '.btn-silo div', '#allowlist-form > div > div > div'].forEach((selector) => {
      toggle_css_value(selector, "float", "left", "right");
    });
  }
}

// Loads and inserts i18n strings into matching elements. Any inner HTML already in the
// element is parsed as JSON and used as parameters to substitute into placeholders in the
// i18n message.
function loadI18nStrings() {
  // replace span contents by their class names
  let nodes = document.querySelectorAll("[class^='i18n_']");
  for (let i = 0; i < nodes.length; i++) {
    const args = JSON.parse("[" + nodes[i].textContent + "]");
    let className = nodes[i].className;
    if (className instanceof SVGAnimatedString) {
      className = className.animVal;
    }
    const stringName = className.split(/\s/)[0].substring(5);
    const prop = "innerHTML" in nodes[i] ? "innerHTML" : "textContent";
    if (args.length > 0) {
      nodes[i][prop] = chrome.i18n.getMessage(stringName, args);
    } else {
      nodes[i][prop] = chrome.i18n.getMessage(stringName);
    }
  }

  // also replace alt, placeholder and title attributes
  const ATTRS = [
    'alt',
    'placeholder',
    'title',
  ];

  // get all the elements that contain one or more of these attributes
  nodes = document.querySelectorAll(
    // for example: "[placeholder^='i18n_'], [title^='i18n_']"
    "[" + ATTRS.join("^='i18n_'], [") + "^='i18n_']"
  );

  // for each element
  for (let i = 0; i < nodes.length; i++) {
    // for each attribute
    ATTRS.forEach(attr_type => {
      // get the translation message key
      let key = nodes[i].getAttribute(attr_type);
      if (key) {
        // remove the i18n_ prefix
        key = key.slice(5);
      }

      // if the attribute exists and looks like i18n_KEY
      if (key) {
        // get chrome.i18n placeholders, if any
        let placeholders = nodes[i].dataset.i18n_placeholders;
        if (placeholders) {
          placeholders = placeholders.split("@@");
        } else {
          placeholders = [];
        }

        // update the attribute with the result of a translation lookup by KEY
        nodes[i].setAttribute(attr_type, chrome.i18n.getMessage(key, placeholders));
      }
    });
  }
}

// Fill in the strings as soon as possible
window.addEventListener("DOMContentLoaded", function () {
  localizeFaqLink();
  setTextDirection();
  loadI18nStrings();
}, true);

}());
