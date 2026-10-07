#!/usr/bin/env python3
"""Regenerate the options reference and lightweight SVG charts from one input file.

No market-data fetching. Decimal arithmetic; all monetary model inputs are IRR.
"""
from pathlib import Path
from decimal import Decimal as D
from html import escape
import json, math, re
ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'assets/data/iranian-options-example.json').read_text(), parse_float=D)
N=data['contracts']; M=data['multiplier']; Q=N*M; P=D(data['entry_premium_irr']); K=D(data['scenario_strike_irr']); F=D(data['irr_per_toman'])
C=P*Q; E=K*Q; B=K+P
SLUG='stock-options-in-the-iranian-market'
TITLE='Stock Options in the Iranian Market: A Practical Knowledge Base'
DESC='An options reference with verified arithmetic, rial/toman checks, conditional payoff scenarios, and exercise-funding calculations.'
def fmt(v):
 s=f'{D(v):,.4f}'.rstrip('0').rstrip('.')
 return s

def scenario(st):
 s=D(str(st))*F; intrinsic=max(D(0),s-K);gross=intrinsic*Q;net=gross-C
 return dict(spot=D(str(st)), intrinsic=intrinsic, gross=gross, net=net, roi=net/C*100)
rows=[scenario(x) for x in data['scenario_spots_toman']]
r650=scenario(650)
# Independent exact expected values guard against unit or multiplier regressions.
assert Q==1560078 and C==99844992 and E==9204460200 and B==5964
assert r650['net']==836201808 and r650['roi']==D('837.5')
assert all(x['net']==-C for x in rows if x['spot']<=K/F)
assert scenario('596.4')['net']==0

def svg_start(w,h,title,desc):
 return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>', '<style>text{font-family:system-ui,sans-serif;fill:#344355;font-size:15px}.small{font-size:13px}.heading{font-size:20px;font-weight:700;fill:#102c3a}.grid{stroke:#d5ddd9;stroke-width:1}.curve{fill:none;stroke:#146b68;stroke-width:3}</style>',f'<rect width="{w}" height="{h}" rx="10" fill="#f5f4ee"/>']
def txt(a,x,y,s,cls='',anchor='start'):
 a.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(str(s))}</text>')
# Exact piecewise linear payoff in million toman, not a fitted prediction.
w,h=820,500;a=svg_start(w,h,'Long-call expiry profit and loss, conditional strike','354 contracts of 4,407 shares; premium 64 IRR; assumed strike 590 toman. Break-even 596.4 toman; at 650 toman profit is 83,620,180.8 toman before fees.')
x=lambda s:80+(float(s)-500)/200*680
y=lambda profit:390-(float(profit)+20)/190*290
xk=x(K/F); xb=x(B/F); y0=y(0); yl=y(-C/F/1000000)
a.append(f'<rect x="80" y="100" width="{xk-80}" height="290" fill="#f4e3df"/><rect x="{xb}" y="100" width="{760-xb}" height="290" fill="#e0eeea"/>')
txt(a,30,33,'Expiration P/L · 354 contracts','heading');txt(a,30,61,'Conditional: strike 590 toman · premium 6.4 toman/share','small')
for value in [0,40,80,120,160]:
 yy=y(value);a.append(f'<line x1="80" y1="{yy}" x2="760" y2="{yy}" class="grid"/>');txt(a,68,yy+5,value,'small','end')
