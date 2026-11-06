# User Stories and Acceptance Criteria

**Project:** Checkout Optimisation Programme  |  **Linked document:** [BRD](BRD_Checkout_Optimisation.docx)
**Estimates** are in story points (Fibonacci) and are my planning guesses, to be replaced by the team's own estimates in refinement.

## How the backlog is organised

| Epic | Goal | Stories |
|---|---|---|
| E1 Guest & account | Remove the account wall | US-01, US-02, US-03 |
| E2 Cost & form friction | Fewer surprises, fewer fields | US-04, US-05 |
| E3 Faster payment | Wallets, cards, PayPal | US-06, US-07, US-08, US-15 |
| E4 Authentication & recovery | Fewer failed payments, easy retry | US-09, US-10, US-11 |
| E5 Performance & measurement | Fast pages, trustworthy data | US-12, US-13, US-14 |

**Release plan:** Phase 1 = US-04 (basic), US-10, US-12, US-13 | Phase 2 = US-01, US-02, US-03, US-05 | Phase 3 = US-06, US-07, US-08, US-09, US-11, US-15 | US-14 runs alongside every phase.

## Summary table

| ID | Story (short) | Epic | Priority | Points | Traces to |
|---|---|---|---|---|---|
| US-01 | Guest checkout | E1 | Must | 8 | BR-01, FR-01 |
| US-02 | Existing-email prompt | E1 | Should | 3 | BR-01, FR-02 |
| US-03 | Create account after purchase | E1 | Should | 5 | BR-08, FR-03 |
| US-04 | Delivery estimate in basket | E2 | Must | 5 | BR-02, FR-04 |
| US-05 | Single page for contact, address, delivery | E2 | Must | 13 | BR-03, FR-05, FR-13 |
| US-06 | Apple Pay / Google Pay | E3 | Must | 13 | BR-04, FR-06 |
| US-07 | Inline card fields, mobile-friendly | E3 | Must | 8 | BR-03, FR-07 |
| US-08 | PayPal without full-page redirect | E3 | Should | 5 | BR-05, FR-08 |
| US-09 | In-page 3-D Secure 2 | E4 | Must | 13 | BR-05, FR-09 |
| US-10 | Clear decline messages and retry | E4 | Must | 5 | BR-06, FR-10 |
| US-11 | Session persistence, no duplicate charge | E4 | Must | 8 | BR-06, FR-11, NFR-07 |
| US-12 | Payment page performance budget | E5 | Should | 8 | BR-07, NFR-01 |
| US-13 | Step-level tracking and dashboard | E5 | Must | 5 | BR-10, FR-14 |
| US-14 | Feature flags and fraud guardrails | E5 | Must | 5 | BR-10, BR-11, FR-15, FR-16 |
| US-15 | Saved payment methods | E3 | Could | 8 | BR-09, FR-12 |

---

## Epic E1: Guest & account

### US-01 Guest checkout
**As a** first-time shopper
**I want to** check out without creating an account
**So that** I can pay quickly without handing over a password.

**Priority:** Must  |  **Points:** 8  |  **Finding:** F4

**Acceptance criteria**
1. **Given** I am on the checkout entry screen, **when** the page loads, **then** "Continue as guest" is the most prominent button and "Sign in" is a secondary link.
2. **Given** I choose guest checkout, **when** I enter a valid email address, **then** I can proceed to the next step without entering a password.
3. **Given** I am a guest, **when** I complete the order, **then** the confirmation email goes to the address I entered and the order can be found by order number and email.
4. **Given** I enter an invalid email format, **when** I leave the field, **then** an inline message explains the problem and the Continue button stays disabled.
5. **Given** the guest flow is switched on by feature flag for 50% of sessions, **when** a session is allocated, **then** the same variant is kept for the whole session.

**Notes:** Marketing consent must be an unticked, optional checkbox.

### US-02 Existing-email prompt
**As a** returning customer who forgot I had an account
**I want to** be offered sign-in when I type my email
**So that** I can use my saved address and cards if I want to.

**Priority:** Should  |  **Points:** 3  |  **Finding:** F4

**Acceptance criteria**
1. **Given** I type an email that matches an existing account, **when** I move to the next field, **then** a non-blocking message offers "Sign in for faster checkout".
2. **Given** that message is shown, **when** I ignore it, **then** I can still continue as a guest.
3. **Given** I choose to sign in, **when** I authenticate successfully, **then** I return to the same step with my basket unchanged.
4. **Given** an email is not registered, **when** I type it, **then** nothing in the interface reveals whether any account exists (to avoid account enumeration where privacy policy requires it).

