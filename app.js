const topFunds = [
  { symbol: "GPFG", aum: "$1,792.0B", ytd: "+8.2%" },
  { symbol: "CIC", aum: "$1,350.0B", ytd: "+5.1%" },
  { symbol: "ADIA", aum: "$1,057.0B", ytd: "+6.8%" },
  { symbol: "KIA", aum: "$969.0B", ytd: "+4.3%" },
  { symbol: "PIF", aum: "$930.0B", ytd: "+12.1%" },
  { symbol: "GIC", aum: "$890.0B", ytd: "+7.4%" },
  { symbol: "HKMA", aum: "$587.0B", ytd: "+3.9%" },
  { symbol: "TEMASEK", aum: "$484.0B", ytd: "+9.2%" },
  { symbol: "QIA", aum: "$526.0B", ytd: "+5.7%" },
  { symbol: "CPPIB", aum: "$570.0B", ytd: "+6.1%" },
  { symbol: "NBIM-ETH", aum: "$424.0B", ytd: "+4.8%" },
  { symbol: "CALPERS", aum: "$540.0B", ytd: "+3.2%" },
  { symbol: "NZSF", aum: "$49.8B", ytd: "+11.3%" },
  { symbol: "MUBADALA", aum: "$330.0B", ytd: "+8.5%" },
  { symbol: "SAFE", aum: "$1,090.0B", ytd: "+2.4%" },
];

const rankings = [
  {
    rank: 1,
    fund: "Norway Government Pension Fund Global",
    country: "Norway",
    aum: "$1,792.0",
    ytd: "+8.2%",
    trend: 82,
  },
  {
    rank: 2,
    fund: "China Investment Corporation",
    country: "China",
    aum: "$1,350.0",
    ytd: "+5.1%",
    trend: 61,
  },
  {
    rank: 3,
    fund: "Abu Dhabi Investment Authority",
    country: "UAE",
    aum: "$1,057.0",
    ytd: "+6.8%",
    trend: 72,
  },
  {
    rank: 4,
    fund: "Kuwait Investment Authority",
    country: "Kuwait",
    aum: "$969.0",
    ytd: "+4.3%",
    trend: 53,
  },
  {
    rank: 5,
    fund: "GIC Private Limited",
    country: "Singapore",
    aum: "$890.0",
    ytd: "+7.4%",
    trend: 74,
  },
  {
    rank: 6,
    fund: "Public Investment Fund",
    country: "Saudi Arabia",
    aum: "$930.0",
    ytd: "+12.1%",
    trend: 95,
  },
  {
    rank: 7,
    fund: "Hong Kong Monetary Authority",
    country: "Hong Kong",
    aum: "$587.0",
    ytd: "+3.9%",
    trend: 49,
  },
];

const feedItems = [
  {
    time: "10 Apr 2026 · 14:32 UTC",
    tag: "Deals",
    title: "ADIA closes $2.4B infrastructure deal in Southeast Asian logistics network",
  },
  {
    time: "10 Apr 2026 · 12:15 UTC",
    tag: "Policy",
    title: "Norway GPFG divests $890M in fossil fuel holdings following ethical review",
  },
  {
    time: "10 Apr 2026 · 09:44 UTC",
    tag: "Deals",
    title: "PIF announces $5B allocation to AI infrastructure across NEOM",
  },
  {
    time: "09 Apr 2026 · 22:10 UTC",
    tag: "Real Estate",
    title: "GIC acquires majority stake in European data center platform for $1.8B",
  },
  {
    time: "09 Apr 2026 · 18:33 UTC",
    tag: "Policy",
    title: "QIA increases emerging market allocation to 18% after portfolio review",
  },
  {
    time: "09 Apr 2026 · 15:01 UTC",
    tag: "Deals",
    title: "Mubadala partners with Brookfield on $3.2B renewable energy fund",
  },
];

const regions = [
  { name: "MENA", value: "$187B", size: 100 },
  { name: "APAC", value: "$142B", size: 76 },
  { name: "Europe", value: "$98B", size: 52 },
  { name: "N.Amer", value: "$121B", size: 65 },
  { name: "LatAm", value: "$34B", size: 18 },
  { name: "Africa", value: "$18B", size: 10 },
];

const allocations = [
  { name: "Public Equities", value: "32%", size: 32 },
  { name: "Fixed Income", value: "22%", size: 22 },
  { name: "Real Estate", value: "18%", size: 18 },
  { name: "Private Equity", value: "14%", size: 14 },
  { name: "Infrastructure", value: "8%", size: 8 },
  { name: "Other", value: "6%", size: 6 },
];

