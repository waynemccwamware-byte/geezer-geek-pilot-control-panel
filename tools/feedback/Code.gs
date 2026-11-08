/**
 * GeezerGeek Pilot Apps — feedback mailer (Google Apps Script web app).
 * App Conventions §5 (footer v1.5) and §7. Not published by Netlify; this file is the master copy.
 *
 * The feedback page (Control Panel site/feedback/) posts each submission here as well as to
 * Netlify Forms (the free archive). This script, running in Wayne's Google account:
 *   1. drops spam (honeypot filled, empty message, more than 20 posts a minute),
 *   2. appends the submission to a "GeezerGeek Feedback" Google Sheet (created on first use),
 *   3. emails it to NOTIFY_TO, with Reply-To set to the sender's email when one was given.
 *
 * Setup: see README.md in this folder. Cost: none (Apps Script free quotas; consumer Gmail
 * accounts can send to 100 recipients a day, per Google's Apps Script quotas page).
 */
const NOTIFY_TO = 'waynemcc@wamware.com';
const SHEET_NAME = 'GeezerGeek Feedback';

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p['bot-field']) return ok_();                       // honeypot: a bot filled the hidden field
  const message = clip_(p.message, 5000);
  if (!message.trim()) return ok_();
  if (tooMany_()) return ok_();

  const row = {
    when: new Date(),
    app: clip_(p.app || p['app-picked'], 120),
    kind: clip_(p.kind, 20),
    name: clip_(p.name, 120),
    email: clip_(p.email, 200),
    message: message,
    device: clip_(p.device, 400),
  };

  try { sheet_().appendRow([row.when, row.app, row.kind, row.name, row.email, row.message, row.device]); }
  catch (err) { console.error('sheet: ' + err); }          // never let the log stop the email

  const replyOk = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(row.email);
  const body = [
    'App:     ' + (row.app || '—'),
    'Kind:    ' + (row.kind || '—'),
    'From:    ' + (row.name || '(no name)') + (row.email ? ' <' + row.email + '>' : ''),
    '',
    row.message,
    '',
    '—',
    'Device:  ' + (row.device || '—'),
    'Sent from https://geezer-geek-pilot-control-panel.netlify.app/feedback/',
  ].join('\n');
  const opts = { to: NOTIFY_TO, subject: '[GGP feedback] ' + (row.kind || 'Note') + ' — ' + (row.app || 'app'),
                 body: body, name: 'GeezerGeek Pilot Apps' };
  if (replyOk) opts.replyTo = row.email;
  MailApp.sendEmail(opts);
  return ok_();
}

// Opening the web app URL in a browser shows this, which is a quick way to check the deployment.
function doGet() {
  return ContentService.createTextOutput('GeezerGeek feedback mailer is running.');
}

// Run once from the editor (Run ▸ testMail) to grant permissions and send yourself a sample.
function testMail() {
  doPost({ parameter: { app: 'Test', kind: 'Other', name: 'Setup test', email: '',
                        message: 'If you can read this, the feedback mailer works.', device: 'Apps Script editor' } });
}

function ok_() { return ContentService.createTextOutput('ok'); }
function clip_(v, n) { return String(v == null ? '' : v).slice(0, n); }

function tooMany_() {
  const cache = CacheService.getScriptCache();
  const key = 'n' + Math.floor(Date.now() / 60000);
  const n = Number(cache.get(key) || 0) + 1;
  cache.put(key, String(n), 120);
  return n > 20;
}

function sheet_() {
  const props = PropertiesService.getScriptProperties();
  let id = props.getProperty('SHEET_ID');
  let ss = null;
  if (id) { try { ss = SpreadsheetApp.openById(id); } catch (err) { ss = null; } }
  if (!ss) {
    ss = SpreadsheetApp.create(SHEET_NAME);
    ss.getSheets()[0].appendRow(['When', 'App', 'Kind', 'Name', 'Email', 'Message', 'Device']);
    ss.getSheets()[0].setFrozenRows(1);
    props.setProperty('SHEET_ID', ss.getId());
  }
  return ss.getSheets()[0];
}
