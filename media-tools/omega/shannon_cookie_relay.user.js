// ==UserScript==
// @name         SHANNON-Ω Cookie Relay
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Auto-export cookies to SHANNON-Ω server for automation
// @author       ZORG-Ω
// @match        https://*.quora.com/*
// @match        https://*.twitter.com/*
// @match        https://*.x.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_cookie
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    const SERVER_URL = 'http://localhost:7777/cookies';
    const INTERVAL_MS = 6 * 60 * 60 * 1000; // Every 6 hours

    function getCookiesForDomain() {
        // Try using document.cookie first (limited but works for many sites)
        var cookies = document.cookie.split(';').map(function(c) {
            var parts = c.trim().split('=');
            return {name: parts[0], value: parts.slice(1).join('=')};
        });
        return cookies;
    }

    function sendCookies() {
        var cookies = getCookiesForDomain();
        var payload = {
            url: window.location.hostname,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            cookies: cookies,
            localStorage: Object.entries(localStorage).map(function(e) {
                return {name: e[0], value: e[1]};
            })
        };

        GM_xmlhttpRequest({
            method: 'POST',
            url: SERVER_URL,
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(payload),
            onload: function(rsp) {
                console.log('[SHANNON-Ω] Cookies relayed: ' + rsp.status);
            },
            onerror: function(err) {
                console.log('[SHANNON-Ω] Relay failed: ' + err);
            }
        });
    }

    // Send on page load + every 6 hours
    setTimeout(sendCookies, 5000);  // First send after 5s
    setInterval(sendCookies, INTERVAL_MS);

    console.log('[SHANNON-Ω] Cookie Relay active — auto-sending every 6h');
})();