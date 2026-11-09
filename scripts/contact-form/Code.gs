// The contact forms of https://topopt.ai/contact/ and of the charter site: one Google Apps Script web app.
// - The topopt.ai form: each message goes by email to RECIPIENTS. Nothing about it changed.
// - The charter form sends the field form=charter: each message goes by email to CHARTER_RECIPIENTS, with all its fields.
//
// Setup, once: Project Settings -> Script properties:
//   RECIPIENTS = the topopt.ai team addresses, separated by commas.
//   CHARTER_RECIPIENTS = the addresses for the charter form, separated by commas.
//   CHARTER_SITE_URL (optional) = the address of the charter site, for the link back on the page that a browser without
//   JavaScript shows.
// Deploy: Deploy -> New deployment -> type "Web app"; Execute as: Me; Who has access: Anyone.
// The /exec address of the deployment is the action of both forms.
// To change the code later and keep that address: Deploy -> Manage deployments -> Edit -> Version: New version.
// The script uses only mail and script properties, so a new version needs no new permission.

const CHARTER_RUN_SIZES = ['10-100', '101-1000', '1001-10000', '10000+'];

function doPost(e) {
  const p = (e && e.parameter) || {};
  const charter = p.form === 'charter';
  const result = charter ? handleCharter_(p) : handle_(p);
  if (p.js === '1') {
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }
  // A browser without JavaScript posts the form itself and lands on this page.
  if (charter) {
    const text = result.ok
      ? 'Thank you. We will be in touch by email soon.'
      : 'The form was not sent. Please go back and try again in a few minutes.';
    const site = PropertiesService.getScriptProperties().getProperty('CHARTER_SITE_URL');
    const back = site ? '<p><a href="' + escapeHtml_(site) + '" target="_top">Back to charter</a></p>' : '';
    return HtmlService.createHtmlOutput('<p>' + text + '</p>' + back);
  }
  const text = result.ok
    ? 'Thank you. Your message is on its way, and we will reply by email.'
    : 'The message was not sent. Please go back and try again in a few minutes.';
  return HtmlService.createHtmlOutput('<p>' + text + '</p><p><a href="https://topopt.ai/" target="_top">Back to topopt.ai</a></p>');
}

function doGet() {
  return ContentService.createTextOutput('The topopt.ai contact form posts here.');
}

function handle_(p) {
  // A person leaves the hidden field "website" empty. A bot that fills every field gets "ok", and nothing is sent.
  if (p.website) return { ok: true };
  const name = String(p.name || '').trim();
  const email = String(p.email || '').trim();
  const message = String(p.message || '').trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !message) return { ok: false, error: 'invalid' };
  const recipients = PropertiesService.getScriptProperties().getProperty('RECIPIENTS');
  if (!recipients) return { ok: false, error: 'not configured' };
  // MailApp counts recipients per day; refuse rather than fail halfway.
  if (MailApp.getRemainingDailyQuota() < recipients.split(',').length) return { ok: false, error: 'quota' };
  MailApp.sendEmail({
    to: recipients,
    replyTo: email,
    name: 'topopt.ai contact form',
    subject: 'topopt.ai: a message from ' + (name || email),
    body: 'Name: ' + (name || '-') + '\nEmail: ' + email + '\n\n' + message,
  });
  return { ok: true };
}

function handleCharter_(p) {
  // The same hidden field as on topopt.ai catches simple bots.
  if (p.website) return { ok: true };
  const email = String(p.email || '').trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { ok: false, error: 'invalid' };
  const runSize = String(p.run_size || '').trim();
  if (runSize && CHARTER_RUN_SIZES.indexOf(runSize) < 0) return { ok: false, error: 'invalid' };
  const recipients = PropertiesService.getScriptProperties().getProperty('CHARTER_RECIPIENTS');
  if (!recipients) return { ok: false, error: 'not configured' };
  // Both forms share the daily mail quota of the account; refuse rather than fail halfway.
  if (MailApp.getRemainingDailyQuota() < recipients.split(',').length) return { ok: false, error: 'quota' };
  MailApp.sendEmail({
    to: recipients,
    replyTo: email,
    name: 'charter contact form',
    subject: 'charter: a message from ' + email,
    body: 'Email: ' + email
      + '\nPhone: ' + (String(p.phone || '').trim() || '-')
      + '\nLink: ' + (String(p.link || '').trim() || '-')
      + '\nProduction run size: ' + (runSize || '-')
      + '\n\nHow can we help:\n' + (String(p.message || '').trim() || '-'),
  });
  return { ok: true };
}

function escapeHtml_(value) {
  return String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
