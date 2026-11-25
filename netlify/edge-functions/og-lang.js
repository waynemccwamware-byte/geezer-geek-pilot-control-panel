// Control Panel v1.37 (25-Nov-2026): a link shared from a Spanish page carries ?lang=es (footer v1.15). Link-preview
// crawlers read only the page's meta tags, so for that address this swaps in the Spanish card (og-image-es.png),
// title and description. Every other request passes straight through. No packages (App Conventions: no npm).
const SWAPS = [
  ['<html lang="en"', '<html lang="es-MX"'],
  ['content="https://geezer-geek-pilot-control-panel.netlify.app/"', 'content="https://geezer-geek-pilot-control-panel.netlify.app/?lang=es"'],
  ['content="GeezerGeek Pilot Apps: free tools for GA pilots"', 'content="Apps de GeezerGeek Pilot: herramientas gratis para pilotos"'],
  ['content="Weather, planning, ATC practice and safety. Free, no signup, nothing to install."', 'content="Meteorología, planeación, práctica de ATC y seguridad. Gratis, sin registro y sin nada que instalar."'],
  ['/og-image.png?', '/og-image-es.png?'],
  ['content="GeezerGeek Pilot Apps: eleven free apps for GA pilots"', 'content="Apps de GeezerGeek Pilot: once apps gratis para pilotos"'],
];

export default async (request, context) => {
  if (new URL(request.url).searchParams.get('lang') !== 'es') return;   // undefined = carry on as usual
  const res = await context.next();
  if (!(res.headers.get('content-type') || '').includes('text/html')) return res;
  let html = await res.text();
  for (const [a, b] of SWAPS) html = html.split(a).join(b);
  const headers = new Headers(res.headers);
  headers.delete('content-length');
  return new Response(html, { status: res.status, headers });
};

export const config = { path: '/' };
