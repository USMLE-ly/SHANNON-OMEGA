// ==UserScript==
// @name         LEXOR Twitter Auto-Poster
// @namespace    http://lexor.ly/
// @version      1.0
// @description  One-click tweet posting for LEXOR fashion content
// @author       SHANNON-Ω
// @match        https://twitter.com/*
// @match        https://x.com/*
// @grant        GM_notification
// ==/UserScript==

(function() {
    'use strict';

    const TWEETS = [
        "Minimalist fashion: clean lines, intentional choices, zero regret. A capsule wardrobe isn't limitation—it's freedom.",
        "Fit over fabric. Fabric over brand. A $20 shirt that fits beats a $200 shirt that doesn't.",
        "Style is not about having more. It's about choosing better.",
        "Before buying anything new ask: does this go with three things I already own?",
        "Neutrals are the foundation. Color is the accent. Master the first before chasing the second.",
        "The most expensive thing you can wear is regret over a purchase you never used.",
        "Fashion is armor for the psyche. Dress accordingly.",
        "A wardrobe should make you feel powerful, not pretty. If it doesn't, you're dressing for the wrong audience.",
    ];

    let tweetIndex = parseInt(localStorage.getItem('lexor_tweet_index') || '0');

    function addFloatingButton() {
        const btn = document.createElement('button');
        btn.id = 'lexor-tweet-btn';
        btn.innerHTML = 'LEXOR';
        btn.style.cssText = `
            position: fixed; bottom: 80px; right: 20px; z-index: 99999;
            background: #C8A951; color: #000; border: none;
            border-radius: 50%; width: 50px; height: 50px;
            font-weight: bold; font-size: 12px; cursor: pointer;
            box-shadow: 0 4px 15px rgba(200,169,81,0.4);
            transition: transform 0.2s;
        `;
        btn.onmouseenter = () => btn.style.transform = 'scale(1.1)';
        btn.onmouseleave = () => btn.style.transform = 'scale(1)';
        btn.onclick = postNextTweet;
        document.body.appendChild(btn);
    }

    function postNextTweet() {
        const tweet = TWEETS[tweetIndex % TWEETS.length];
        tweetIndex++;
        localStorage.setItem('lexor_tweet_index', tweetIndex.toString());

        // Find tweet composer
        const tweetBtn = document.querySelector('[data-testid="SideNav_NewTweet_Button"]');
        if (tweetBtn) {
            tweetBtn.click();
            setTimeout(() => {
                const textarea = document.querySelector('[data-testid="tweetTextarea_0"]');
                if (textarea) {
                    textarea.focus();
                    document.execCommand('insertText', false, tweet);
                    setTimeout(() => {
                        const postBtn = document.querySelector('[data-testid="tweetButton"]');
                        if (postBtn) postBtn.click();
                        GM_notification({ text: '✅ LEXOR tweet posted!', timeout: 3000 });
                    }, 500);
                }
            }, 1000);
        } else {
            alert('LEXOR: Click the Post button in the sidebar first!');
        }
    }

    setTimeout(addFloatingButton, 3000);
    console.log('LEXOR Twitter poster loaded');
})();
