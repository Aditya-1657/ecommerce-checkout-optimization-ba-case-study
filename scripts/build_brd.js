const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Header, Footer,
  AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
} = require("docx");

const W = 9638; // A4 content width in DXA (2 cm margins)
const NAVY = "1F3A5F";
const border = { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };

function runs(text, base = {}) {
  // supports **bold** segments
  return text.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map(s =>
    s.startsWith("**") ? new TextRun({ text: s.slice(2, -2), bold: true, ...base }) : new TextRun({ text: s, ...base }));
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o.run || {}), spacing: { after: 100, line: 276 }, ...(o.p || {}) });
const H1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const BUL = t => new Paragraph({ numbering: { reference: "bul", level: 0 }, children: runs(t), spacing: { after: 60, line: 264 } });
const NUM = t => new Paragraph({ numbering: { reference: "num", level: 0 }, children: runs(t), spacing: { after: 60, line: 264 } });
const CAP = t => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: t, italics: true, size: 18, color: "555555" })] });

function img(file, wpx) {
  const buf = fs.readFileSync(file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 40 },
    children: [new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: Math.round(wpx * h / w) },
      altText: { title: file, description: file, name: file } })] });
}

function cell(text, w, o = {}) {
  const paras = String(text).split("\n").map(line => new Paragraph({
    spacing: { after: 20 }, alignment: o.align || AlignmentType.LEFT,
    children: runs(line, { size: 18, color: o.color, bold: o.bold }) }));
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, children: paras,
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 }, verticalAlign: "top" });
}
function table(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], { fill: NAVY, color: "FFFFFF", bold: true })) }),
      ...rows.map((r, ri) => new TableRow({ children: r.map((c, i) => cell(c, widths[i], { fill: ri % 2 ? "F3F6FA" : undefined })) })),
    ] });
}
const GAP = () => new Paragraph({ spacing: { after: 120 }, children: [] });

const children = [];
const add = (...x) => children.push(...x);

