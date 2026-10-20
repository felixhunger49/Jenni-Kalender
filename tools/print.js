// HTML -> PDF (und optional PNG-Vorschau je Seite) mit Chromium/Playwright
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const [html, pdf, pngDir] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(html), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true });
  if (pngDir) {
    fs.mkdirSync(pngDir, { recursive: true });
    const els = await page.$$('.page');
    for (let i = 0; i < els.length; i++) {
      await els[i].screenshot({ path: path.join(pngDir, String(i + 1).padStart(2, '0') + '.png') });
    }
  }
  await browser.close();
})();
