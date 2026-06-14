#!/usr/bin/env node
/**
 * EmailGen — Temporary email generator + inbox checker
 * Uses Guerrilla Mail API (free, no signup, works instantly)
 */
const API = 'https://api.guerrillamail.com/ajax.php';

async function apiCall(params) {
  const url = `${API}?${new URLSearchParams(params)}`;
  const res = await fetch(url);
  return res.json();
}

async function generateEmail() {
  console.log('[EMAILGEN] Generating temporary email...');
  const data = await apiCall({ f: 'get_email_address', ip: '127.0.0.1', agent: 'ZORG-Ω' });
  console.log(`  ✓ Email: ${data.email_addr}`);
  console.log(`  ✓ Token: ${data.sid_token}`);
  return data;
}

async function checkInbox(sidToken) {
  const data = await apiCall({ f: 'get_email_list', sid_token: sidToken, offset: '0', limit: '20' });
  return data;
}

async function fetchEmail(sidToken, emailId) {
  const data = await apiCall({ f: 'fetch_email', sid_token: sidToken, email_id: emailId });
  return data;
}

async function waitForEmail(sidToken, timeoutMs = 120000) {
  const start = Date.now();
  console.log('[EMAILGEN] Waiting for new emails...');
  while (Date.now() - start < timeoutMs) {
    const inbox = await checkInbox(sidToken);
    const emails = inbox.list || [];
    if (emails.length > 0) {
      const newest = emails[0];
      console.log(`  ✓ New email: "${newest.mail_subject}" from ${newest.mail_from}`);
      const full = await fetchEmail(sidToken, newest.mail_id);
      return full;
    }
    await new Promise(r => setTimeout(r, 3000));
    process.stdout.write('.');
  }
  console.log('\n[EMAILGEN] Timeout waiting for email');
  return null;
}

const args = process.argv.slice(2);
const cmd = args[0] || 'generate';

switch (cmd) {
  case 'generate': {
    const data = await generateEmail();
    console.log(`\nEmail:     ${data.email_addr}`);
    console.log(`SID Token: ${data.sid_token}`);
    console.log(`Alias:     ${data.alias}`);
    
    // Save to file
    const fs = await import('fs');
    const path = await import('path');
    const fpath = path.resolve(import.meta.dirname, '../../../.last_email.json');
    fs.writeFileSync(fpath, JSON.stringify(data, null, 2));
    console.log(`\nSaved to:  .last_email.json`);
    break;
  }
  case 'inbox': {
    const sid = args[1];
    const inbox = await checkInbox(sid);
    console.log(`Inbox has ${inbox.count || 0} emails:`);
    for (const email of (inbox.list || [])) {
      console.log(`  [${email.mail_id}] ${email.mail_subject}`);
      console.log(`         From: ${email.mail_from}`);
      console.log(`         Time: ${email.mail_timestamp}`);
    }
    break;
  }
  case 'wait': {
    const sid = args[1];
    const email = await waitForEmail(sid);
    if (email) {
      console.log(`\nSubject: ${email.mail_subject}`);
      console.log(`From:    ${email.mail_from}`);
      console.log(`Body:    ${(email.mail_body || '').substring(0, 500)}`);
    }
    break;
  }
  default:
    console.log('EmailGen — Temporary Email Tool');
    console.log('');
    console.log('Usage:');
    console.log('  node emailgen.mjs generate             Get new temp email');
    console.log('  node emailgen.mjs inbox <sid_token>     Check inbox');
    console.log('  node emailgen.mjs wait <sid_token>      Wait for new email');
}