for value in [500,550,600,650,700]:txt(a,x(value),420,value,'','middle')
a.append(f'<line x1="80" y1="{y0}" x2="760" y2="{y0}" stroke="#82908d"/>')
pts=[(500,-C/F/1000000),(K/F,-C/F/1000000),(700,scenario(700)['net']/F/1000000)]
a.append('<polyline points="'+' '.join(f'{x(s)},{y(v)}' for s,v in pts)+'" class="curve"/>')
for xx in [xk,xb]:a.append(f'<line x1="{xx}" y1="100" x2="{xx}" y2="390" stroke="#9b713d" stroke-dasharray="5 5"/>')
txt(a,100,123,'OTM · S < 590','small');txt(a,580,123,'Profit · S > 596.4','small');txt(a,xk-8,85,'Strike 590','small','end');txt(a,xb+8,85,'Break-even 596.4','small')
txt(a,100,yl+27,'Maximum loss: 9.9844992 million toman','small')
xx=x(650);yy=y(r650['net']/F/1000000);a.append(f'<circle cx="{xx}" cy="{yy}" r="6" fill="#9b713d"/>');txt(a,xx-10,yy-22,'650 → +83.6201808m toman','small','end')
txt(a,80,465,'X: underlying at expiration (toman/share) · Y: total P/L (million toman)','small');txt(a,80,487,'ITM starts above 590; ITM does not necessarily mean a net profit. Fees excluded.','small');a.append('</svg>')
(ROOT/'assets/charts/iranian-options-payoff.svg').write_text('\n'.join(a)+'\n')
# Supplied close/volume only. Invalid OHLC inputs are deliberately not repaired.
a=svg_start(820,480,'Supplied option closes and volume','Unverified source rows: closing prices 16, 64, 70 IRR and volume 10,353, 44,828, 41,077 contracts on April 12–14, 2025. Two opening prices are below their reported lows; no candles or open-interest data are plotted.')
txt(a,30,32,'Supplied history · not a verified market feed','heading');txt(a,30,58,'Closing premium (IRR/share); volume (contracts). No open-interest data.','small')
xs=[150,410,670]
for value in [0,20,40,60,80]:
 yy=220-value*1.65;a.append(f'<line x1="80" y1="{yy}" x2="755" y2="{yy}" class="grid"/>');txt(a,68,yy+5,value,'small','end')
a.append('<polyline points="'+' '.join(f'{xx},{220-row["close"]*1.65}' for xx,row in zip(xs,data['history']))+'" class="curve"/>')
for xx,row in zip(xs,data['history']):
 yy=220-row['close']*1.65;a.append(f'<circle cx="{xx}" cy="{yy}" r="5" fill="#146b68"/>');txt(a,xx,yy-12,row['close'],'','middle')
 bh=row['volume']/45000*110;a.append(f'<rect x="{xx-32}" y="{405-bh}" width="64" height="{bh}" rx="3" fill="#9b713d"/>');txt(a,xx,395-bh,f'{row["volume"]:,}','small','middle');txt(a,xx,435,row['date'],'small','middle')
