// One-off runtime verification for finesse demo-linear.html
// Uses the Playwright MCP server's own playwright-core + cached chromium.
const path = require('path');
const pw = require('C:/Users/Administrator/AppData/Roaming/npm/node_modules/@playwright/mcp/node_modules/playwright-core');

(async () => {
  const exe = 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe';
  const url = 'file:///D:/Desktop/cc/.claude/skills/finesse-ui/demo-linear.html';
  const browser = await pw.chromium.launch({ executablePath: exe, headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));

  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(900);

  // hero screenshot
  await page.screenshot({ path: 'demo-hero.png' });

  // check the board rendered real tickets + real column counts
  const boardInfo = await page.evaluate(() => {
    const cols = [...document.querySelectorAll('#board .col')].map(c => ({
      label: c.querySelector('.col-head').textContent.trim().replace(/\s+/g, ' '),
      tickets: c.querySelectorAll('.ticket').length
    }));
    const chartLines = document.querySelectorAll('#cycleChart path, #cycleChart circle').length;
    const total = document.getElementById('statTotal').textContent;
    const vel = document.getElementById('statVel').textContent;
    const pct = document.getElementById('statPct').textContent;
    return { cols, chartLines, total, vel, pct, tickerIn: document.querySelector('.hero .ticket.in') !== null };
  });

  // filter interaction
  const filterOk = await page.evaluate(() => {
    const f = document.getElementById('issueFilter');
    f.value = 'offline'; f.dispatchEvent(new Event('input', { bubbles: true }));
    const counts = [...document.querySelectorAll('#board .col .count')].map(e => e.textContent);
    return counts; // expect [0, 0, 1] (offline appears once, in done)
  });

  // scroll to the chart section and wait for draw-in
  await page.evaluate(() => document.getElementById('analytics').scrollIntoView());
  await page.waitForTimeout(1200);
  await page.screenshot({ path: 'demo-analytics.png' });
  const chartState = await page.evaluate(() => {
    const dl = document.getElementById('delLine');
    const pa = document.querySelector('.plan-line');
    return { delOffset: dl ? dl.style.strokeDashoffset : null,
             areaVis: getComputedStyle(document.querySelector('.area-fill')).opacity,
             stats: [statTotal.textContent, statVel.textContent, statPct.textContent] };
  });

  // pricing toggle
  const priceToggle = await page.evaluate(() => {
    const monthly = document.querySelector('[data-cycle="monthly"]');
    monthly.click();
    return [...document.querySelectorAll('[data-price]')].map(e => e.textContent).join(',');
  });

  // reduced-motion: reload with emulateMedia and confirm final states land
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.reload({ waitUntil: 'load' });
  await page.waitForTimeout(400);
  const rmState = await page.evaluate(() => {
    const dl = document.getElementById('delLine');
    const tk = [...document.querySelectorAll('.ticket')];
    const reveal = [...document.querySelectorAll('.reveal')];
    return { delOffset: dl ? dl.style.strokeDashoffset : null,
      areaVis: getComputedStyle(document.querySelector('.area-fill')).opacity,
      ticketsShown: tk.filter(t => getComputedStyle(t).opacity === '1').length + '/' + tk.length,
      revealsShown: reveal.filter(r => getComputedStyle(r).opacity === '1').length + '/' + reveal.length,
      stats: [statTotal.textContent, statVel.textContent, statPct.textContent] };
  });

  await browser.close();

  console.log(JSON.stringify({
    boardInfo, filterOk, chartState, priceToggle, rmState, errors
  }, null, 2));
  console.log('ERRORS:', errors.length);
})().catch(e => { console.error('FATAL', e); process.exit(1); });
