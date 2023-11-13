import puppeteer, { Page } from "puppeteer";
import * as fs from 'fs';
import {MongoClient, Collection, ObjectId} from "mongodb"

const client = new MongoClient("mongodb://admin:Conway4554@129.213.145.51:2727/?authMechanism=DEFAULT");


function delay(time: number) {
    return new Promise(resolve => setTimeout(resolve, time));
}

async function scrape(lang:string)
{
    await client.connect();
    const db = client.db("CodingChallengeBot");
    const collection:Collection = db.collection('Challenges');
    var currentDoc = ""
    var waiting = false
    

    const browser = await puppeteer.launch({ headless: false });
    var page:Page = (await browser.pages())[0]
    await page.setRequestInterception(true);
    page.on('request', request => {
        request.continue();
    });
    page.on('response', async response => {
        if (response.url().includes(`/${lang}/session`)) {
            var r = await response.json()
            //@ts-ignore
            var doc = (await collection.find({"_id": currentDoc}).toArray())[0]
            if (!doc.code)
            {
                doc.code = {}
            }
            doc.code[lang as string] = {setup: r.setup, exampleFixture: r.exampleFixture}
            //@ts-ignore
            await collection.replaceOne({"_id": currentDoc}, doc)
            waiting = false
        }
    });

    var allDocs = await collection.find({"languages": {"$in": [lang]}}).toArray()
    
    for (let index = 0; index < allDocs.length; index++) {
        var doc = allDocs[index]
        currentDoc = doc._id.toString()
        console.log(currentDoc)

        if (doc.code)
        {
            if (doc.code[lang])
            {
                console.log("skipping")
                continue
            }
        }

        if (index % 100 == 0 && index != 0)
        {
            await delay(30000)
        }

        console.log("fetching: " + currentDoc + " index: " + index + ":" + allDocs.length)
        waiting = true
        await page.goto(`https://www.codewars.com/kata/${currentDoc}/train/${lang}`);
        while (waiting)
        {
            await delay(100)
        }
    }

    await browser.close();
    await client.close()
}

scrape("typescript")