txt(a,80,262,'Volume · contracts','small');txt(a,30,469,'Source: supplied rows; inconsistent open/high/low fields are excluded from the plot.','small');a.append('</svg>')
(ROOT/'assets/charts/iranian-options-history.svg').write_text('\n'.join(a)+'\n')
parts=[]
def p(s):parts.append('<p>'+s+'</p>')
def h(id,s):parts.append(f'<h2 id="{id}">{s}</h2>')
def code(label,s):parts.append(f'<pre tabindex="0" aria-label="{escape(label)}"><code>{escape(s,quote=False)}</code></pre>')
def ul(items):parts.append('<ul>'+''.join('<li>'+v+'</li>' for v in items)+'</ul>')
def table(label,heads,rs):parts.append(f'<div class="reference-table" role="region" aria-label="{label}" tabindex="0"><table><thead><tr>'+''.join('<th scope="col">'+v+'</th>' for v in heads)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in row)+'</tr>' for row in rs)+'</tbody></table></div>')
def fig(path,alt,caption):parts.append(f'<figure class="options-figure"><a href="../../assets/charts/{path}" aria-label="Open full-size chart: {alt}"><img src="../../assets/charts/{path}" alt="{alt}" loading="lazy"></a><figcaption>{caption}</figcaption></figure>')
p('<strong>Unit convention throughout this historical example: 1 toman = 10 IRR.</strong> Entry premium is 64 IRR per underlying share, or 6.4 toman. Never add a rial premium to a toman strike without converting first.')
parts.append('<blockquote><p><strong>Unresolved contract input:</strong> the supplied strike is “590” with conflicting unit labels. The premium reconciles to approximately 10 million toman, but that does not establish the strike unit. Calculations below show both interpretations; the main scenario chart conditionally assumes <strong>590 toman = 5,900 IRR</strong>. The contract specification has not been independently verified.</p></blockquote>')
p('This reference reconstructs a supplied historical trade example; it does not authenticate an execution record. Options are leveraged derivatives: buyers can lose the entire premium, while writers can face materially different and potentially much larger losses. This is educational material, not personalized financial advice.')
p('Jump to: <a href="#units">Unit reconciliation</a> · <a href="#break-even">Break-even</a> · <a href="#funding">Exercise cash</a> · <a href="#scenarios">Scenarios</a> · <a href="#exit">Sell or exercise</a> · <a href="#history">Historical data issues</a> · <a href="#cheat-sheet">Cheat sheet</a>.')
h('contract','1. What an Option Contract Is')
table('Option terminology',['Term','Meaning'],[('Call / put','A call gives the holder a right to buy; a put gives a right to sell the specified underlying quantity at the strike, subject to the contract’s exercise terms.'),('Buyer / writer','The buyer pays for a right. A writer opens a short position and accepts the corresponding obligation if assigned. Selling an existing long position to close it is different from writing a new option.'),('Premium / strike','Premium is the option price paid up front; strike is the per-share transaction price on exercise. Both require an explicit currency unit.'),('Expiration / multiplier','Expiration limits the contract’s life. The multiplier specifies shares per contract and can be adjusted; it is not universally 1,000.'),('Exercise / physical settlement','Exercise invokes the contract. Physical settlement transfers shares and cash; a cash-settled contract instead settles the prescribed difference under its rules.'),('Intrinsic / time value','Call intrinsic value is max(0, spot − strike); put intrinsic value is max(0, strike − spot). The excess of an option quote over intrinsic value is commonly called time or extrinsic value.')])
code('Anatomy of the supplied contract','''Bank Tejarat shares (وتجارت)
  -> Call contract (ضجار2054)
     -> Multiplier: 4,407 shares per contract (supplied)
     -> Strike: 590 [unit unresolved]
     -> Entry premium: 64 IRR per share
     -> Expiration: 17 Ordibehesht [verify year and cutoff]
     -> Close in market OR exercise/settle under contract rules''')
