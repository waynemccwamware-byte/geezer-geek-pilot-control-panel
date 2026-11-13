// v1.23 (13-Nov-2026): /reference serves the "GeezerGeek Coach Reference Materials" Google Doc as a PDF,
// shown inline in the browser's own PDF viewer — print layout, white pages, and on iPhone it stays out of
// the Google Docs app (which can open in dark theme / mobile layout). Google Docs has no URL parameter for
// Print layout or light theme, so the PDF export is the only way to fix both. The export is fetched live
// on each open (5-min cache), so edits to the Doc show up without touching this site.
// Google's export URL itself is sent as a download (Content-Disposition: attachment); this function
// re-serves it inline. If the export fails, it falls back to the Doc's /preview page.
const DOC_ID = '1chfDa3JBCjsGykGjwrAFwOqMAS7d3_dIY9ieROLCIyU';
const EXPORT_URL = `https://docs.google.com/document/d/${DOC_ID}/export?format=pdf`;
const FALLBACK_URL = `https://docs.google.com/document/d/${DOC_ID}/preview`;

export default async () => {
  try {
    const r = await fetch(EXPORT_URL, { redirect: 'follow' });
    const type = r.headers.get('content-type') || '';
    if (r.ok && type.includes('pdf')) {
      return new Response(r.body, {
        headers: {
          'content-type': 'application/pdf',
          'content-disposition': 'inline; filename="GeezerGeek-Coach-Reference-Materials.pdf"',
          'cache-control': 'public, max-age=300',
        },
      });
    }
  } catch (e) { /* fall through */ }
  return Response.redirect(FALLBACK_URL, 302);
};

export const config = { path: '/reference' };
