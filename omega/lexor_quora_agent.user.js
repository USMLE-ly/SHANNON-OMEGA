// ==UserScript==
// @name         LEXOR Quora Auto-Answer Agent
// @namespace    http://lexor.ly/
// @version      1.0
// @description  One-click Quora answer posting for LEXOR fashion content
// @author       SHANNON-Ω
// @match        https://www.quora.com/*
// @match        https://quora.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_notification
// ==/UserScript==

(function() {
    'use strict';

    const API_URL = 'https://opencode.ai/zen/v1/chat/completions';
    const ANSWERS_KEY = 'lexor_quora_answers';

    // Pre-loaded fashion answers (fallback if API fails)
    const FALLBACK_ANSWERS = [
        "The biggest mistake is buying for a fantasy version of yourself. Dress the person you are today, not the one you might be.",
        "Fit matters more than fabric. Fabric matters more than brand. A $20 shirt that fits beats a $200 one that doesn't.",
        "A capsule wardrobe isn't limitation. It's freedom. 33 items, infinite outfits, zero decision fatigue.",
        "Before buying anything new ask: does this go with three things I already own? If no, put it back.",
        "Neutrals are the foundation. Color is the accent. Master the first before chasing the second.",
        "Style is not about having more. It's about choosing better. Quality over quantity always wins.",
        "The most expensive thing you can wear is regret over a purchase you never used.",
        "Dressing well is not about the clothes. It's about the confidence they give you.",
    ];

    // Add control panel to Quora pages
    function addControlPanel() {
        const panel = document.createElement('div');
        panel.id = 'lexor-panel';
        panel.innerHTML = `
            <div style="
                position: fixed; bottom: 20px; right: 20px; z-index: 99999;
                background: #1a1a1a; color: #fff; padding: 12px 16px;
                border-radius: 12px; font-family: -apple-system, sans-serif;
                font-size: 13px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                border: 1px solid #333; max-width: 280px;
            ">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong style="color:#C8A951;">LEXOR</strong>
                    <span style="color:#888; font-size:11px;">SHANNON-Ω</span>
                </div>
                <button id="lexor-answer-btn" style="
                    width:100%; padding:8px; background:#C8A951; color:#000;
                    border:none; border-radius:6px; font-weight:600; cursor:pointer;
                    margin-bottom:6px;
                ">✨ Generate Answer</button>
                <button id="lexor-fill-btn" style="
                    width:100%; padding:6px; background:#333; color:#fff;
                    border:none; border-radius:6px; cursor:pointer; font-size:12px;
                    margin-bottom:4px;
                ">📋 Paste Saved Answer</button>
                <div id="lexor-status" style="color:#888; font-size:11px; margin-top:4px;"></div>
            </div>
        `;
        document.body.appendChild(panel);

        document.getElementById('lexor-answer-btn').onclick = generateAndFill;
        document.getElementById('lexor-fill-btn').onclick = showSavedAnswers;
    }

    function setStatus(msg, isError = false) {
        const el = document.getElementById('lexor-status');
        if (el) {
            el.textContent = msg;
            el.style.color = isError ? '#ff6b6b' : '#888';
        }
    }

    async function generateAndFill() {
        setStatus('Generating answer...');

        // Get the question from the page
        let question = '';
        const qEl = document.querySelector('[class*="question"], [class*="QText"], h1, .q-text');
        if (qEl) question = qEl.textContent.trim().substring(0, 200);

        try {
            // Try API first
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: 'deepseek-v4-flash-free',
                    messages: [
                        { role: 'system', content: 'Write a short Quora answer about fashion. 100-200 words. Sound like a real person, not AI. No hashtags.' },
                        { role: 'user', content: question || 'Write about minimalist wardrobe tips' }
                    ],
                    temperature: 0.8,
                    max_tokens: 1000
                })
            });
            const data = await response.json();
            let answer = data.choices?.[0]?.message?.content || '';
            if (answer.length > 20) {
                fillAnswerBox(answer);
                return;
            }
        } catch(e) {
            console.log('API failed, using fallback');
        }

        // Fallback: pick a random pre-loaded answer
        const randomIdx = Math.floor(Math.random() * FALLBACK_ANSWERS.length);
        fillAnswerBox(FALLBACK_ANSWERS[randomIdx]);
    }

    function fillAnswerBox(text) {
        // Find the answer editor
        const editor = document.querySelector('[contenteditable="true"], .qu-editor, [class*="editor"], [data-testid="answer-editor"]');
        if (editor) {
            editor.focus();
            // Insert text
            document.execCommand('insertText', false, '\n' + text + '\n');
            setStatus('✅ Answer pasted! Review and post.');
            GM_notification({ text: 'LEXOR: Answer pasted!', timeout: 3000 });
        } else {
            setStatus('⚠️ Click the answer box first, then generate', true);
        }
    }

    function showSavedAnswers() {
        const saved = GM_getValue(ANSWERS_KEY, FALLBACK_ANSWERS);
        const pick = saved[Math.floor(Math.random() * saved.length)];
        fillAnswerBox(pick);
    }

    // Auto-init
    setTimeout(addControlPanel, 3000);
})();