table('Moneyness of calls and puts',['State','Call','Put'],[('OTM — no intrinsic value','Spot < strike','Spot > strike'),('ATM — at the strike','Spot = strike','Spot = strike'),('ITM — positive intrinsic value','Spot > strike','Spot < strike')])
p('Moneyness ignores the premium paid: an ITM call can still be a losing trade. For general payoff definitions, see the Options Industry Council’s <a href="https://www.optionseducation.org/strategies/all-strategies/long-call">long-call guide</a>. Its educational concepts apply here; US contract sizes and exercise procedures must not be imported into Iranian contracts.')
h('comparison','2. Spot vs Futures vs Options')
table('Cash shares, futures, and options',['Feature','Cash stock purchase','Futures','Long option / option writer'],[('Ownership','Own shares after settlement.','Contract exposure, not immediate share ownership.','Long option owns a right; writer owes performance if assigned.'),('Obligation','Pay for the shares purchased.','Both sides have contractual obligations unless closed.','Buyer may exercise under terms; writer must meet assignment obligations.'),('Capital / margin','Full purchase cost when unleveraged.','Initial and variation margin; additional cash may be needed.','Buyer funds premium; physical exercise needs further cash. Writer collateral/margin depends on rules.'),('Leverage','None for an unleveraged cash purchase.','Notional can exceed margin deposited.','Exposure can be large relative to premium or collateral.'),('Maximum loss','Purchase cost for unleveraged long shares, if value reaches zero.','Can exceed initial margin; depends on position and underlying.','Buyer: premium plus costs before exercise. Uncovered call writer: theoretically unlimited loss.'),('Expiration','No derivative expiry.','Contract expires.','Option expires.'),('Risk','Share-price and issuer risk.','Price moves, leverage, margin calls, settlement.','Time decay, volatility, liquidity; writers add assignment and funding risks.')])
p('The option buyer’s premium-loss limit describes the option position. After a call is physically exercised, the holder owns shares and faces their subsequent price risk. A short put also carries substantial downside; collateral does not eliminate economic loss.')
h('iran','3. How Iranian Stock Options Work')
p('For a Tehran Stock Exchange or Iran Fara Bourse series, use the exchange contract specification, corporate-action notices, and the broker’s current exercise instructions as the operational source of truth. This article does not claim a verified current commission, settlement window, margin formula, or exercise deadline.')
ul(['Confirm multiplier, strike, quote currency, underlying, expiration year, last trading day, and exercise style.', 'Confirm physical versus cash settlement, eligibility, submission procedure, cash/share delivery deadlines, fees, taxes, and consequences of failing to act.', 'Check corporate-action adjustments to strike and multiplier. Use prices and specifications effective on the same date; do not mix pre-adjustment prices with a post-adjustment multiplier.', 'Confirm the trading calendar and broker cutoff separately from the printed expiration date. Do not assume an ITM holding will settle automatically.'])
p('The supplied multiplier of 4,407 is used exactly as given. Its unusual size is a reason to inspect adjustment history, not proof of any particular corporate action. No authoritative contract notice was located to resolve the disputed strike unit.')
h('symbol','4. Reading an Option Symbol in EasyTrader')
p('The supplied identifiers are <bdi lang="fa">ضجار2054</bdi> and <code>BTEJ-O-14040217</code>, with underlying Bank Tejarat (<bdi lang="fa">وتجارت</bdi>). Treat them as lookup keys, not a substitute for the terms. The date-like suffix suggests 1404/02/17, consistent with the supplied “17 Ordibehesht”; the year, exchange date, and broker deadline still need confirmation. This is a historical 2025 example, not a live quote.')
table('Fields to inspect in the trading platform',['Field','What to check'],[('Underlying, strike, expiration, multiplier','Exact series, explicit rial/toman units, effective adjustment date, and settlement terms.'),('Best bid / best ask','Prices and quantities currently available. An immediate sale is evaluated against executable bids, not the last trade.'),('Last / closing price','Last is a recent transaction; closing is the venue’s published session value and can differ. Neither guarantees execution.'),('Volume / open interest','Session trading activity versus outstanding contracts at a point in time; verify timestamp and definition.'),('Spread / depth / liquidity','Price concession and available contracts across multiple order-book levels, especially for a 354-contract exit.')])
h('opening','5. Opening a Long Call Position')
code('Conceptual order workflow','''Search contract -> Inspect specifications and units
  -> Choose number of contracts -> Enter premium per share
  -> Review premium x multiplier x quantity + costs
  -> Submit buy order -> Confirm actual fills
  -> Monitor position, liquidity, and expiration obligations''')
