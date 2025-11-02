// server.js  (CommonJS version)
const express = require("express");
const bodyParser = require("body-parser");
const { chromium } = require("playwright");

const app = express();
app.use(bodyParser.json());

let browser, page;

app.post("/mcp", async (req, res) => {
  const { method, params, id } = req.body;

  try {
    switch (method) {
      case "initialize":
        browser = await chromium.launch({ headless: false });
        const context = await browser.newContext();
        page = await context.newPage();
        return res.json({ jsonrpc: "2.0", result: { status: "initialized" }, id });

      case "browser_navigate":
        await page.goto(params.url);
        return res.json({ jsonrpc: "2.0", result: { ok: true }, id });

      case "browser_snapshot":
        const elements = await page.evaluate(() =>
          Array.from(document.querySelectorAll("*")).map((el, i) => ({
            ref: i,
            text: el.innerText,
            role: el.getAttribute("role") || "",
          }))
        );
        return res.json({ jsonrpc: "2.0", result: { elements }, id });

      default:
        return res.json({
          jsonrpc: "2.0",
          error: { code: -32601, message: "Unknown method" },
          id,
        });
    }
  } catch (err) {
    res.json({
      jsonrpc: "2.0",
      error: { code: -32000, message: err.message },
      id,
    });
  }
});

app.listen(8931, () => console.log(" Playwright MCP Server running on port 8931"));
