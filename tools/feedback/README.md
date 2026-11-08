# Feedback mailer (Google Apps Script)

The feedback form (`site/feedback/`) posts each submission to two places:

1. **Netlify Forms**, form `feedback`: the free archive (Netlify → Control Panel project → Forms).
   Netlify's email notifications are a paid feature on Wayne's plan, so they aren't used.
2. **This Apps Script web app** (`Code.gs`), running in Wayne's Google account. It emails each
   submission to waynemcc@wamware.com, with Reply-To set to the sender's email if one was given.
   It also logs the submission to a "GeezerGeek Feedback" Google Sheet, which it creates on first use.

Free: consumer Google accounts may email 100 recipients a day from Apps Script
(developers.google.com/apps-script/quotas, read 07-Nov-2026).

## One-time setup (about 5 minutes)

1. Go to https://script.google.com, signed in to the Google account that should own it, and click **New project**.
2. Name it "GeezerGeek feedback mailer". Replace the editor's contents with `Code.gs` from this folder, then save.
3. In the function menu pick **testMail** and click **Run**. Approve the permission prompts (send email
   as you, create a spreadsheet). A test email arrives, and the sheet appears in Drive.
   - On the "Google hasn't verified this app" screen, click Advanced, then Go to … (unsafe). It is your own script.
4. Click **Deploy ▸ New deployment ▸ Select type ▸ Web app**, and set:
   - Execute as: **Me**
   - Who has access: **Anyone**
5. Click Deploy and copy the **Web app URL** (ends in `/exec`).
6. Put that URL in `MAILER_URL` near the top of the script in `site/feedback/index.html`, then push.

Opening the `/exec` URL in a browser should show "GeezerGeek feedback mailer is running."

## Changing the script later

Edit `Code.gs` here first (it is the master), paste it into the Apps Script editor, then use
**Deploy ▸ Manage deployments ▸ edit ▸ Version: New version**. That keeps the same `/exec` URL.
A *new deployment* gets a new URL, which would then need to go into `MAILER_URL`.
