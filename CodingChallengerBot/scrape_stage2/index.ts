import puppeteer from "puppeteer";
import * as fs from 'fs';

function delay(time: number) {
    return new Promise(resolve => setTimeout(resolve, time));
}

(async () => {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    await page.setRequestInterception(true);
    page.on('request', request => {
        request.continue();
    });
    page.on('response', async response => {
        if (response.url().includes("/python/session")) {
            var r = await response.json()
            fs.writeFileSync("json.json", JSON.stringify({setup: r.setup, exampleFixture: r.exampleFixture}))
        }
    });
    await page.goto('https://www.codewars.com/kata/5818d00a559ff57a2f000082/train/python');
    await delay(2000)
    await browser.close();
})();