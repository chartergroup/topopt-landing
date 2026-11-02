// The contact form of https://topopt.ai/contact/: a Google Apps Script web app that emails each message to the team.
//
// Setup, once: Project Settings -> Script properties -> RECIPIENTS = the team addresses, separated by commas.
// Deploy: Deploy -> New deployment -> type "Web app"; Execute as: Me; Who has access: Anyone.
// The /exec address of the deployment is the action of the form in site/contact/index.html.
// To change the code later and keep that address: Deploy -> Manage deployments -> Edit -> Version: New version.

function doPost(e) {
  const p = (e && e.parameter) || {};
  const result = handle_(p);
  if (p.js === '1') {
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }
  // A browser without JavaScript posts the form itself and lands on this page.
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