p('This is a platform-independent workflow, not a claim about current EasyTrader button names. An accepted order is not a fill. Record executed quantity and weighted-average entry premium if fills occur at multiple prices; recompute exposure and cost from executed values.')
h('formulas','6. Core Calculations')
code('Long-call formulas with every price in IRR per share','''N = number of contracts        M = shares per contract
Q = N x M                      P = entry premium (IRR/share)
K = strike (IRR/share)          S_T = spot at expiration (IRR/share)

Premium cost                 C = P x Q
Intrinsic value/share        I = max(0, S_T - K)
Gross intrinsic value        G = I x Q
Expiry net P/L before costs     = G - C
Break-even before costs         = K + P
Additional exercise cash        = K x Q
Maximum option loss             = C + applicable transaction costs
Return on premium (%)           = (G - C) / C x 100
IRR -> toman                    = IRR / 10''')
p('Q is the contractual share quantity, not current share ownership or delta-adjusted exposure. These are expiration formulas, not a pricing model for an option with time remaining. “Gross exercise value” below means the intrinsic spread, not the total market value of delivered shares. Physical settlement does not necessarily pay that spread as cash.')
h('units','7. Worked Example: 354 Contracts and the Unit Check')
code('Reconcile the premium payment',f'''{N:,} contracts x {M:,} shares/contract = {Q:,} underlying shares
{fmt(P)} IRR/share x {Q:,} shares = {fmt(C)} IRR
{fmt(C)} IRR / 10 = {fmt(C/F)} toman

Premium per contract = {fmt(P*M)} IRR = {fmt(P*M/F)} toman
Reported approximate payment = 10,000,000 toman
Difference = {fmt(D(data['reported_paid_toman'])-C/F)} toman''')
p('The calculated premium is approximately 10 million toman. The small difference can reflect rounding or costs, but no fee amount can be inferred without the execution statement. If the quoted premium were 64 <em>toman</em>, the cost would instead be <strong>'+fmt(C)+' toman</strong>—ten times the result and inconsistent with the stated approximate payment.')
p('<strong>This reconciles the premium unit only.</strong> The strike is not part of the premium-cost formula. The payment cannot independently verify the strike unit, underlying-price unit, or multiplier adjustment history.')
h('break-even','8. Break-Even: Two Different Strike Interpretations')
table('Strike-unit ambiguity',['Interpretation','Normalized strike','Break-even before costs'],[('590 means IRR','590 IRR = 59 toman','654 IRR = 65.4 toman'),('590 means toman — conditional model','5,900 IRR = 590 toman','5,964 IRR = 596.4 toman')])
p('The supplied spot discussion explicitly labels 546–562 as toman. If those labels are correct, a 590-toman strike describes an OTM call and is internally coherent with the discussion. A 590-IRR strike alongside a 546-toman spot would imply 487 toman of intrinsic value per share against a 6.4-toman entry premium—a major inconsistency requiring investigation. This is evidence of mismatched inputs, not a verified arbitrage or proof of the true strike.')
p('If the spot figures were themselves actually IRR, then a 590-IRR strike could also be coherent. Therefore the rest of the article uses <strong>the explicit conditional assumption K = 590 toman</strong>, not a verified contract fact. Do not use its funding amounts or scenario returns for an order until the official terms and units agree.')
fig('iranian-options-payoff.svg','Conditional long-call expiration payoff in million toman','Calculated from 354 × 4,407 shares and a 64-IRR premium. Strike 590 toman is assumed, not verified. Full-size view opens on selection; exact values follow in the scenario table.')
p('Below or at 590 toman the full premium is lost at expiration. Between 590 and 596.4 toman the call is ITM but still loses money after premium. Above 596.4 toman it makes a before-fee profit, assuming its intrinsic value is successfully realized. Costs raise the effective break-even.')
h('funding','9. Exercise and Physical Settlement Funding')
table('Funding under the conditional 590-toman strike',['Amount','IRR','Toman'],[('New exercise cash per contract',fmt(K*M),fmt(K*M/F)),('New exercise cash for all 354',fmt(E),fmt(E/F)),('Original premium already paid',fmt(C),fmt(C/F)),('Total acquisition cost including premium, before fees',fmt(E+C),fmt((E+C)/F))])
p('The buyer needs <strong>'+fmt(E/F)+' toman of additional exercise cash</strong>; the '+fmt(C/F)+'-toman premium is already spent and does not fund that payment. Total effective acquisition cost is 596.4 toman per share before fees. If the strike were instead 590 IRR, additional exercise cash would be '+fmt(D(590)*Q/F)+' toman. That is another tenfold difference in the funding requirement.')
h('scenarios','10. Scenario Analysis at Expiration')
p('<strong>Conditional strike: 590 toman. All monetary columns below are in toman</strong>; intrinsic is per share and the other monetary columns cover all 354 contracts. Original premium is fixed at '+fmt(C/F)+' toman. Returns use this exact premium, not the rounded 10-million figure. Fees, taxes, financing, slippage, and settlement failure are excluded.')
table('Conditional expiration scenarios in toman',['Spot at expiration','Intrinsic / share','Gross exercise value','Original premium','Net P/L','Return on premium','Exercise economic?'],[[fmt(row['spot']),fmt(row['intrinsic']/F),fmt(row['gross']/F),fmt(C/F),fmt(row['net']/F),fmt(row['roi'])+'%', 'Yes: positive intrinsic' if row['intrinsic']>0 else ('No intrinsic benefit (ATM)' if row['spot']==K/F else 'No (OTM)')] for row in rows])
p('“Yes” asks whether exercise captures positive intrinsic value if available under the contract, ignoring costs and constraints. It is not an instruction to exercise rather than close. Premium is a sunk cost for that decision: exercise can preserve some value even when the overall trade is below break-even.')
h('650','11. The 650-Toman Scenario, Recalculated')
code('Exact 650-toman scenario, conditional on a 590-toman strike',f'''Spot at expiry           = 650 toman = 6,500 IRR/share
Strike                   = 590 toman = 5,900 IRR/share
Intrinsic                = 60 toman = 600 IRR/share
Entry premium            = 6.4 toman = 64 IRR/share
Profit after premium     = 53.6 toman = 536 IRR/share
Profit per contract      = {fmt(D(536)*M/F)} toman = {fmt(D(536)*M)} IRR
Gross intrinsic, all     = {fmt(r650['gross']/F)} toman = {fmt(r650['gross'])} IRR
Original premium, all    = {fmt(C/F)} toman = {fmt(C)} IRR
Net profit, all          = {fmt(r650['net']/F)} toman = {fmt(r650['net'])} IRR
Return on exact premium  = {fmt(r650['roi'])}% before fees''')
p('At 650 toman, the delivered shares have a market value of '+fmt(D(650)*Q)+' toman. Subtract '+fmt(E/F)+' toman of exercise cash and '+fmt(C/F)+' toman of premium to obtain '+fmt(r650['net']/F)+' toman. If the shares are retained, that figure is a mark-to-market economic gain at the assumed spot, not a realized cash profit. Selling all shares at that price is not guaranteed.')
ul(['<strong>Exercise and acquire shares:</strong> fund the strike payment, follow the valid exercise process, and take on stock ownership risk after delivery.', '<strong>Sell to close before expiration:</strong> realized P/L is (actual sale premium − 64 IRR) × shares represented by the contracts closed, less costs. Market price may include time value and execution may occur across multiple bids.', '<strong>Hold ITM through expiration:</strong> value depends on correctly meeting the exercise/settlement rules. ITM status is not a guarantee of automatic payment or successful settlement.'])
p('The 837.5% figure is return on premium for the conditional expiration model, not an annualized return, probability estimate, or return on all capital needed to acquire the shares.')
h('exit','12. Sell the Option or Exercise It?')
p('Compare the executable option bid with intrinsic value, remaining time value, fees, share-market liquidity, and the funding requirement. Use the bid available for the intended quantity, not a stale last price. Exercise is only available when the contract permits it; European-style exercise terms, where applicable, do not allow an early exercise simply because it looks attractive.')
code('Decision framework, subject to the contract’s exercise window','''Before the trading/exercise cutoff
  |
  +-- Verify specifications, units, deadline, and executable bids
  |
  +-- OTM or ATM?
  |     -> Before expiry: option may still have saleable time value
  |     -> At expiry: no intrinsic exercise benefit; check instructions
  |
  +-- ITM?
        -> Net sale proceeds vs net exercise-and-share-sale proceeds
        -> Bid above intrinsic? Closing may preserve time value
        -> Weak bids? Check depth, costs, and actual exercise eligibility
        -> Want shares AND can fund settlement? Evaluate exercise
        -> Cannot fund or meet cutoff? Plan a feasible exit in time

Do not let an ITM position lapse merely because action was missed.''')
p('Closing may suit a holder who can capture meaningful time value, has sufficient bids and a reasonable spread, and does not want to fund physical delivery. Exercise may be relevant near expiration when permitted, little time value remains, the holder wants shares, funds are available, and settlement costs have been checked. Neither is universally preferable.')
p('Time value is often estimated as option market price minus current intrinsic value. Positive remaining time value can be sacrificed by exercise instead of sale. A negative residual from an illiquid quote or a contract that cannot currently be exercised requires analysis; do not silently clamp it to zero and call it a reliable valuation. Discounting, dividends, and exercise restrictions can also matter.')
h('history','13. Time Decay and the Supplied Price History')
p('Theta describes sensitivity to the passage of time, holding other pricing inputs constant. Long options generally lose time value as expiry approaches; that decay can be pronounced around the strike near expiry, but it is neither a fixed daily deduction nor a prediction that every observed premium must fall.')
table('Unverified historical option rows; all prices IRR per share',['Date','Open','High','Low','Close','Last','Volume (contracts)','Data check'],[[row['date'],str(row['open']),str(row['high']),str(row['low']),str(row['close']),str(row['last']),fmt(row['volume']), 'Invalid OHLC: open below low' if row['open']<row['low'] else 'Range consistent; unverified'] for row in data['history']])
p('<strong>Do not draw candles from these inputs.</strong> The April 12 open of 8 is below the stated low of 11; the April 13 open of 16 is below the stated low of 45. Those are inconsistent if they describe the same session and price basis. The fields may be mislabelled or differently adjusted, but the source does not establish a correction. They remain flagged, not repaired.')
fig('iranian-options-history.svg','Supplied closing prices and trading volumes for April 12 to 14, 2025','Only supplied closes (IRR per underlying share) and volume (contracts) are plotted. These fields are not independently verified; open/high/low inconsistencies prevent a reliable candlestick chart.')
p('The supplied closes rise 16 → 64 → 70 IRR across three sessions. This does not identify a cause: underlying moves, implied volatility, remaining time, order-book effects, and data adjustments may all contribute. No matching spot series or implied-volatility observations were supplied, so attributing the rise solely to bullish expectations or isolating theta would be unsupported.')
h('liquidity','14. Liquidity and Open Interest')
ul(['<strong>Volume:</strong> contracts traded during the session; repeated turnover can involve the same outstanding exposure.', '<strong>Open interest:</strong> outstanding contracts at a measurement time, counted once per matched long/short contract. It is not the sum of both sides and cannot be inferred from volume.', '<strong>Bid/ask spread:</strong> an immediate execution cost indicator; narrow spread alone does not establish depth.', '<strong>Order-book depth:</strong> quantities available at each price. A 354-contract sale may sweep multiple levels or fill only partially.'])
p('The latest supplied volume is 41,077 contracts; that says nothing conclusive about whether 354 can be sold near the displayed last price now. Check current bids, quantities, timestamps, and partial-fill risk. No numerical open-interest or turnover-value series was included in the supplied extract, so neither is fabricated or charted. Last × volume × multiplier is not a substitute for actual session turnover across different execution prices.')
h('mistakes','15. Common Mistakes')
ul(['<strong>Mixing rial and toman:</strong> a tenfold error can invalidate cost, moneyness, exercise funding, and payoff. Label every input before multiplying.', 'Assuming 1,000 shares per contract instead of the supplied 4,407, or mixing adjustment dates.', 'Treating 64 IRR per underlying share as the cost of one whole contract.', 'Adding a 64-IRR premium directly to a 590-toman strike; the correct conditional addition is 590 + 6.4 toman.', 'Equating ITM with net profit, or treating break-even as a pre-expiration sale-price forecast.', 'Assuming every ITM option must be exercised or will settle automatically; ignoring valid exercise windows and instructions.', 'Ignoring time value, executable bids, depth, and the funding required for physical settlement.', 'Using last price for an entire 354-contract exit, or treating model intrinsic value as guaranteed cash proceeds.', 'Ignoring fees, taxes, financing, corporate-action adjustments, data inconsistencies, and settlement rules.'])
h('cheat-sheet','16. Quick Reference / Cheat Sheet')
code('Reusable formulas: normalize prices to one unit first','''Q = contracts x shares per contract
Premium cost = entry premium x Q
Call intrinsic/share = max(0, spot - strike)
Put intrinsic/share = max(0, strike - spot)
Long call expiry P/L = [max(0, spot - strike) - entry premium] x Q
Long call break-even = strike + entry premium       (before costs)
Physical call exercise funding = strike x Q        (additional cash)
Closing P/L = (sale premium - entry premium) x shares closed - costs
IRR to toman = divide by 10; toman to IRR = multiply by 10''')
code('Before buying','''[ ] Verify underlying and exact contract
[ ] Verify strike and rial/toman units
[ ] Verify multiplier and corporate-action effective date
[ ] Verify expiration year, exercise style, and cutoffs
[ ] Check executable bid/ask, spread, and depth
[ ] Check volume and open interest with timestamps
[ ] Calculate maximum premium loss and before-cost break-even
[ ] Understand fees, settlement requirements, and exercise funding''')
code('Before expiration','''[ ] Check spot vs strike in the same unit
[ ] Calculate intrinsic value
[ ] Compare executable option bid with intrinsic value
[ ] Estimate time value, fees, and realistic exit proceeds
[ ] Check liquidity for the full intended quantity
[ ] Calculate additional exercise cash
[ ] Choose a feasible close, exercise, or expiry plan
[ ] Submit required instructions on time and confirm the outcome''')
p('Calculation inputs are available as <a href="../../assets/data/iranian-options-example.json">a small JSON dataset</a>. Figures and scenario tables are generated from the same IRR-based model. Historical inputs remain explicitly unverified; current exchange and broker notices must resolve the contract terms before operational use.')
body='\n\n        '.join(parts);reading=f'{math.ceil(len(re.sub("<[^>]+>"," ",body).split())/220)} min read'
s=(ROOT/'templates/post.html').read_text()
for k,v in {'TITLE':TITLE,'DESCRIPTION':DESC,'CANONICAL_URL':f'https://hossein.cloud/blog/posts/{SLUG}.html','DATE_ISO':'2026-10-06','DATE_DISPLAY':'October 6, 2026','TOPIC':'Markets','READING_TIME':reading,'INTRODUCTION':DESC,'BODY':body}.items():s=s.replace('{{'+k+'}}',v)
s=re.sub(r'<a href="https://github.com/hosseinmoazami".*?</a><a href="mailto:.*?</a>','<a href="/blog/">Writing</a><a href="/#contact">Contact</a>',s)
s=s.replace('    </article>','      <a class="article-next" href="restoring-a-gzip-mongodb-backup-in-docker.html"><span><small>Next field note</small><strong>Restoring a Gzip-Compressed MongoDB Backup in Docker</strong></span><span aria-hidden="true">→</span></a>\n    </article>')
(ROOT/'blog/posts'/f'{SLUG}.html').write_text(s)
print(f'Generated article ({reading}), two SVG charts, and consistent scenario calculations.')