### US-03 Create account after purchase
**As a** guest who has just ordered
**I want to** save my details with one action
**So that** next time checkout is faster.

**Priority:** Should  |  **Points:** 5  |  **Finding:** F4

**Acceptance criteria**
1. **Given** I am on the confirmation page as a guest, **when** the page loads, **then** I see a "Save my details" panel with a single password field.
2. **Given** I enter a password that meets the policy, **when** I submit, **then** an account is created using my order email, name and address, and the order is linked to it.
3. **Given** I enter a weak password, **when** I submit, **then** an inline message states the rule and no account is created.
4. **Given** I do not use the panel, **when** I leave the page, **then** no account is created and no marketing opt-in is assumed.

---

## Epic E2: Cost & form friction

### US-04 Delivery estimate in basket
**As a** shopper
**I want to** see what delivery will cost before I start checkout
**So that** I am not surprised later.

**Priority:** Must  |  **Points:** 5  |  **Finding:** F5

**Acceptance criteria**
1. **Given** I am on the basket page, **when** I enter a postcode or ZIP, **then** an estimated delivery cost and delivery window appear within 2 seconds.
2. **Given** the free-shipping threshold is $75, **when** my basket is $60, **then** a progress bar reads "Add $15.00 for free delivery".
3. **Given** my basket reaches the threshold, **when** the total updates, **then** the message changes to "You've got free delivery" without a page reload.
4. **Given** the estimate service is unavailable, **when** I view the basket, **then** a generic message "Delivery calculated at next step" appears and checkout is not blocked.
5. **Given** I proceed to the delivery step, **when** the final cost is shown, **then** it matches the estimate (or any difference is explained).

### US-05 Single page for contact, address and delivery
**As a** mobile shopper
**I want to** fill in my contact details, address and delivery choice on one page
**So that** I reach payment with less effort.

**Priority:** Must  |  **Points:** 13  |  **Findings:** F3, F4

**Acceptance criteria**
1. **Given** I reach this page, **when** it loads, **then** it contains email, name, address (with autocomplete), phone and delivery options, and no more than 7 required fields.
2. **Given** I start typing an address, **when** at least 3 characters are entered, **then** matching address suggestions appear and selecting one fills street, city, postcode and region.
3. **Given** I leave a required field empty or invalid, **when** I move away, **then** an inline message appears next to the field, and a summary appears if I press Continue.
4. **Given** I change the address, **when** the delivery options update, **then** prices and dates refresh without losing other entered data.
5. **Given** I am on a screen narrower than 600 px, **when** I view the page, **then** the order summary is collapsed by default and opens with one tap, showing the total.
6. **Given** a browser autofill is available, **when** I use it, **then** all matching fields are filled correctly.
7. **Given** I use only a keyboard or screen reader, **when** I move through the page, **then** every field has a label and a visible focus state (WCAG 2.2 AA).

---

## Epic E3: Faster payment

### US-06 Apple Pay and Google Pay
**As a** mobile shopper with a wallet set up
**I want to** pay with Apple Pay or Google Pay
**So that** I can finish in seconds without typing card details.

**Priority:** Must  |  **Points:** 13  |  **Findings:** F3, F7

**Acceptance criteria**
1. **Given** I use Safari on a device with Apple Pay set up, **when** I view the basket or payment page, **then** an Apple Pay button is shown. **Given** I use Chrome with Google Pay available, **then** a Google Pay button is shown. Unsupported devices see neither button.
2. **Given** I tap a wallet button on the basket page, **when** I authenticate with Face ID, fingerprint or passcode, **then** my contact details and shipping address are returned from the wallet and I do not see the address form.
3. **Given** I choose a shipping option inside the wallet sheet, **when** the sheet updates, **then** the total shown matches the order total on the site.
4. **Given** the wallet payment is approved, **when** the PSP responds, **then** I land on the confirmation page and receive an order email.
5. **Given** I cancel the wallet sheet, **when** I return to the page, **then** my basket and any entered data are unchanged.
6. **Given** the wallet payment is declined, **when** the response arrives, **then** I see a clear message and can pick another method (see US-10).
7. **Given** wallet orders are placed, **when** reports run, **then** orders are tagged by payment method for analysis.