const transactions = [
  {
    title: "ADIA acquired 12% stake in Vantage Data Centers — $2.4B",
    time: "2 hours ago",
    tag: "Infrastructure",
  },
  {
    title: "GIC co-led Series E in Stripe — $800M at $95B valuation",
    time: "5 hours ago",
    tag: "Unlisted Equity",
  },
  {
    title: "PIF committed $1.2B to Blackstone Real Estate Partners X",
    time: "8 hours ago",
    tag: "Real Estate Fund",
  },
  {
    title: "CPP Investments sold $430M position in Thames Water",
    time: "12 hours ago",
    tag: "Infrastructure",
  },
  {
    title: "Temasek increased allocation to AI and semiconductor sector by $3.1B",
    time: "14 hours ago",
    tag: "Listed Equity",
  },
  {
    title: "Mubadala and Brookfield announce $3.2B renewable energy joint venture",
    time: "18 hours ago",
    tag: "Energy",
  },
  {
    title: "NZ Super Fund issues RFP for global multi-asset credit manager",
    time: "1 day ago",
    tag: "RFP",
  },
  {
    title: "NBIM exits four mining companies on ESG grounds — $890M",
    time: "1 day ago",
    tag: "Divestment",
  },
];

function updateClock() {
  const clock = document.getElementById("utc-clock");
  if (!clock) return;
  clock.textContent = new Date().toISOString().slice(11, 19);
}

function mountTicker() {
  const ticker = document.getElementById("ticker-track");
  if (!ticker) return;

  const repeated = [...topFunds, ...topFunds, ...topFunds];
  ticker.innerHTML = repeated
    .map(
      (fund) => `
        <div class="ticker-item">
          <span class="ticker-symbol">${fund.symbol}</span>
          <span class="ticker-aum">${fund.aum}</span>
          <span class="ticker-ytd">${fund.ytd}</span>
        </div>
      `,
    )
    .join("");
}

function mountWatchGrid() {
  const target = document.getElementById("watch-grid");
  if (!target) return;

  target.innerHTML = topFunds
    .slice(0, 10)
    .map(
      (fund) => `
        <article class="watch-card">
          <span class="symbol">${fund.symbol}</span>
          <strong>${fund.aum}</strong>
          <span class="ytd">${fund.ytd}</span>
        </article>
      `,
    )
    .join("");
}

function mountRankings() {
  const body = document.getElementById("ranking-body");
  if (!body) return;

  body.innerHTML = rankings
    .map(
      (row) => `
        <tr>
          <td class="rank-cell">${row.rank}</td>
          <td class="fund-cell"><strong>${row.fund}</strong></td>
          <td>${row.country}</td>
          <td>${row.aum}</td>
          <td class="ytd">${row.ytd}</td>
          <td>
            <div class="trend-bar"><span style="width:${row.trend}%"></span></div>
          </td>
        </tr>
      `,
    )
    .join("");
}

function mountFeed() {
  const feed = document.getElementById("feed-list");
  if (!feed) return;

  feed.innerHTML = feedItems
    .map(
      (item) => `
        <article class="feed-item">
          <div class="feed-meta">
            <span class="feed-time">${item.time}</span>
            <span class="feed-tag">${item.tag}</span>
          </div>
          <strong>${item.title}</strong>
        </article>
      `,
    )
    .join("");
}

function mountRegions() {
  const regionList = document.getElementById("region-list");
  if (!regionList) return;

  regionList.innerHTML = regions
    .map(
      (item) => `
        <article class="region-item">
          <span class="region-name">${item.name}</span>
          <div class="value-bar" style="--size:${item.size}%"><span></span></div>
          <span class="region-value">${item.value}</span>
        </article>
      `,
    )
    .join("");
}

function mountAllocations() {
  const allocationList = document.getElementById("allocation-list");
  if (!allocationList) return;

  allocationList.innerHTML = allocations
    .map(
      (item) => `
        <article class="allocation-item">
          <span class="allocation-name">${item.name}</span>
          <div class="value-bar" style="--size:${item.size}%"><span></span></div>
          <span class="allocation-value">${item.value}</span>
        </article>
      `,
    )
    .join("");
}

function mountTransactions() {
  const stream = document.getElementById("stream-list");
  if (!stream) return;

  stream.innerHTML = transactions
    .map(
      (item) => `
        <article class="stream-item">
          <div class="stream-meta">
            <span class="stream-time">${item.time}</span>
            <span class="stream-tag">${item.tag}</span>
          </div>
          <strong>${item.title}</strong>
        </article>
      `,
    )
    .join("");
}

function mountDates() {
  const date = new Date().toISOString().slice(0, 10);
  const asOfDate = document.getElementById("as-of-date");
  if (asOfDate) {
    asOfDate.textContent = date;
  }
}

updateClock();
mountTicker();
mountWatchGrid();
mountRankings();
mountFeed();
mountRegions();
mountAllocations();
mountTransactions();
mountDates();
setInterval(updateClock, 1000);