// ---------- cover ----------
add(
  new Paragraph({ spacing: { before: 1800, after: 120 }, children: [new TextRun({ text: "BUSINESS REQUIREMENTS DOCUMENT", bold: true, size: 22, color: "777777", characterSpacing: 40 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Checkout Optimisation Programme", bold: true, size: 52, color: NAVY })] }),
  new Paragraph({ spacing: { after: 400 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: "C8483B", space: 8 } },
    children: [new TextRun({ text: "Reducing cart abandonment at the payment stage for an online retail store", size: 26, color: "444444" })] }),
  table(["Field", "Detail"], [
    ["Document ID", "BRD-CHK-001"],
    ["Version / status", "1.0 / Draft for stakeholder review"],
    ["Prepared by", "[Your Name], Business Analyst"],
    ["Date", "November 2026"],
    ["Project type", "Portfolio case study. The business, the data and the figures are simulated."],
    ["Related files", "analysis/Checkout_Funnel_Analysis.xlsx, sql/02_funnel_analysis.sql, docs/User_Stories.md"],
  ], [2400, 7238]),
  new Paragraph({ children: [new PageBreak()] }),
);

// ---------- 1 exec summary ----------
add(H1("1. Executive summary"),
  P("Of every 100 shoppers who add something to the basket, only about 21 complete the purchase. The other 79 leave somewhere along a seven-screen checkout. This document sets out why they leave, what the business should change, and how we will know the change worked."),
  P("I analysed 25,000 simulated cart sessions covering July to September 2026. Three findings drive the recommendations:"),
  NUM("**The payment stage is where the most committed shoppers are lost.** Of the 10,383 sessions that reached Payment Details, 5,065 (48.8%) never completed. The final step, gateway authorisation, has the worst drop rate in the funnel at 32.5%. About $424,000 of cart value was lost there in the quarter."),
  NUM("**Mobile is the weakest channel.** Mobile is 62% of cart traffic but converts at 16.9%, against 29.5% on desktop. Only 61% of mobile sessions that reach the gateway get through it."),
  NUM("**A forced account wall is the second big leak.** New customers pass the login step at 66%, returning customers at 88%. This step alone lost 5,017 sessions, 25.5% of all abandonment."),
  P("The proposal is to move from seven screens to five: guest checkout by default, delivery cost shown in the basket, one combined contact-address-delivery page, Apple Pay and Google Pay, in-page 3-D Secure 2 authentication, and a proper recovery path when a card is declined. Under cautious assumptions the model projects a rise in cart-to-order conversion from 21.3% to about 26.4%, worth roughly $110,000 of extra revenue per quarter at current traffic. These recovery rates are assumptions, and the plan therefore uses A/B testing to confirm them before full rollout."),
);

// ---------- 2 business problem ----------
add(H1("2. Business problem and objectives"),
  H2("2.1 Problem statement"),
  P("The store is losing a large share of ready-to-buy customers at checkout, and most of that loss happens once the shopper has already entered an address and chosen delivery. These shoppers have shown clear intent, so each one lost is expensive. The business has traffic. What it lacks is a checkout that lets that traffic pay."),
  H2("2.2 Business objectives"),
  table(["#", "Objective", "Baseline", "Target (12 weeks after full rollout)"], [
    ["O1", "Raise cart-to-order conversion", "21.3%", "26.0% or higher"],
    ["O2", "Cut payment-stage abandonment (Payment Details to Confirmed)", "48.8%", "40% or lower"],
    ["O3", "Close the mobile gap: gateway pass rate on mobile", "61.2%", "70% or higher"],
    ["O4", "Improve the pass rate of new customers at the login step", "66.2%", "80% or higher"],
    ["O5", "Payment page load time, 75th percentile on mobile", "4.9 sec (simulated)", "3.0 sec or less"],
  ], [600, 4300, 2200, 2538]),
  P("Targets are working hypotheses drawn from the scenario model in the Excel workbook. They should be revisited with the product owner once the first A/B test reads out.", { run: { italics: true, size: 18 } }),
);

// ---------- 3 scope ----------
add(H1("3. Scope"),
  H2("3.1 In scope"),
  BUL("Web checkout (desktop, tablet, mobile web) from the basket page to the order confirmation page"),
  BUL("Guest checkout and optional account creation after purchase"),
  BUL("Delivery cost estimate in the basket and a combined contact, address and delivery page"),
  BUL("Apple Pay, Google Pay, card (inline fields) and PayPal"),
  BUL("3-D Secure 2 handling, decline messaging and retry"),
  BUL("Checkout analytics and the dashboard that tracks the KPIs above"),
  H2("3.2 Out of scope"),
  BUL("Native mobile apps (a later phase once the web results are known)"),
  BUL("Changes to pricing, promotions, loyalty or product pages"),
  BUL("Buy-now-pay-later providers (candidate for a future release)"),
  BUL("Replacing the payment service provider (PSP)"),
  BUL("Abandoned-cart email campaigns (useful, but a separate marketing workstream)"),
);

// ---------- 4 stakeholders ----------
add(H1("4. Stakeholders"),
  table(["Stakeholder", "Role in this project", "What they care about"], [
    ["Head of E-commerce (sponsor)", "Approves scope, budget and targets", "Revenue, conversion rate, delivery date"],
    ["Product Owner, Checkout", "Owns the backlog and prioritisation", "Clear, testable stories; a realistic roadmap"],
    ["UX / UI Designer", "Designs the TO-BE screens", "Usability on mobile; accessibility"],
    ["Engineering Lead", "Estimates and delivers the build", "Clear requirements, limited rework, tech debt"],
    ["QA Lead", "Test planning and sign-off", "Acceptance criteria that can be tested"],
    ["Payments / Finance Manager", "PSP relationship, reconciliation, fees", "Authorisation rates, chargebacks, fees"],
    ["Risk and Fraud Analyst", "Fraud rules and 3-D Secure policy", "Fraud rate must not rise with guest checkout"],
    ["Customer Service Manager", "Handles payment and order queries", "Fewer failed-payment tickets"],
    ["Data / Analytics", "Tracking plan and A/B test analysis", "Clean event data, valid experiments"],
    ["Legal / Compliance", "Privacy, PCI DSS, strong customer authentication", "Regulatory compliance"],
  ], [2700, 3200, 3738]),
);

// ---------- 5 current state ----------
add(new Paragraph({ children: [new PageBreak()] }),
  H1("5. Current-state analysis (AS-IS)"),
  H2("5.1 Current checkout flow"),
  P("Today a shopper moves through seven screens. An account is mandatory, delivery cost appears for the first time on screen four, and payment is limited to card and PayPal with manual entry. Percentages on the arrows show the share of sessions that continue to the next step."),
  img("images/05_as_is_flow.png", 330),
  CAP("Figure 1. AS-IS checkout flow with step pass rates (simulated data)"),
  H2("5.2 Where the funnel leaks"),
  img("images/01_funnel.png", 560),
  CAP("Figure 2. Sessions reaching each step. Payment-related steps are highlighted."),
  table(["Step", "Reached", "Lost at step", "Drop rate", "% of all lost", "Lost cart value"], [
    ["1 Cart", "25,000", "5,637", "22.5%", "28.6%", "$459,305"],
    ["2 Login / Create account", "19,363", "5,017", "25.9%", "25.5%", "$412,704"],
    ["3 Shipping address", "14,346", "1,798", "12.5%", "9.1%", "$149,276"],
    ["4 Delivery options", "12,548", "2,165", "17.3%", "11.0%", "$144,524"],
    ["5 Payment details", "10,383", "2,505", "24.1%", "12.7%", "$206,817"],
    ["6 Gateway authorisation", "7,878", "2,560", "32.5%", "13.0%", "$217,569"],
    ["7 Order confirmed", "5,318", "-", "-", "-", "-"],
  ], [2600, 1200, 1400, 1250, 1500, 1688]),
  P("**How to read this.** Losing people at the cart is normal, since many are comparing prices or browsing. The losses at steps 5 and 6 are different. Those shoppers have typed an address, accepted a delivery price and opened the payment form. Together the two payment steps account for 25.7% of all lost sessions but 48.8% of everyone who reached payment, and step 6 has the highest drop rate of any step.", { p: { spacing: { before: 120, after: 100 } } }),
  H2("5.3 Key findings and evidence"),
  table(["Ref", "Finding", "Evidence (from the dataset)"], [
    ["F1", "Half of the shoppers who reach payment do not finish", "5,065 of 10,383 lost (48.8%); $424,385 cart value"],
    ["F2", "Authentication and gateway problems dominate the last step", "3-D Secure timeout/fail 34.4%, card declined 22.5%, gateway error or expired session 26.6%, redirect abandoned 16.5% of gateway exits"],
    ["F3", "Mobile converts far below desktop", "Cart-to-order: mobile 16.9%, tablet 23.8%, desktop 29.5%. Gateway pass: mobile 61.2%, desktop 76.7%"],
    ["F4", "Forced account creation pushes new customers away", "Login step pass rate: new 66.2%, returning 88.2%. 5,017 sessions lost"],
    ["F5", "Late delivery-cost reveal", "Step 4 to 5 pass rate: free shipping 91.3%, paid shipping 75.8%. 63% of delivery exits tagged \"shipping cost too high\""],
    ["F6", "Slow payment page", "Step 5 to 6 pass rate: under 3 sec 81.1%, 3 to 4.5 sec 77.6%, over 4.5 sec 67.5%"],
    ["F7", "Unmet demand for wallets", "29.2% of exits at Payment Details tagged \"wanted wallet option\""],
  ], [600, 3500, 5538]),
  GAP(),
  img("images/03_device.png", 400),
  CAP("Figure 3. Conversion by device"),
  img("images/04_gateway_reasons.png", 430),
  CAP("Figure 4. Reasons captured at gateway exit"),
  H2("5.4 Root causes"),
  BUL("**Too much friction for card entry on a phone.** Long forms, manual card typing and a redirect page make mobile payment slow and error-prone."),
  BUL("**Authentication handled the old way.** A full-page redirect or a challenge that times out loses shoppers who would otherwise pay."),
  BUL("**Poor failure recovery.** When a card is declined or the gateway times out, the shopper gets little guidance and often loses the form data."),
  BUL("**Commitment is demanded before value is shown.** The shopper must create an account and only then learns the delivery cost."),
);

// ---------- 6 TO-BE ----------
add(new Paragraph({ children: [new PageBreak()] }),
  H1("6. Proposed solution (TO-BE)"),
  P("The TO-BE flow removes the account wall, shows cost earlier, merges three screens into one, and gives the shopper faster ways to pay. Express wallet buttons let a returning mobile shopper skip the form entirely."),
  img("images/06_to_be_flow.png", 480),
  CAP("Figure 5. TO-BE checkout flow"),
  table(["Change", "Addresses", "Expected effect"], [
    ["Guest checkout as default; account offered after purchase", "F4", "More new customers pass the login step"],
    ["Delivery estimate and free-shipping progress bar in the basket", "F5", "No surprise at step 4; fewer cost-driven exits"],
    ["One page for contact, address and delivery; address autocomplete; 12 fields cut to 7", "F3, F4", "Shorter path, especially on mobile"],
    ["Apple Pay and Google Pay on basket and payment pages", "F3, F7", "Skip typing; fewer abandoned payment forms"],
    ["Inline card fields, correct mobile keyboards, saved methods", "F3, F6", "Faster, fewer typing errors"],
    ["3-D Secure 2 with in-page challenge; no full-page redirect", "F2", "Fewer authentication timeouts and redirect exits"],
    ["Clear decline messages with retry or switch method; form data kept", "F2", "Recover shoppers whose card fails"],
    ["Payment page performance budget", "F6", "Remove the penalty for slow pages"],
  ], [4600, 1200, 3838]),
);

// ---------- 7 business requirements ----------
add(H1("7. Business requirements"),
  P("Priority uses MoSCoW: Must, Should, Could. Each requirement points back to the finding it responds to."),
  table(["ID", "Business requirement", "Finding", "Priority"], [
    ["BR-01", "Customers must be able to buy without creating an account.", "F4", "Must"],
    ["BR-02", "Customers must see delivery cost and any free-shipping threshold before starting checkout.", "F5", "Must"],
    ["BR-03", "The path from basket to payment must contain fewer screens and fields than today.", "F3, F4", "Must"],
    ["BR-04", "Customers on supported devices must be able to pay with Apple Pay or Google Pay.", "F3, F7", "Must"],
    ["BR-05", "Authentication must complete inside the checkout page where possible.", "F2", "Must"],
    ["BR-06", "A failed payment must not lose the order, and the customer must be told clearly how to proceed.", "F2", "Must"],
    ["BR-07", "The payment page must meet a defined performance budget on mobile networks.", "F6", "Should"],
    ["BR-08", "Guest customers should be able to create an account after purchase in one step.", "F4", "Should"],
    ["BR-09", "Logged-in customers should be able to reuse saved payment methods.", "F3", "Could"],
    ["BR-10", "Every checkout step must be tracked so conversion can be measured and experiments run.", "All", "Must"],
    ["BR-11", "Fraud and chargeback rates must not rise as a result of the changes.", "Risk", "Must"],
  ], [900, 6000, 1300, 1438]),
);

// ---------- 8 functional ----------
add(H1("8. Functional requirements"),
  table(["ID", "Requirement", "Traces to"], [
    ["FR-01", "The checkout entry screen shows \"Continue as guest\" as the primary action, with \"Sign in\" as secondary. Only an email address is required for guests.", "BR-01"],
    ["FR-02", "If a guest enters an email that already has an account, the system offers sign-in but does not block checkout.", "BR-01"],
    ["FR-03", "After order confirmation, the system offers \"Save my details\" and creates the account with one action by setting a password, using data already entered.", "BR-08"],
    ["FR-04", "The basket page shows an estimated delivery cost based on postcode or ZIP, and a progress bar showing how much more is needed for free shipping.", "BR-02"],
    ["FR-05", "Contact, delivery address and delivery method appear on a single page. Address fields use autocomplete and inline validation. Required fields are reduced from 12 to 7.", "BR-03"],
    ["FR-06", "Apple Pay and Google Pay buttons appear on the basket and payment pages when the device and browser support them. The wallet returns contact and address details so no further form is needed.", "BR-04"],
    ["FR-07", "Card details use PSP-hosted inline fields: numeric keypad on mobile, card-type detection, number-format check, and browser autofill support.", "BR-03, BR-04"],
    ["FR-08", "PayPal opens in an in-context pop-up or overlay rather than a full-page redirect, where PayPal supports it.", "BR-05"],
    ["FR-09", "The system requests 3-D Secure 2 frictionless authentication first. If a challenge is needed it appears inside the page as an overlay, with a visible timer and a cancel option that returns the shopper to payment selection.", "BR-05"],
    ["FR-10", "Gateway decline codes are mapped to plain-language messages (for example insufficient funds, card expired, bank declined). The shopper keeps all entered data and can retry or switch method.", "BR-06"],
    ["FR-11", "Basket and checkout session persist for at least 60 minutes. A warning appears 5 minutes before expiry. Payment submissions are idempotent so a retry never creates a duplicate order.", "BR-06"],
    ["FR-12", "Logged-in customers can save a card or wallet using PSP tokens. No full card number is stored by the retailer.", "BR-09"],
    ["FR-13", "The order summary stays visible on every step and collapses on small screens.", "BR-03"],
    ["FR-14", "The system records an event for each step view, step completion, error and exit with device, source and customer type, and stores the exit tag when known.", "BR-10"],
    ["FR-15", "Each major change is controlled by a feature flag so it can be A/B tested and switched off quickly.", "BR-10, BR-11"],
    ["FR-16", "Fraud rules continue to run on guest and wallet orders. Orders above a configurable value trigger extra verification.", "BR-11"],
  ], [900, 7000, 1738]),
);

// ---------- 9 NFR ----------
add(H1("9. Non-functional requirements"),
  table(["ID", "Category", "Requirement"], [
    ["NFR-01", "Performance", "Payment page Largest Contentful Paint of 2.5 sec or less (75th percentile) on a mid-range phone on 4G."],
    ["NFR-02", "Availability", "Checkout and payment services available 99.9% of the time, excluding planned maintenance."],
    ["NFR-03", "Security", "No card data touches retailer servers (PSP hosted fields, PCI DSS SAQ-A scope). TLS 1.2 or higher."],
    ["NFR-04", "Compliance", "Strong customer authentication rules (for example PSD2 in the EU/UK) are respected. Guest email use follows the privacy policy and consent rules."],
    ["NFR-05", "Accessibility", "Checkout meets WCAG 2.2 level AA: keyboard navigation, labels, error messages, contrast."],
    ["NFR-06", "Compatibility", "Latest two versions of Chrome, Safari, Edge and Firefox; iOS 16+ and Android 11+."],
    ["NFR-07", "Reliability", "Payment retries are idempotent; no duplicate charges."],
    ["NFR-08", "Observability", "Errors from the PSP are logged with codes and alert the on-call team when failure rate crosses a set threshold."],
  ], [900, 1700, 7038]),
);

// ---------- 10 assumptions etc ----------
add(H1("10. Assumptions, constraints and dependencies"),
  H2("10.1 Assumptions"),
  BUL("The current PSP supports Apple Pay, Google Pay and 3-D Secure 2 (to be confirmed in discovery)."),
  BUL("Exit tags in the dataset come from existing app events and are reasonably accurate. A survey sample should be added to confirm them."),
  BUL("Recovery rates in the scenario model (guest 20%, shipping estimate 15%, wallets 20%, authentication 25%) are estimates for planning and not forecasts."),
  BUL("Traffic mix and average order value stay close to the Q3 2026 sample."),
  H2("10.2 Constraints"),
  BUL("Payment card data rules (PCI DSS) limit how card fields can be built."),
  BUL("One checkout squad of about 5 engineers is available, so the work is phased."),
  BUL("The peak sales period needs a release freeze, so the schedule avoids it."),
  H2("10.3 Dependencies"),
  BUL("Apple Pay merchant verification and Google Pay merchant registration"),
  BUL("PSP configuration for 3-D Secure 2 and decline-code data"),
  BUL("Analytics team capacity for the tracking plan and experiment design"),
  BUL("UX design of the combined contact, address and delivery page"),
);

// ---------- 11 risks ----------
add(H1("11. Risks and mitigations"),
  table(["Risk", "Likelihood", "Impact", "Mitigation"], [
    ["Fraud rises with guest and wallet orders", "Medium", "High", "Keep fraud rules active; 3-D Secure 2 risk-based; monitor chargebacks weekly; kill switch via feature flag"],
    ["Uplift smaller than modelled", "Medium", "Medium", "A/B test each phase; stage investment; use the pessimistic case for planning"],
    ["PSP lacks required wallet or 3-D Secure 2 features", "Low", "High", "Confirm in discovery week 1; shortlist alternative only if needed"],
    ["Fewer account sign-ups hurt marketing and loyalty", "Medium", "Medium", "Post-purchase account creation; track sign-up rate as a guardrail"],
    ["Tracking changes break the baseline", "Medium", "Medium", "Freeze baseline definitions; run old and new tracking in parallel for two weeks"],
    ["Scope creep (BNPL, new payment types)", "Medium", "Medium", "Keep out-of-scope list; handle new asks through change control"],
    ["Regulatory change to authentication rules", "Low", "Medium", "Compliance review at design and before launch"],
  ], [3000, 1100, 1000, 4538]),
);

// ---------- 12 success ----------
add(H1("12. Success metrics and measurement plan"),
  table(["Metric", "Type", "Definition", "Source"], [
    ["Cart-to-order conversion", "Primary", "Orders divided by cart sessions", "Analytics"],
    ["Payment-stage abandonment", "Primary", "Sessions reaching Payment Details but not confirmed", "Analytics"],
    ["Mobile gateway pass rate", "Secondary", "Mobile sessions confirmed divided by mobile sessions reaching gateway", "Analytics"],
    ["New-customer login-step pass rate", "Secondary", "New sessions passing step 2 to 3", "Analytics"],
    ["Wallet share of orders", "Secondary", "Orders paid by Apple Pay or Google Pay", "PSP report"],
    ["Fraud and chargeback rate", "Guardrail", "Chargebacks as a share of orders", "Finance / PSP"],
    ["Average order value", "Guardrail", "Mean value of completed orders", "Analytics"],
    ["Post-purchase account creation", "Guardrail", "Guest orders followed by account creation", "Analytics"],
    ["Payment-failure support tickets", "Guardrail", "Tickets tagged payment failed", "Service desk"],
  ], [2700, 1200, 4038, 1700]),
  H2("12.1 Experiment design"),
  BUL("Randomise at session level, 50% old flow and 50% new flow, per phase."),
  BUL("A lift of 2 percentage points on a 21% base needs roughly 6,800 sessions per arm (80% power, 5% significance). At current traffic that is about 7 weeks for the test to run."),
  BUL("Run for whole weeks to cover weekday and weekend behaviour. Avoid promotional periods."),
  BUL("Stop early only if a guardrail metric (fraud, errors) breaches its limit."),
);

// ---------- 13 rollout ----------
add(H1("13. Delivery approach"),
  table(["Phase", "Weeks", "Scope", "Why this order"], [
    ["1. Quick wins", "1 to 4", "Delivery estimate in basket; decline messages; payment page performance work; full step tracking", "Low effort, addresses F5, F6 and gives the baseline data"],
    ["2. Friction removal", "5 to 10", "Guest checkout; combined contact, address and delivery page; post-purchase account creation", "Addresses the largest top-of-funnel leak (F4)"],
    ["3. Payment upgrade", "11 to 16", "Apple Pay and Google Pay; inline card fields; 3-D Secure 2 in-page; saved methods", "Biggest build and PSP dependency, so it follows discovery"],
    ["4. Review", "17 to 20", "Results review, tune thresholds, plan next backlog", "Confirm targets and decide next steps"],
  ], [1700, 900, 4000, 3038]),
);

// ---------- 14 traceability ----------
add(H1("14. Traceability matrix"),
  P("Links each finding to the requirements and user stories that address it. The user stories are in docs/User_Stories.md."),
  table(["Finding", "Business req.", "Functional req.", "User stories"], [
    ["F1 Payment abandonment", "BR-05, BR-06", "FR-09, FR-10, FR-11", "US-09, US-10, US-11"],
    ["F2 Authentication problems", "BR-05, BR-06", "FR-08, FR-09, FR-10", "US-08, US-09, US-10"],
    ["F3 Mobile gap", "BR-03, BR-04, BR-09", "FR-05, FR-06, FR-07, FR-12, FR-13", "US-05, US-06, US-07, US-15"],
    ["F4 Account wall", "BR-01, BR-08", "FR-01, FR-02, FR-03", "US-01, US-02, US-03"],
    ["F5 Late cost reveal", "BR-02", "FR-04", "US-04"],
    ["F6 Slow payment page", "BR-07", "NFR-01", "US-12"],
    ["F7 Wallet demand", "BR-04", "FR-06", "US-06"],
    ["Measurement and risk", "BR-10, BR-11", "FR-14, FR-15, FR-16", "US-13, US-14"],
  ], [2500, 2000, 2700, 2438]),
);

// ---------- 15 glossary ----------
add(H1("15. Glossary"),
  table(["Term", "Meaning"], [
    ["Cart abandonment", "A shopper adds items to the basket but leaves without paying."],
    ["PSP", "Payment service provider, the company that processes card and wallet payments."],
    ["3-D Secure (3DS) / 3DS2", "Card-holder authentication step required by many banks. Version 2 can run without a challenge for low-risk payments."],
    ["SCA", "Strong customer authentication, a regulatory requirement in some regions."],
    ["Guest checkout", "Buying without creating an account."],
    ["Wallet", "Apple Pay or Google Pay: stored cards approved with biometrics."],
    ["MoSCoW", "Must, Should, Could, Won't prioritisation method."],
    ["Idempotent", "A request that has the same effect if sent twice, so a retry cannot create a second charge."],
  ], [2600, 7038]),
);

// ---------- 16 sign-off ----------
add(H1("16. Approval"),
  table(["Name", "Role", "Decision", "Date"], [
    ["", "Head of E-commerce (sponsor)", "", ""],
    ["", "Product Owner, Checkout", "", ""],
    ["", "Engineering Lead", "", ""],
    ["", "Payments / Finance Manager", "", ""],
  ], [2800, 3200, 1800, 1838]),
);

const doc = new Document({
  creator: "Business Analyst", title: "Business Requirements Document - Checkout Optimisation",
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Arial", size: 30, bold: true, color: NAVY },
        paragraph: { spacing: { before: 320, after: 140 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Arial", size: 23, bold: true, color: "2D5C8A" },
        paragraph: { spacing: { before: 220, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 300 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "BRD-CHK-001  |  Checkout Optimisation Programme", size: 16, color: "888888" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Page ", size: 16, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "888888" })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("docs/BRD_Checkout_Optimisation.docx", b); console.log("brd saved"); });