### US-07 Inline card fields, mobile-friendly
**As a** shopper paying by card on a phone
**I want** card entry to be quick and forgiving
**So that** I do not give up because of typos.

**Priority:** Must  |  **Points:** 8  |  **Findings:** F3, F6

**Acceptance criteria**
1. **Given** I tap the card number field on a phone, **when** the keyboard opens, **then** it is the numeric keypad.
2. **Given** I type a card number, **when** the first digits are entered, **then** the card brand icon appears and the number is spaced in groups.
3. **Given** I enter an invalid number or expiry, **when** I leave the field, **then** an inline message says what is wrong (for example "Card has expired").
4. **Given** my browser stores a card, **when** I tap the field, **then** autofill can complete number, expiry and name.
5. **Given** card fields are rendered, **when** the page source is inspected, **then** the fields are hosted by the PSP and no card data is sent to the retailer's servers.
6. **Given** I submit with all fields valid, **when** I tap "Pay", **then** the button shows a loading state and cannot be pressed twice.

### US-08 PayPal without full-page redirect
**As a** PayPal customer
**I want to** pay in a pop-up or overlay
**So that** I do not lose my place in checkout.

**Priority:** Should  |  **Points:** 5  |  **Finding:** F2

**Acceptance criteria**
1. **Given** I select PayPal, **when** I tap the button, **then** the PayPal flow opens in an overlay or pop-up and the checkout page remains in the background.
2. **Given** I approve the payment, **when** the overlay closes, **then** the order is completed and I see the confirmation page.
3. **Given** I close the overlay without paying, **when** I return, **then** I am on the payment page with my data intact and no order is created.
4. **Given** pop-ups are blocked by the browser, **when** I tap PayPal, **then** the system falls back to a redirect and returns me to the same checkout session.

### US-15 Saved payment methods
**As a** logged-in customer
**I want to** reuse a saved card or wallet
**So that** repeat purchases take one tap.

**Priority:** Could  |  **Points:** 8  |  **Finding:** F3

**Acceptance criteria**
1. **Given** I am signed in and tick "Save this card for next time", **when** the payment succeeds, **then** a PSP token and the last four digits are stored and the full number is not.
2. **Given** I have a saved method, **when** I reach payment, **then** it is pre-selected and shows brand, last four digits and expiry.
3. **Given** I pay with a saved card that needs authentication, **when** the bank requests it, **then** the in-page challenge opens (US-09).
4. **Given** I open my account, **when** I choose "Remove", **then** the token is deleted and the card no longer appears.

---

## Epic E4: Authentication & recovery

### US-09 In-page 3-D Secure 2
**As a** card payer whose bank asks for verification
**I want** the check to happen on the same page
**So that** I do not get lost on a redirect or time out.

**Priority:** Must  |  **Points:** 13  |  **Finding:** F2

**Acceptance criteria**
1. **Given** a card payment is submitted, **when** the PSP supports it, **then** the system requests 3-D Secure 2 data (device and order details) so low-risk payments can be approved without a challenge.
2. **Given** the bank requires a challenge, **when** it is triggered, **then** the challenge appears in an overlay inside the checkout page, not on a full-page redirect.
3. **Given** the challenge is open, **when** I look at it, **then** I can see how much time remains and a "Cancel and choose another method" option.
4. **Given** the challenge succeeds, **when** the bank responds, **then** the order completes and I see the confirmation page within 3 seconds.
5. **Given** the challenge fails or times out, **when** the overlay closes, **then** I return to the payment page with a clear message (see US-10) and my data retained.
6. **Given** a payment is sent for authentication, **when** I refresh or go back, **then** the system does not submit a second charge.
7. **Given** a transaction is eligible for an SCA exemption under policy, **when** it is processed, **then** the exemption is requested and the result is logged.

### US-10 Clear decline messages and retry
**As a** shopper whose payment fails
**I want to** know why and what to do next
**So that** I can fix it and still buy.

**Priority:** Must  |  **Points:** 5  |  **Finding:** F2

**Acceptance criteria**
1. **Given** the PSP returns a decline code, **when** the page updates, **then** the message is in plain language mapped from the code (for example "Your bank declined this payment. Try another card or contact your bank").
2. **Given** a decline, **when** the message appears, **then** the entered address and basket remain, and card fields are cleared except for the last four digits.
3. **Given** a decline, **when** I look at the page, **then** I see two actions: "Try again" and "Use a different payment method".
4. **Given** a technical gateway error, **when** it occurs, **then** the message states that no money was taken and invites a retry.
5. **Given** three consecutive failed attempts, **when** the third fails, **then** the page suggests contacting customer service and shows the support link.
6. **Given** any failure, **when** it occurs, **then** the decline code, step and device are logged for analysis (US-13).

