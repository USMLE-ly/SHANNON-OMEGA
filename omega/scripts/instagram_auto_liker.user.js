// ==UserScript==
// @name         Ω Omega Instagram Bot
// @namespace    http://shannon-omega.io/
// @version      2.0
// @description  SHANNON-Ω Instagram automation — like, follow, growth
// @author       SHANNON-Ω
// @match        https://www.instagram.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=instagram.com
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_log
// @grant        GM_addStyle
// @grant        GM_info
// ==/UserScript==

(function() {
    'use strict';

    const CONFIG = {
        likeInterval: parseInt(GM_getValue('likeInterval', '3000')),
        followInterval: parseInt(GM_getValue('followInterval', '7000')),
        maxLikes: parseInt(GM_getValue('maxLikes', '30')),
        maxFollows: parseInt(GM_getValue('maxFollows', '10')),
        target: GM_getValue('target', 'vaulex_watches'),
    };

    GM_log('Ω Omega Bot active — target: @' + CONFIG.target);

    // Styles
    GM_addStyle(`
        #omega-panel {
            position:fixed; bottom:20px; right:20px; z-index:99999;
            background:#1a1a2e; color:#fff; padding:16px; border-radius:12px;
            font-family:monospace; font-size:13px; min-width:220px;
            box-shadow:0 0 30px rgba(0,255,0,0.25); border:1px solid #00ff88;
            backdrop-filter:blur(8px);
        }
        #omega-panel .title {
            font-weight:bold; margin-bottom:10px; color:#00ff88;
            font-size:14px; letter-spacing:1px;
        }
        #omega-panel label { display:block; margin-bottom:6px; color:#aaa; font-size:11px; }
        #omega-panel input {
            width:100%; background:#16213e; color:#fff; border:1px solid #333;
            padding:4px 8px; border-radius:4px; box-sizing:border-box; margin-top:2px;
        }
        #omega-panel .btn-row { display:flex; gap:6px; margin:8px 0; }
        #omega-panel button {
            flex:1; border:none; padding:6px 10px; border-radius:6px;
            cursor:pointer; font-size:12px; font-weight:bold; transition:0.2s;
        }
        #omega-panel button:hover { transform:scale(1.05); }
        #omega-panel .btn-like { background:#00ff88; color:#000; }
        #omega-panel .btn-follow { background:#ff6b6b; color:#fff; }
        #omega-panel .btn-export { background:#4a4a6a; color:#fff; }
        #omega-panel .stats { font-size:11px; color:#888; margin-top:4px; }
        #omega-panel .log { font-size:10px; color:#666; margin-top:6px; max-height:60px; overflow-y:auto; }
        #omega-panel .close-btn { background:none; color:#555; border:none; cursor:pointer; font-size:11px; margin-top:4px; }
        .omega-log-entry { color:#888; margin:1px 0; }
    `);

    function log(msg) {
        GM_log('[Ω] ' + msg);
        const el = document.getElementById('omega-log');
        if (el) {
            const entry = document.createElement('div');
            entry.className = 'omega-log-entry';
            entry.textContent = '> ' + msg;
            el.appendChild(entry);
            el.scrollTop = el.scrollHeight;
        }
    }

    function addControlPanel() {
        const panel = document.createElement('div');
        panel.id = 'omega-panel';
        panel.innerHTML = `
            <div class="title">Ω OMEGA BOT</div>
            <label>Target username
                <input id="omega-target" value="${CONFIG.target}">
            </label>
            <div class="btn-row">
                <button class="btn-like" id="omega-like">❤ Like</button>
                <button class="btn-follow" id="omega-follow">➕ Follow</button>
            </div>
            <div class="btn-row">
                <button class="btn-export" id="omega-export-cookies">🍪 Export Cookies</button>
                <button class="btn-export" id="omega-export-state">💾 Save State</button>
            </div>
            <div class="stats">
                Likes: <span id="omega-like-count">0</span> &middot;
                Follows: <span id="omega-follow-count">0</span> &middot;
                <span id="omega-status">idle</span>
            </div>
            <div class="log" id="omega-log"></div>
            <button class="close-btn" id="omega-close">✕ hide (show again: Ω+F12)</button>
        `;
        document.body.appendChild(panel);

        document.getElementById('omega-like').onclick = startAutoLike;
        document.getElementById('omega-follow').onclick = startAutoFollow;
        document.getElementById('omega-export-cookies').onclick = exportCookies;
        document.getElementById('omega-export-state').onclick = saveState;
        document.getElementById('omega-close').onclick = () => panel.style.display = 'none';

        // Keyboard shortcut: Ω+F12 to show panel
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F12' && e.ctrlKey) {
                panel.style.display = 'block';
            }
        });

        log('Panel loaded — ready');
    }

    // Helper: wait ms
    function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

    // Helper: find visible button by text
    function findButton(text) {
        const buttons = document.querySelectorAll('button, div[role="button"], a[role="button"]');
        for (const btn of buttons) {
            if (btn.textContent.trim().toLowerCase() === text.toLowerCase()) {
                if (btn.offsetParent !== null) return btn;
            }
        }
        return null;
    }

    // ═══ AUTO LIKE ═══
    async function startAutoLike() {
        log('Starting auto-like...');
        document.getElementById('omega-status').textContent = 'liking...';
        let count = 0;

        const target = document.getElementById('omega-target').value.trim();
        if (target && !window.location.href.includes('/' + target + '/')) {
            window.location.href = 'https://www.instagram.com/' + target + '/';
            await wait(3000);
        }

        const postLinks = document.querySelectorAll('a[href*="/p/"]');
        log('Found ' + postLinks.length + ' posts');

        for (const link of postLinks) {
            if (count >= CONFIG.maxLikes) break;

            try {
                link.click();
                await wait(3000);

                // Find and click Like button
                const likeSvg = document.querySelector('svg[aria-label="Like"]');
                if (likeSvg) {
                    // Walk up to find clickable parent
                    let el = likeSvg.parentElement;
                    while (el && el.tagName !== 'BUTTON' && el.tagName !== 'DIV' && el.tagName !== 'A') {
                        el = el.parentElement;
                    }
                    if (el && el.click) {
                        el.click();
                        count++;
                        document.getElementById('omega-like-count').textContent = count;
                        log('Liked post #' + count);
                    }
                } else {
                    log('Like button not visible (already liked?)');
                }

                await wait(1500);

                // Close post
                const closeSvg = document.querySelector('svg[aria-label="Close"]');
                if (closeSvg) {
                    let el = closeSvg.parentElement;
                    while (el && el.tagName !== 'BUTTON' && el.tagName !== 'DIV' && el.tagName !== 'A') {
                        el = el.parentElement;
                    }
                    if (el && el.click) el.click();
                }
                await wait(CONFIG.likeInterval);
            } catch(e) {
                log('Like error: ' + e.message);
            }
        }

        log('Auto-like complete: ' + count + ' likes');
        document.getElementById('omega-status').textContent = 'done';
    }

    // ═══ AUTO FOLLOW ═══
    async function startAutoFollow() {
        log('Starting auto-follow...');
        document.getElementById('omega-status').textContent = 'following...';
        let count = 0;

        const target = document.getElementById('omega-target').value.trim();
        if (target && !window.location.href.includes('/' + target + '/')) {
            window.location.href = 'https://www.instagram.com/' + target + '/';
            await wait(3000);
        }

        // Try to open followers
        const followersLink = document.querySelector('a[href$="/followers/"]');
        if (followersLink) {
            followersLink.click();
            await wait(3000);
        }

        // Find Follow buttons
        const allButtons = document.querySelectorAll('button');
        const followBtns = [];
        for (const btn of allButtons) {
            const text = btn.textContent.trim().toLowerCase();
            if (text === 'follow' && btn.offsetParent !== null) {
                followBtns.push(btn);
            }
        }

        log('Found ' + followBtns.length + ' follow buttons');

        for (const btn of followBtns) {
            if (count >= CONFIG.maxFollows) break;

            try {
                btn.click();
                count++;
                document.getElementById('omega-follow-count').textContent = count;
                log('Followed #' + count);
                await wait(CONFIG.followInterval);
            } catch(e) {
                log('Follow error: ' + e.message);
            }
        }

        log('Auto-follow complete: ' + count + ' follows');
        document.getElementById('omega-status').textContent = 'done';
    }

    // ═══ EXPORT COOKIES ═══
    function exportCookies() {
        const cookies = document.cookie.split('; ').map(c => {
            const [name, ...val] = c.split('=');
            return { name: name.trim(), value: val.join('=') || '', domain: '.instagram.com', path: '/' };
        });

        // Also try to get cookies from document.cookie with httpOnly ones
        const cookieStr = JSON.stringify(cookies, null, 2);
        navigator.clipboard.writeText(cookieStr).then(() => {
            log('Copied ' + cookies.length + ' cookies to clipboard');
        }).catch(() => {
            // Fallback: show in console
            console.log('Ω COOKIES:', cookies);
            log('Cookies logged to console (F12)');
        });

        // Also save to GM storage
        GM_setValue('saved_cookies', JSON.stringify(cookies));
        log('Cookies saved to GM storage');
    }

    // ═══ SAVE STATE ═══
    function saveState() {
        const state = {
            url: window.location.href,
            title: document.title,
            target: document.getElementById('omega-target').value.trim(),
            timestamp: new Date().toISOString(),
        };
        GM_setValue('omega_state', JSON.stringify(state));
        log('State saved');
    }

    // ═══ INIT ═══
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addControlPanel);
    } else {
        addControlPanel();
    }

    // Restore previous target if saved
    const savedTarget = GM_getValue('omega_state');
    if (savedTarget) {
        try {
            const s = JSON.parse(savedTarget);
            if (s.target && document.getElementById('omega-target')) {
                document.getElementById('omega-target').value = s.target;
            }
        } catch(e) {}
    }

})();