### US-11 Session persistence and no duplicate charges
**As a** shopper with a slow connection
**I want** my basket and payment attempt to survive delays and retries
**So that** I am never charged twice or forced to start over.

**Priority:** Must  |  **Points:** 8  |  **Finding:** F2

**Acceptance criteria**
1. **Given** I am inactive in checkout, **when** 55 minutes pass, **then** a warning offers to extend the session.
2. **Given** my session expires, **when** I return within 24 hours on the same device, **then** my basket is restored.
3. **Given** I tap "Pay" twice or my connection drops mid-submit, **when** the retry is sent, **then** the same idempotency key is used and only one charge is created.
4. **Given** a payment is authorised but the confirmation page fails to load, **when** I reload, **then** I see the order confirmation (not the payment form).
5. **Given** a payment result is unknown, **when** the system recovers, **then** it checks the PSP status before allowing a new attempt.

---

## Epic E5: Performance & measurement

### US-12 Payment page performance budget
**As a** shopper on a mobile network
**I want** the payment page to load quickly
**So that** I do not abandon while waiting.

**Priority:** Should  |  **Points:** 8  |  **Finding:** F6

**Acceptance criteria**
1. **Given** a mid-range Android phone on a throttled 4G connection, **when** the payment page loads, **then** Largest Contentful Paint is 2.5 seconds or less at the 75th percentile.
2. **Given** a third-party script is added to the page, **when** it is reviewed, **then** it must be loaded after the payment form or be approved against the performance budget.
3. **Given** a release is prepared, **when** the automated performance test runs, **then** the build fails if the budget is exceeded.
4. **Given** the page is live, **when** real-user monitoring runs, **then** the load-time distribution by device is visible on the dashboard.

### US-13 Step-level tracking and dashboard
**As a** product owner
**I want** reliable data on every checkout step
**So that** I can see where shoppers drop and whether changes work.

**Priority:** Must  |  **Points:** 5  |  **Finding:** All

**Acceptance criteria**
1. **Given** a shopper reaches any checkout step, **when** it loads, **then** a view event is recorded with session id, device type, traffic source, customer type and timestamp.
2. **Given** a shopper completes or leaves a step, **when** that happens, **then** a completion or exit event is recorded, with an exit tag where one can be determined (for example error code).
3. **Given** the dashboard is opened, **when** it loads, **then** it shows the funnel by step, conversion by device, payment-stage abandonment and top gateway exit reasons for any chosen date range.
4. **Given** the old and new tracking run in parallel for two weeks, **when** the numbers are compared, **then** session counts agree within 2%.
5. **Given** personal data is involved, **when** events are stored, **then** no card data or full email address appears in the analytics payload.

### US-14 Feature flags and fraud guardrails
**As an** engineering and risk owner
**I want** each change behind a switch with fraud monitoring
**So that** we can test safely and reverse quickly.

**Priority:** Must  |  **Points:** 5  |  **Findings:** Risk

**Acceptance criteria**
1. **Given** each initiative (guest, wallets, in-page 3DS2, single page) has a flag, **when** an administrator changes it, **then** the change applies within 5 minutes without a deployment.
2. **Given** the experiment runs, **when** sessions are allocated, **then** the split can be set from 0% to 100% per flag.
3. **Given** guest or wallet orders are placed, **when** they are processed, **then** existing fraud rules run on them and orders above the configured value trigger extra verification.
4. **Given** the chargeback rate on the new flow exceeds the agreed limit for a week, **when** the weekly report is produced, **then** an alert is sent to the product owner and risk analyst.

---

## Definition of Ready
- Story has a clear user, goal and benefit, and links to a BRD requirement
- Acceptance criteria are testable and agreed with QA
- Designs available for any UI change; PSP dependencies identified
- Estimated by the team; no unanswered blocking questions

## Definition of Done
- All acceptance criteria pass in QA on iOS Safari, Android Chrome and desktop Chrome
- Accessibility check (WCAG 2.2 AA) and performance budget pass
- Tracking events verified in the analytics tool
- Behind a feature flag; rollout plan and rollback step documented
- Product owner has accepted the story in the demo
